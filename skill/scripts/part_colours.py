"""A copy of the model with every blockout part in its own flat colour, for judging the shape part by part.

Each triangle takes the colour of the part it lies nearest to (the same rule texturing uses to tell parts apart), so
a part that is misplaced, swallowed by another or cut away shows up at a glance. Not scored: the judges see only
untextured.glb and textured.glb.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
import parts as PT
from render_preview import ANGLES, render


KELLY = ["F3C300", "875692", "F38400", "A1CAF1", "BE0032", "C2B280", "008856", "E68FAC", "0067A5", "F99379", "604E97",
         "F6A600", "B3446C", "DCD300", "882D17", "8DB600", "654522", "E25822", "2B3D26", "222222"]   # Kelly's contrast set
BODY = "C8C8C8"


def part_colours(parts):
    """The biggest part (the body) plain grey, so the parts on it stand out; the rest from Kelly's colours of maximum
    contrast, in his order (each far from the one before). Past 20 parts the list repeats, lighter."""
    big = int(np.argmax([PT.volume(p) for p in parts]))
    out, k = [], 0
    for i in range(len(parts)):
        if i == big: out.append(np.array([int(BODY[j:j + 2], 16) for j in (0, 2, 4)]) / 255); continue
        c = np.array([int(KELLY[k % 20][j:j + 2], 16) for j in (0, 2, 4)]) / 255
        out.append(c if k < 20 else 0.55 * c + 0.45); k += 1
    return np.array(out)


def split_by_part(V, F, N, parts):
    """Each face's part, and the mesh with vertices split where parts meet, so the colour borders stay crisp."""
    pid = PT.nearest_part(parts, V[F].mean(1)).astype(np.int64)
    key = np.repeat(pid, 3) * len(V) + F.reshape(-1)              # one vertex per (vertex, part) pair
    uniq, inv = np.unique(key, return_inverse=True)
    src = uniq % len(V)
    return V[src], inv.reshape(-1, 3), (N[src] if N is not None else None), uniq // len(V), pid


def key_image(parts, cols, width, sw=18):
    names = [p["name"] for p in parts]
    per_row = max(1, width // 190); rows = -(-len(names) // per_row)
    im = Image.new("RGB", (width, rows * (sw + 6) + 6), "white"); d = ImageDraw.Draw(im)
    for i, (n, c) in enumerate(zip(names, cols)):
        x = 8 + (i % per_row) * 190; y = 6 + (i // per_row) * (sw + 6)
        d.rectangle([x, y, x + sw, y + sw], fill=tuple(int(255 * k) for k in c), outline="black")
        d.text((x + sw + 6, y + 3), n, fill="black")
    return im


def preview_parts(V, F, N, face_cols, parts, cols, out, px=360):
    w = px * len(ANGLES); key = key_image(parts, cols, w)
    sheet = Image.new("RGB", (w, px + 20 + key.height), "white"); d = ImageDraw.Draw(sheet)
    for k, (name, yaw, pitch) in enumerate(ANGLES):
        sheet.paste(render(V, F, face_cols, yaw, pitch, px, N), (px * k, 20)); d.text((px * k + 8, 4), name, fill="black")
    sheet.paste(key, (0, px + 20)); sheet.save(out)


def write_part_model(path, preview_path, V, F, N, parts, shift, write_glb):
    cols = part_colours(parts)
    V2, F2, N2, vpart, pid = split_by_part(V, F, N, parts)
    write_glb(path, V2 + shift, F2, normals=N2, vertex_colours=cols[vpart] ** 2.2, colour=(1, 1, 1, 1))   # glTF: linear
    preview_parts(V, F, N, cols[pid] * 255, parts, cols, preview_path)
    return {p["name"]: "#%02x%02x%02x" % tuple(int(255 * k) for k in c) for p, c in zip(parts, cols)}
