"""Minimal binary glTF (.glb) writer.

Input geometry uses the scorer's convention: z-up metres, x = animal's right/left, y = length, feet at z = 0.
glTF is y-up, so on write (x, y, z) -> (x, z, -y), the inverse of score_glb.py's conversion.
"""
import io, json, struct
import numpy as np


def _pad4(b, fill=b"\x00"):
    return b + fill * ((4 - len(b) % 4) % 4)


def vertex_normals(V, F):
    n = np.zeros_like(V)
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    for k in range(3):
        np.add.at(n, F[:, k], fn)
    l = np.linalg.norm(n, axis=1, keepdims=True)
    return n / np.maximum(l, 1e-12)


def read_glb(path, with_normals=False, with_colours=False):
    """Reader for the files write_glb makes (one primitive, no node transforms): V z-up, F, uv or None, PIL image or None
    (and the z-up vertex normals, if with_normals; and the vertex colours, if with_colours)."""
    from PIL import Image
    b = open(path, "rb").read()
    n = struct.unpack_from("<I", b, 12)[0]; js = json.loads(b[20:20 + n]); blob = b[20 + n + 8:]
    ct = {5125: np.uint32, 5126: np.float32}; nc = {"SCALAR": 1, "VEC2": 2, "VEC3": 3}

    def acc(i):
        a = js["accessors"][i]; bv = js["bufferViews"][a["bufferView"]]
        return np.frombuffer(blob, ct[a["componentType"]], a["count"] * nc[a["type"]], bv.get("byteOffset", 0)).reshape(a["count"], -1)

    p = js["meshes"][0]["primitives"][0]
    Vg = acc(p["attributes"]["POSITION"]).astype(float); V = np.c_[Vg[:, 0], -Vg[:, 2], Vg[:, 1]]
    F = acc(p["indices"]).reshape(-1, 3).astype(np.int64)
    uv = acc(p["attributes"]["TEXCOORD_0"]) if "TEXCOORD_0" in p["attributes"] else None
    img = None
    if js.get("images"):
        bv = js["bufferViews"][js["images"][0]["bufferView"]]
        img = Image.open(io.BytesIO(blob[bv["byteOffset"]:bv["byteOffset"] + bv["byteLength"]])).convert("RGB")
    if with_normals:
        Ng = acc(p["attributes"]["NORMAL"]).astype(float)
        out = (V, F, uv, img, np.c_[Ng[:, 0], -Ng[:, 2], Ng[:, 1]])
    else:
        out = (V, F, uv, img)
    if with_colours:                                                 # sRGB 0-255, or None
        out += ((acc(p["attributes"]["COLOR_0"]) ** (1 / 2.2) * 255 if "COLOR_0" in p["attributes"] else None),)
    return out


def write_glb(path, V, F, uv=None, texture=None, colour=(0.8, 0.8, 0.8, 1.0), normals=None, vertex_colours=None):
    """V: (n,3) z-up metres, F: (m,3) triangle indices, uv: (n,2) or None, texture: PIL image or None,
    normals: (n,3) z-up vertex normals or None (computed). Pass normals when vertices are split along texture
    seams, so the seams don't show up as creases in the shading. vertex_colours: (n,3) linear RGB 0-1, or None."""
    V = np.asarray(V, float); F = np.asarray(F, np.uint32)
    Vg = np.c_[V[:, 0], V[:, 2], -V[:, 1]].astype(np.float32)
    if normals is not None:
        Nz = np.asarray(normals, float); Ng = np.c_[Nz[:, 0], Nz[:, 2], -Nz[:, 1]].astype(np.float32)
    else:
        Ng = vertex_normals(Vg.astype(float), F.astype(np.int64)).astype(np.float32)

    blob, views, accessors = b"", [], []

    def add(data, target=None):
        nonlocal blob
        off = len(blob); blob = _pad4(blob + data)
        bv = {"buffer": 0, "byteOffset": off, "byteLength": len(data)}
        if target: bv["target"] = target
        views.append(bv); return len(views) - 1

    def add_acc(arr, ctype, typ, target, minmax=False):
        a = {"bufferView": add(arr.tobytes(), target), "componentType": ctype, "count": len(arr), "type": typ}
        if minmax: a["min"] = arr.min(0).tolist(); a["max"] = arr.max(0).tolist()
        accessors.append(a); return len(accessors) - 1

    attrs = {"POSITION": add_acc(Vg, 5126, "VEC3", 34962, True), "NORMAL": add_acc(Ng, 5126, "VEC3", 34962)}
    mat = {"pbrMetallicRoughness": {"baseColorFactor": list(colour), "metallicFactor": 0.0, "roughnessFactor": 0.9},
           "doubleSided": True}
    gltf = {"asset": {"version": "2.0", "generator": "penguin-challenge skill"}}
    if vertex_colours is not None:
        attrs["COLOR_0"] = add_acc(np.asarray(vertex_colours, np.float32), 5126, "VEC3", 34962)
    if uv is not None and texture is not None:
        attrs["TEXCOORD_0"] = add_acc(np.asarray(uv, np.float32), 5126, "VEC2", 34962)
        png = io.BytesIO(); texture.convert("RGB").save(png, "PNG")
        gltf["images"] = [{"bufferView": add(png.getvalue()), "mimeType": "image/png"}]
        gltf["samplers"] = [{"magFilter": 9729, "minFilter": 9729}]
        gltf["textures"] = [{"source": 0, "sampler": 0}]
        mat["pbrMetallicRoughness"]["baseColorTexture"] = {"index": 0}
        mat["pbrMetallicRoughness"]["baseColorFactor"] = [1, 1, 1, 1]
    ind = add_acc(F.reshape(-1), 5125, "SCALAR", 34963)

    gltf.update({"scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"mesh": 0, "name": "animal"}],
                 "meshes": [{"primitives": [{"attributes": attrs, "indices": ind, "material": 0}]}],
                 "materials": [mat], "accessors": accessors, "bufferViews": views,
                 "buffers": [{"byteLength": len(blob)}]})
    js = _pad4(json.dumps(gltf, separators=(",", ":")).encode(), b" ")
    total = 12 + 8 + len(js) + 8 + len(blob)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(js), 0x4E4F534A)); f.write(js)
        f.write(struct.pack("<II", len(blob), 0x004E4942)); f.write(blob)
