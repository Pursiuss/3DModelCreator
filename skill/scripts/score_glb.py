"""Challenge scoring script (kit v0.1): how well does a .glb model match the reference silhouettes?

usage: python score_glb.py MODEL.glb REFS_DIR [--out score.json] [--textured]
  REFS_DIR holds front-mask.png, side-mask.png, back-mask.png, top-mask.png (white = animal) and subject.json
  (real size of the animal in metres: {"height": .., "length": .., "width": ..}).
  --textured also compares the model's colours with REFS_DIR/final.png (coarse; the experts judge the real look).

Conventions (the same as the course staff's tools): the model is z-up in Blender terms (a .glb is y-up; the script
converts), x is the animal's right/left, y runs along its length (nose towards +y), the feet are at z = 0.
  front: looks along +y   (image right = +x, up = +z)      back: image right = -x
  side : looks along -x   (image right = +y, up = +z)      top : image right = -x, image down = +y
The scale comes from the real size in subject.json and the mask's bounding box. The model stands on the bottom of the box
(z = 0 is the feet) and is centred sideways on its own extent. So a model of the wrong size or the wrong shape scores low.

Score per view = IoU (overlap / union) of the model's silhouette and the mask. The result is the mean of the four.
It needs only numpy and Pillow."""
import argparse, json, os, struct, sys
import numpy as np
from PIL import Image, ImageDraw

VIEWS = {  # view: (horizontal axis, sign, vertical axis, sign) ; vertical sign -1 = up on the image
    "front": ("x", +1, "z", -1), "back": ("x", -1, "z", -1), "side": ("y", +1, "z", -1), "top": ("x", -1, "y", +1)}
RES = 512   # canvas size in pixels (long side)


def load_glb(path):
    """All triangles of the first mesh primitive set, as (V, T) in z-up metres (numpy), plus the base-colour image or None."""
    b = open(path, "rb").read()
    if b[:4] != b"glTF": raise SystemExit("not a binary glTF (.glb) file")
    n = struct.unpack_from("<I", b, 12)[0]; js = json.loads(b[20:20 + n]); off = 20 + n; blob = b""
    while off < len(b):
        ln, tp = struct.unpack_from("<II", b, off)
        if tp == 0x004E4942: blob = b[off + 8:off + 8 + ln]
        off += 8 + ln
    ct = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
    nc = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}

    def acc(i):
        a = js["accessors"][i]; bv = js["bufferViews"][a["bufferView"]]; dt = ct[a["componentType"]]; k = nc[a["type"]]
        o = bv.get("byteOffset", 0) + a.get("byteOffset", 0); st = bv.get("byteStride")
        if st and st != np.dtype(dt).itemsize * k:
            raw = np.frombuffer(blob, np.uint8, count=a["count"] * st, offset=bv.get("byteOffset", 0)).reshape(a["count"], st)
            return np.frombuffer(raw[:, a.get("byteOffset", 0):a.get("byteOffset", 0) + np.dtype(dt).itemsize * k].tobytes(), dt).reshape(-1, k)
        return np.frombuffer(blob, dt, count=a["count"] * k, offset=o).reshape(-1, k)

    def world(node_i, M, out):
        nd = js["nodes"][node_i]; L = np.eye(4)
        if "matrix" in nd: L = np.array(nd["matrix"]).reshape(4, 4).T
        else:
            T = np.eye(4); T[:3, 3] = nd.get("translation", [0, 0, 0])
            x, y, z, w = nd.get("rotation", [0, 0, 0, 1])
            R = np.eye(4); R[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                                        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                                        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
            S = np.diag(list(nd.get("scale", [1, 1, 1])) + [1]); L = T @ R @ S
        M = M @ L
        if "mesh" in nd: out.append((nd["mesh"], M))
        for c in nd.get("children", []): world(c, M, out)

    items = []
    for r in js["scenes"][js.get("scene", 0)]["nodes"]: world(r, np.eye(4), items)
    Vs, Ts, base = [], [], 0
    for mi, M in items:
        for p in js["meshes"][mi]["primitives"]:
            if p.get("mode", 4) != 4: continue
            P = acc(p["attributes"]["POSITION"]).astype(float); P = (np.c_[P, np.ones(len(P))] @ M.T)[:, :3]
            idx = acc(p["indices"]).reshape(-1) if "indices" in p else np.arange(len(P))
            Vs.append(P); Ts.append(idx.reshape(-1, 3) + base); base += len(P)
    if not Vs: raise SystemExit("no triangles in the model")
    V = np.vstack(Vs); V = np.c_[V[:, 0], -V[:, 2], V[:, 1]]      # glTF y-up -> z-up: (x, y, z) = (x, -z_gltf, y_gltf)
    img = None
    try:
        mat = js["materials"][0]["pbrMetallicRoughness"]["baseColorTexture"]["index"]
        src = js["textures"][mat]["source"]; bv = js["bufferViews"][js["images"][src]["bufferView"]]
        import io; img = Image.open(io.BytesIO(blob[bv.get("byteOffset", 0):bv.get("byteOffset", 0) + bv["byteLength"]])).convert("RGB")
    except Exception: pass
    return V, np.vstack(Ts), img


VIEWMAP = VIEWS


def pixel_scale(view, box, size):
    ha, _, va, _ = VIEWMAP[view]
    real = {"x": size["width"], "y": size["length"], "z": size["height"]}
    return 0.5 * ((box[2] - box[0]) / real[ha] + (box[3] - box[1]) / real[va])


def raster(V, T, view, mask_box, size, shape):
    ha, hs, va, vs = VIEWMAP[view]
    h = V[:, "xyz".index(ha)] * hs; v = V[:, "xyz".index(va)] * vs
    sc = pixel_scale(view, mask_box, size)
    c = (mask_box[0] + mask_box[2]) / 2 + (h - (h.min() + h.max()) / 2) * sc
    r = mask_box[3] + v * sc if va == "z" else (mask_box[1] + mask_box[3]) / 2 + (v - (v.min() + v.max()) / 2) * sc
    im = Image.new("L", (shape[1], shape[0]), 0); d = ImageDraw.Draw(im)
    for t in T: d.polygon([(c[i], r[i]) for i in t], fill=255)
    return np.array(im) > 127


def colour_match(img, final, backdrop=None):
    """Coarse colour similarity (0..1): histogram intersection in 6 levels per channel. Ignored pixels: near-white, near-black,
    and (in the final image) the backdrop colour from subject.json, if it has one."""
    def hist(im, bd=None):
        a = np.array(im.convert("RGB").resize((256, 256))).reshape(-1, 3).astype(int)
        keep = ~((a > 240).all(1) | (a < 12).all(1))
        if bd is not None: keep &= np.abs(a - np.array(bd) * 255).max(1) > 60
        a = a[keep] // 43
        h = np.bincount(a[:, 0] * 36 + a[:, 1] * 6 + a[:, 2], minlength=216).astype(float)
        return h / max(h.sum(), 1)
    return float(np.minimum(hist(img), hist(final, backdrop)).sum())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("model"); ap.add_argument("refs"); ap.add_argument("--out"); ap.add_argument("--textured", action="store_true")
    a = ap.parse_args()
    size = json.load(open(os.path.join(a.refs, "subject.json"))); subj = size; size = size.get("size", size); V, T, img = load_glb(a.model)
    res = {"model": os.path.basename(a.model), "views": {}}
    for view in VIEWMAP:
        m = np.array(Image.open(os.path.join(a.refs, f"{view}-mask.png")).convert("L")) > 127
        ys, xs = np.nonzero(m); box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        s = raster(V, T, view, box, size, m.shape); i, u = (s & m).sum(), (s | m).sum()
        res["views"][view] = {"iou": round(float(i / max(u, 1)), 3), "reference_missed": round(float((m & ~s).sum() / max(m.sum(), 1)), 3),
                              "model_outside": round(float((s & ~m).sum() / max(s.sum(), 1)), 3)}
    res["shape_score"] = round(float(np.mean([v["iou"] for v in res["views"].values()])), 3)
    if a.textured:
        fin = os.path.join(a.refs, "final.png")
        if img is None: res["colour_match"] = None; res["note"] = "no base-colour texture found in the model"
        elif not os.path.exists(fin): res["colour_match"] = None; res["note"] = "no final.png in the references"
        else: res["colour_match"] = round(colour_match(img, Image.open(fin), subj.get("backdrop")), 3)
    print(json.dumps(res, indent=1))
    if a.out: json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
