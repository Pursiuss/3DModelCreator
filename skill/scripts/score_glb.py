"""Challenge scoring script (kit v0.2): how far is a .glb model from the reference views?

usage: python score_glb.py MODEL.glb REFS_DIR [--out score.json] [--textured]
  REFS_DIR holds, for each of front / side / back / top, the reference picture <view>.png (a cut-out with a transparent
  background), its mask <view>-mask.png (white = animal), and subject.json (real size in metres:
  {"height": .., "length": .., "width": ..}).

What is scored
  Shape : for each view, IoU (overlap / union) of the model's silhouette with the mask. The shape score is the mean of the
          best TWO of the three views front, side and top. The back view is reported but not scored.
          Gross errors: a view where more than 2% of the animal's picture is wrong by more than the tolerance (3% of the animal's
          longest dimension, about 2 cm on a 70 cm animal) is listed in "gross_errors". It means a missing or misplaced body part
          (a missing head or foot, a nose on the wrong end) that overlap alone would hide. To pass the shape test you need the
          shape score at or above the bar AND an empty "gross_errors" list.
  Colour: only with --textured. The textured model is drawn in each view and compared, cell by cell, with the reference
          picture (background removed on both sides). The colour score is the mean of the best TWO of front, side and top.
  Why best two of three: the reference pictures are AI-made and are not perfectly consistent with each other. Taking the two
  views that agree best with your model keeps one bad reference from deciding the result. The back view is not scored.

Conventions (a .glb is y-up; the script converts to the z-up frame that Blender uses)
  z is up, x is the animal's left-right, y runs along its length. THE NOSE POINTS TOWARDS -y (Blender's "front").
  The feet are at z = 0. All cameras are orthographic (no perspective).
    front: camera at -y, looking along +y, image right = +x, up = +z
    back : camera at +y, looking along -y, image right = -x
    side : camera at +x, looking along -x, image right = +y   (the animal faces to the LEFT of the picture)
    top  : camera above, looking down, image right = -x, image up = -y (the nose is at the top of the picture)
  The scale comes from the real size in subject.json and the mask's bounding box. The model stands on the bottom of the box
  (z = 0 is the feet) and is centred sideways on its own extent, so a model of the wrong size or shape scores low.

It needs only numpy and Pillow."""
import argparse, io, json, os, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

VIEWS = {  # view: (horizontal axis, sign, vertical axis, sign) ; vertical sign -1 = up on the image
    "front": ("x", +1, "z", -1), "back": ("x", -1, "z", -1), "side": ("y", +1, "z", -1), "top": ("x", -1, "y", +1)}
VIEWMAP = VIEWS
SCORED = ("front", "side", "top")          # the back view is reported, not scored
DEPTH = {"front": ("y", -1), "back": ("y", +1), "side": ("x", +1), "top": ("z", +1)}   # axis and sign that point TOWARDS the camera
DELTA_E_MAX = 60.0                          # colour difference (CIE76 Lab) at which a cell scores 0
CELLS_HIGH = 40                             # colour cells over the height of the animal in the picture
GROSS_LIMIT = 0.02                          # in any scored view, more than this share of the reference off by more than the tolerance is a gross error
TOLERANCE = 0.03                            # outline tolerance as a share of the animal's longest dimension (about 2 cm on a 70 cm animal)


def load_glb(path):
    """Triangles of the model as (V, T, UV, image): z-up metres, UV per vertex (or None), base-colour picture (or None)."""
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
    Vs, Ts, Us, base = [], [], [], 0
    for mi, M in items:
        for p in js["meshes"][mi]["primitives"]:
            if p.get("mode", 4) != 4: continue
            P = acc(p["attributes"]["POSITION"]).astype(float); P = (np.c_[P, np.ones(len(P))] @ M.T)[:, :3]
            idx = acc(p["indices"]).reshape(-1) if "indices" in p else np.arange(len(P))
            uv = acc(p["attributes"]["TEXCOORD_0"]).astype(float) if "TEXCOORD_0" in p["attributes"] else np.full((len(P), 2), np.nan)
            Vs.append(P); Ts.append(idx.reshape(-1, 3) + base); Us.append(uv); base += len(P)
    if not Vs: raise SystemExit("no triangles in the model")
    V = np.vstack(Vs); V = np.c_[V[:, 0], -V[:, 2], V[:, 1]]      # glTF y-up -> z-up: (x, y, z) = (x, -z_gltf, y_gltf)
    img = None
    try:
        mat = js["materials"][0]["pbrMetallicRoughness"]["baseColorTexture"]["index"]
        src = js["textures"][mat]["source"]; bv = js["bufferViews"][js["images"][src]["bufferView"]]
        img = Image.open(io.BytesIO(blob[bv.get("byteOffset", 0):bv.get("byteOffset", 0) + bv["byteLength"]])).convert("RGB")
    except Exception: pass
    return V, np.vstack(Ts), np.vstack(Us), img


def pixel_scale(view, box, size):
    ha, _, va, _ = VIEWMAP[view]
    real = {"x": size["width"], "y": size["length"], "z": size["height"]}
    return 0.5 * ((box[2] - box[0]) / real[ha] + (box[3] - box[1]) / real[va])


def project(V, view, box, size):
    ha, hs, va, vs = VIEWMAP[view]
    h = V[:, "xyz".index(ha)] * hs; v = V[:, "xyz".index(va)] * vs
    sc = pixel_scale(view, box, size)
    c = (box[0] + box[2]) / 2 + (h - (h.min() + h.max()) / 2) * sc
    r = box[3] + v * sc if va == "z" else (box[1] + box[3]) / 2 + (v - (v.min() + v.max()) / 2) * sc
    return c, r


def raster(V, T, view, box, size, shape):
    c, r = project(V, view, box, size)
    im = Image.new("L", (shape[1], shape[0]), 0); d = ImageDraw.Draw(im)
    for t in T: d.polygon([(c[i], r[i]) for i in t], fill=255)
    return np.array(im) > 127


def render_colour(V, T, UV, tex, view, box, size, shape):
    """Draw the textured model in a view (far triangles first, one colour per triangle from the texture at its centre)."""
    c, r = project(V, view, box, size)
    ax, sg = DEPTH[view]; near = V[:, "xyz".index(ax)] * sg           # larger = nearer the camera
    order = np.argsort(near[T].mean(1))                               # far first
    tex_a = np.asarray(tex.convert("RGB")); th, tw = tex_a.shape[:2]
    uv = UV[T].mean(1); ok = np.isfinite(uv).all(1)
    px = np.clip((uv[:, 0] % 1.0) * tw, 0, tw - 1).astype(int); py = np.clip((uv[:, 1] % 1.0) * th, 0, th - 1).astype(int)  # glTF v runs down
    col = np.where(ok[:, None], tex_a[py, px], 128)
    im = Image.new("RGB", (shape[1], shape[0]), (0, 0, 0)); d = ImageDraw.Draw(im)
    for k in order:
        t = T[k]; d.polygon([(c[i], r[i]) for i in t], fill=tuple(int(x) for x in col[k]))
    return np.asarray(im)


def to_lab(rgb):
    a = rgb.astype(float) / 255.0
    a = np.where(a > 0.04045, ((a + 0.055) / 1.055) ** 2.4, a / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = a @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def colour_view(model_rgb, model_mask, ref_rgb, ref_mask):
    """Colour agreement 0..1 in one view: cells of the picture where both show the animal, mean Lab difference per cell."""
    ov = model_mask & ref_mask
    ys, xs = np.nonzero(ref_mask)
    if len(ys) == 0 or ov.sum() == 0: return 0.0
    cell = max(4, int(round((ys.max() - ys.min() + 1) / CELLS_HIGH)))
    H, W = ov.shape; h2, w2 = H // cell * cell, W // cell * cell
    def pool(a): return a[:h2, :w2].reshape(h2 // cell, cell, w2 // cell, cell, *a.shape[2:])
    o = pool(ov.astype(float)).sum((1, 3)); good = o >= 0.5 * cell * cell
    if not good.any(): return 0.0
    def mean_lab(rgb):
        lab = to_lab(rgb); s = (pool(lab) * pool(ov.astype(float))[..., None]).sum((1, 3))
        return s / np.maximum(o, 1)[..., None]
    de = np.linalg.norm(mean_lab(model_rgb) - mean_lab(ref_rgb), axis=-1)
    return float(np.clip(1 - de[good] / DELTA_E_MAX, 0, 1).mean())


def dilate(mask, r):
    if r < 1: return mask
    im = Image.fromarray((mask * 255).astype("uint8")).filter(ImageFilter.MaxFilter(2 * int(r) + 1)); return np.array(im) > 127


def off_target(s, m, r):
    """Share of the reference area that is wrong by more than the tolerance r (pixels): the model outside the reference grown by r,
    plus the reference outside the model grown by r. Catches a missing head or foot that IoU hides.
    Works on pictures shrunk to about 160 pixels high, which is fast and precise enough."""
    f = max(1, int(round(m.shape[0] / 160)))
    if f > 1:
        shrink = lambda a: np.array(Image.fromarray((a * 255).astype("uint8")).resize((a.shape[1] // f, a.shape[0] // f), Image.BOX)) > 100
        s, m, r = shrink(s), shrink(m), r / f
    r = max(1, int(round(r)))
    return float(((s & ~dilate(m, r)).sum() + (m & ~dilate(s, r)).sum()) / max(m.sum(), 1))


def best_two(values):
    v = sorted(values, reverse=True)[:2]
    return float(np.mean(v))


def load_refs(refs_dir):
    refs = {}
    for view in VIEWMAP:
        m = np.array(Image.open(os.path.join(refs_dir, f"{view}-mask.png")).convert("L")) > 127
        ys, xs = np.nonzero(m); box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        pic = os.path.join(refs_dir, f"{view}.png"); rgb = None
        if os.path.exists(pic): rgb = np.asarray(Image.open(pic).convert("RGBA"))[:, :, :3]
        refs[view] = (m, box, rgb)
    size = json.load(open(os.path.join(refs_dir, "subject.json")))
    return refs, size.get("size", size)


def score(V, T, UV, tex, refs, size, textured=False):
    res = {"views": {}}; sil = {}
    for view, (m, box, rgb) in refs.items():
        s = sil[view] = raster(V, T, view, box, size, m.shape); i, u = (s & m).sum(), (s | m).sum()
        res["views"][view] = {"iou": round(float(i / max(u, 1)), 3), "reference_missed": round(float((m & ~s).sum() / max(m.sum(), 1)), 3),
                              "model_outside": round(float((s & ~m).sum() / max(s.sum(), 1)), 3), "scored": view in SCORED}
        r = TOLERANCE * max(size.values()) * pixel_scale(view, box, size); res["views"][view]["off_target"] = round(off_target(s, m, r), 4)
    res["shape_score"] = round(best_two([res["views"][v]["iou"] for v in SCORED]), 3)
    res["gross_errors"] = [v for v in SCORED if res["views"][v]["off_target"] > GROSS_LIMIT]
    if textured:
        if tex is None or not np.isfinite(UV).any():
            res["colour_score"] = None; res["note"] = "no base-colour texture with UV coordinates found in the model"
        else:
            for view, (m, box, rgb) in refs.items():
                if rgb is None: continue
                rend = render_colour(V, T, UV, tex, view, box, size, m.shape); s = sil[view]
                res["views"][view]["colour"] = round(colour_view(rend, s, rgb, m), 3)
            res["colour_score"] = round(best_two([res["views"][v]["colour"] for v in SCORED if "colour" in res["views"][v]]), 3)
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("model"); ap.add_argument("refs"); ap.add_argument("--out"); ap.add_argument("--textured", action="store_true")
    a = ap.parse_args()
    refs, size = load_refs(a.refs); V, T, UV, tex = load_glb(a.model)
    res = {"model": os.path.basename(a.model), "kit": "0.2"}; res.update(score(V, T, UV, tex, refs, size, a.textured))
    print(json.dumps(res, indent=1))
    if a.out: json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
