"""Shaded preview of a model from several angles, so the agent (and you) can judge whether it looks like the animal.

usage: python render_preview.py MODEL.glb OUT.png [--px 360]
Painter's algorithm into a triangle-id buffer, then per-pixel texture lookup and smooth Lambert shading.
Camera 0 deg = the scorer's front camera (at -y, looking towards +y); angles orbit around the vertical axis.
"""
import argparse, os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
from glb_io import read_glb

ANGLES = [("front", 0, 5), ("front 3/4", 35, 15), ("side", 90, 5), ("back 3/4", 215, 15), ("from above", 20, 60)]
LIGHT = np.array([-0.4, -0.7, 0.6]) / np.linalg.norm([-0.4, -0.7, 0.6])


def face_colours(F, uv, img):
    if uv is None or img is None: return None
    t = np.asarray(img, np.float32)
    c = uv[F].mean(1)
    px = np.clip((c[:, 0] * t.shape[1]).astype(int), 0, t.shape[1] - 1)
    py = np.clip((c[:, 1] * t.shape[0]).astype(int), 0, t.shape[0] - 1)
    return t[py, px]


def render(V, F, cols, yaw, pitch, px=360, N=None, uv=None, img=None, ss=2):
    """N: vertex normals (as stored in the model) for smooth shading; without them each facet is shaded flat.
    uv, img: texture coordinates and image. With them every pixel looks up its own texture colour, as a glTF viewer
    does, so the preview shows the texture's real detail and seams (cols, one colour per triangle, is a rough
    stand-in that turns every edge in the texture into a staircase of triangles)."""
    a, b = np.radians(yaw), np.radians(pitch)
    Rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, np.cos(b), -np.sin(b)], [0, np.sin(b), np.cos(b)]])
    R = Rz.T @ Rx.T
    P = (V - (V.min(0) + V.max(0)) / 2) @ R                       # x right, y away from camera, z up
    W = px * ss
    span = max(np.ptp(P[:, 0]), np.ptp(P[:, 2])) * 1.1
    sx = W / 2 + P[:, 0] / span * W; sy = W / 2 - P[:, 2] / span * W
    order = np.argsort(-P[F, 1].mean(1))                          # far to near
    ids = Image.new("I", (W, W), 0); d = ImageDraw.Draw(ids)
    for i in order:
        f = F[i]; d.polygon([(sx[f[0]], sy[f[0]]), (sx[f[1]], sy[f[1]]), (sx[f[2]], sy[f[2]])], fill=int(i) + 1)
    idm = np.asarray(ids, np.int64) - 1
    yy, xx = np.nonzero(idm >= 0); t = idm[yy, xx]
    A = np.c_[sx, sy][F[t]]                                       # (n, 3, 2) corners of each pixel's triangle
    p = np.c_[xx + 0.5, yy + 0.5]
    v0, v1, v2 = A[:, 1] - A[:, 0], A[:, 2] - A[:, 0], p - A[:, 0]
    den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
    den = np.where(np.abs(den) < 1e-12, 1e-12, den)
    w1 = (v2[:, 0] * v1[:, 1] - v1[:, 0] * v2[:, 1]) / den
    w2 = (v0[:, 0] * v2[:, 1] - v2[:, 0] * v0[:, 1]) / den
    w = np.clip(np.c_[1 - w1 - w2, w1, w2], 0, 1); w /= np.maximum(w.sum(1, keepdims=True), 1e-12)
    if N is not None:
        n = (N[F[t]] * w[..., None]).sum(1) @ R
    else:
        tri = P[F[t]]; n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    shade = 0.35 + 0.65 * np.abs(n @ LIGHT)
    if uv is not None and img is not None:
        tex = np.asarray(img.convert("RGB"), np.float32)
        q = (uv[F[t]] * w[..., None]).sum(1)
        qx = np.clip((q[:, 0] * tex.shape[1]).astype(int), 0, tex.shape[1] - 1)
        qy = np.clip((q[:, 1] * tex.shape[0]).astype(int), 0, tex.shape[0] - 1)
        base = tex[qy, qx]
    elif cols is not None:
        base = np.asarray(cols, np.float32)[t]
    else:
        base = np.full((len(t), 3), 200.0)
    out = np.empty((W, W, 3), np.float32); out[:] = (225, 228, 235)
    out[yy, xx] = np.clip(base * shade[:, None], 0, 255)
    im = Image.fromarray(out.astype(np.uint8))
    return im.resize((px, px), Image.LANCZOS) if ss > 1 else im


def preview(V, F, uv, img, out, px=360, N=None):
    sheet = Image.new("RGB", (px * len(ANGLES), px + 20), "white"); d = ImageDraw.Draw(sheet)
    for k, (name, yaw, pitch) in enumerate(ANGLES):
        sheet.paste(render(V, F, None, yaw, pitch, px, N, uv, img), (px * k, 20)); d.text((px * k + 8, 4), name, fill="black")
    sheet.save(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("model"); ap.add_argument("out"); ap.add_argument("--px", type=int, default=360)
    a = ap.parse_args()
    V, F, uv, img, N = read_glb(a.model, with_normals=True)
    preview(V, F, uv, img, a.out, a.px, N); print("wrote", a.out)


if __name__ == "__main__":
    main()
