"""Synthetic test animals in the kit's layout: front/back/side/top.png (transparent), final.png, subject.json, masks.

usage: python make_synthetic.py OUT_DIR [names...]
Each animal is a union of simple solids, voxelised and rendered with exact orthographic views in the scorer's
conventions (nose towards -y, as the practice masks have it). The views are perfectly consistent with each other,
unlike drawn or AI-generated references, so these test geometry (thin parts, hollows, odd body plans), not
disagreements between views. final.png is the side view on a plain backdrop, declared in subject.json.
"""
import json, os, sys
import numpy as np
from PIL import Image

BACKDROP = (0.55, 0.70, 0.85)


def ellipsoid(c, r):
    c, r = np.array(c), np.array(r)
    return lambda P: (((P - c) / r) ** 2).sum(-1) <= 1


def capsule(a, b, r):
    a, b = np.array(a, float), np.array(b, float)
    def f(P):
        ab = b - a; t = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1)
        return np.linalg.norm(P - (a + t[..., None] * ab), axis=-1) <= r
    return f


def plate(c, r, thick_axis, thick):
    """Elliptical plate: radii r in the other two axes, thin along thick_axis."""
    c = np.array(c); rr = np.array(r, float); rr[thick_axis] = thick / 2
    return ellipsoid(c, rr)


def clip(f, axis, lo=-1e9, hi=1e9):
    return lambda P: f(P) & (P[..., axis] >= lo) & (P[..., axis] <= hi)


def spots(base, spot, scale, frac=0.35, seed=0):
    from scipy.spatial import cKDTree
    rng = np.random.default_rng(seed); tree = cKDTree(rng.uniform(-60, 60, (60000, 3)))
    def colour(P):
        d, _ = tree.query(P / scale, k=2)
        edge = (d[:, 1] - d[:, 0]) < frac * 0.6          # dark network between cells -> giraffe-like patches
        return np.where(edge[:, None], np.array(base), np.array(spot))
    return colour


def solid(rgb):
    return lambda P: np.tile(np.array(rgb, float), (len(P), 1))


ANIMALS = {
    "turtle": [  # flat dome shell, flipper legs, low and wide
        (clip(ellipsoid((0, 0, 0.035), (0.13, 0.16, 0.10)), 2, lo=0.035), spots((0.25, 0.22, 0.12), (0.45, 0.42, 0.2), 0.03, seed=1)),
        (ellipsoid((0, 0, 0.04), (0.125, 0.155, 0.025)), solid((0.8, 0.72, 0.45))),
        (ellipsoid((0, -0.205, 0.06), (0.035, 0.05, 0.03)), solid((0.45, 0.5, 0.35))),
        (capsule((0, -0.13, 0.05), (0, -0.18, 0.06), 0.025), solid((0.45, 0.5, 0.35))),
        (plate((0.13, -0.08, 0.025), (0.07, 0.035, 0), 2, 0.014), solid((0.45, 0.5, 0.35))),
        (plate((-0.13, -0.08, 0.025), (0.07, 0.035, 0), 2, 0.014), solid((0.45, 0.5, 0.35))),
        (ellipsoid((0.1, 0.11, 0.02), (0.035, 0.03, 0.02)), solid((0.45, 0.5, 0.35))),
        (ellipsoid((-0.1, 0.11, 0.02), (0.035, 0.03, 0.02)), solid((0.45, 0.5, 0.35))),
        (capsule((0, 0.15, 0.03), (0, 0.19, 0.02), 0.01), solid((0.45, 0.5, 0.35)))],
    "giraffe": [  # tall, thin legs, long neck
        (ellipsoid((0, 0, 2.0), (0.35, 0.8, 0.42)), spots((0.45, 0.28, 0.12), (0.88, 0.7, 0.4), 0.12, seed=2)),
        (capsule((0, -0.6, 2.2), (0, -1.0, 4.0), 0.16), spots((0.45, 0.28, 0.12), (0.88, 0.7, 0.4), 0.12, seed=3)),
        (ellipsoid((0, -1.2, 4.1), (0.13, 0.32, 0.15)), solid((0.85, 0.68, 0.4))),
        (capsule((0.06, -1.05, 4.25), (0.06, -1.0, 4.45), 0.03), solid((0.35, 0.22, 0.1))),
        (capsule((-0.06, -1.05, 4.25), (-0.06, -1.0, 4.45), 0.03), solid((0.35, 0.22, 0.1))),
        *[(capsule((sx * 0.2, sy * 0.55, 1.85), (sx * 0.2, sy * 0.55, 0.0), 0.07), solid((0.8, 0.62, 0.36)))
          for sx in (-1, 1) for sy in (-1, 1)],
        (capsule((0, 0.75, 2.2), (0, 0.95, 1.3), 0.03), solid((0.35, 0.22, 0.1)))],
    "bat": [  # thin wing membranes spread sideways, small furry body, ears; lowest point = feet
        (ellipsoid((0, 0, 0.07), (0.025, 0.022, 0.045)), solid((0.35, 0.25, 0.2))),
        (ellipsoid((0, -0.005, 0.125), (0.02, 0.02, 0.02)), solid((0.35, 0.25, 0.2))),
        (capsule((0.01, -0.005, 0.135), (0.02, -0.005, 0.16), 0.006), solid((0.3, 0.2, 0.18))),
        (capsule((-0.01, -0.005, 0.135), (-0.02, -0.005, 0.16), 0.006), solid((0.3, 0.2, 0.18))),
        (plate((0.1, 0.0, 0.08), (0.09, 0, 0.05), 1, 0.004), solid((0.2, 0.15, 0.15))),
        (plate((-0.1, 0.0, 0.08), (0.09, 0, 0.05), 1, 0.004), solid((0.2, 0.15, 0.15))),
        (capsule((0.01, 0, 0.03), (0.012, 0, 0.0), 0.004), solid((0.3, 0.2, 0.18))),
        (capsule((-0.01, 0, 0.03), (-0.012, 0, 0.0), 0.004), solid((0.3, 0.2, 0.18)))],
    "crab": [  # wide flat body, eight thin legs, two claws
        (clip(ellipsoid((0, 0, 0.035), (0.075, 0.055, 0.03)), 2, lo=0.02), solid((0.85, 0.3, 0.15))),
        *[(capsule((sx * 0.06, y, 0.035), (sx * 0.14, y * 1.4, 0.0), 0.006), solid((0.8, 0.35, 0.2)))
          for sx in (-1, 1) for y in (-0.02, 0.0, 0.02, 0.04)],
        (capsule((0.05, -0.04, 0.035), (0.08, -0.09, 0.04), 0.008), solid((0.85, 0.3, 0.15))),
        (capsule((-0.05, -0.04, 0.035), (-0.08, -0.09, 0.04), 0.008), solid((0.85, 0.3, 0.15))),
        (ellipsoid((0.085, -0.11, 0.04), (0.02, 0.03, 0.015)), solid((0.9, 0.4, 0.2))),
        (ellipsoid((-0.085, -0.11, 0.04), (0.02, 0.03, 0.015)), solid((0.9, 0.4, 0.2))),
        (capsule((0.02, -0.05, 0.05), (0.025, -0.06, 0.065), 0.004), solid((0.1, 0.1, 0.1))),
        (capsule((-0.02, -0.05, 0.05), (-0.025, -0.06, 0.065), 0.004), solid((0.1, 0.1, 0.1)))],
    "fish": [  # no legs, thin fins; rests on its belly
        (ellipsoid((0, 0, 0.08), (0.035, 0.16, 0.07)), spots((0.2, 0.35, 0.6), (0.65, 0.75, 0.85), 0.02, seed=5)),
        (plate((0, 0.02, 0.16), (0, 0.07, 0.04), 0, 0.004), solid((0.3, 0.45, 0.7))),
        (plate((0, 0.2, 0.08), (0, 0.05, 0.065), 0, 0.004), solid((0.3, 0.45, 0.7))),
        (plate((0.035, -0.06, 0.04), (0, 0.04, 0.02), 0, 0.003), solid((0.8, 0.5, 0.3))),
        (plate((-0.035, -0.06, 0.04), (0, 0.04, 0.02), 0, 0.003), solid((0.8, 0.5, 0.3)))],
}


def bounds(parts):
    lo = np.array([1e9] * 3); hi = -lo
    probe = np.stack(np.meshgrid(*[np.linspace(-6, 6, 241)] * 3, indexing="ij"), -1).reshape(-1, 3)
    for f, _ in parts:
        m = f(probe)
        if m.any(): lo = np.minimum(lo, probe[m].min(0)); hi = np.maximum(hi, probe[m].max(0))
    pad = (hi - lo).max() * 0.5 + 0.1; lo, hi = lo - pad, hi + pad            # thin parts the probe missed
    ax = [np.linspace(lo[i], hi[i], 160) for i in range(3)]
    P = np.stack(np.meshgrid(*ax, indexing="ij"), -1); occ = np.zeros(P.shape[:3], bool)
    for f, _ in parts: occ |= f(P)
    idx = np.array(np.nonzero(occ)); step = (hi - lo) / 159
    return lo + (idx.min(1) - 2) * step, lo + (idx.max(1) + 2) * step


def voxelise(parts, res=360):
    lo, hi = bounds(parts)
    pad = (hi - lo) * 0.03; lo -= pad; hi += pad
    step = (hi - lo).max() / res
    ax = [np.arange(lo[i], hi[i], step) for i in range(3)]
    P = np.stack(np.meshgrid(*ax, indexing="ij"), -1)
    occ = np.zeros(P.shape[:3], bool); col = np.zeros(P.shape[:3] + (3,), np.float32)
    for f, c in parts:
        m = f(P); occ |= m; col[m] = c(P[m])
    xs, ys, zs = np.nonzero(occ)          # trim to the animal
    sl = (slice(xs.min(), xs.max() + 1), slice(ys.min(), ys.max() + 1), slice(zs.min(), zs.max() + 1))
    return occ[sl], col[sl], step


def render(occ, col, axis, from_high):
    o = np.moveaxis(occ, axis, -1); c = np.moveaxis(col, axis, -2)
    n = o.shape[-1]; has = o.any(-1)
    idx = (n - 1 - np.argmax(o[..., ::-1], -1)) if from_high else np.argmax(o, -1)
    rgb = np.take_along_axis(c, idx[..., None, None], -2)[..., 0, :]
    depth = np.where(has, idx if from_high else n - 1 - idx, 0).astype(float)
    g0, g1 = np.gradient(depth)
    shade = np.clip(0.55 + 0.45 / np.sqrt(1 + 0.15 * (g0 ** 2 + g1 ** 2)) - 0.12 * np.tanh(0.2 * g1), 0.35, 1.0)
    rgb = rgb * shade[..., None]
    return np.concatenate([np.clip(rgb * 255, 0, 255), has[..., None] * 255.0], -1).astype(np.uint8)


def views(occ, col):
    # arrays come out indexed [a, b] over the two remaining axes in order; orient to image (row, col)
    front = render(occ, col, 1, False)          # [x, z] -> image right +x, up +z
    back = render(occ, col, 1, True)            # image right -x
    side = render(occ, col, 0, True)            # [y, z] -> image right +y, up +z
    top = render(occ, col, 2, True)             # [x, y] -> image right -x, down +y
    return {"front": np.transpose(front, (1, 0, 2))[::-1], "back": np.transpose(back, (1, 0, 2))[::-1, ::-1],
            "side": np.transpose(side, (1, 0, 2))[::-1], "top": np.transpose(top, (1, 0, 2))[:, ::-1]}


def main():
    out = sys.argv[1]; names = sys.argv[2:] or list(ANIMALS)
    for name in names:
        occ, col, step = voxelise(ANIMALS[name])
        d = os.path.join(out, name); os.makedirs(d, exist_ok=True)
        V = views(occ, col)
        for v, im in V.items():
            Image.fromarray(np.pad(im, ((12, 12), (12, 12), (0, 0)))).save(os.path.join(d, f"{v}.png"))
            Image.fromarray((np.pad(im[..., 3], 12) > 127).astype(np.uint8) * 255).save(os.path.join(d, f"{v}-mask.png"))
        s = np.pad(V["side"], ((60, 60), (60, 60), (0, 0))).astype(float)
        a = s[..., 3:] / 255; bg = np.array(BACKDROP) * 255
        Image.fromarray((s[..., :3] * a + bg * (1 - a)).astype(np.uint8)).save(os.path.join(d, "final.png"))
        size = {"height": round(occ.shape[2] * step, 3), "length": round(occ.shape[1] * step, 3), "width": round(occ.shape[0] * step, 3)}
        json.dump({**size, "backdrop": list(BACKDROP)}, open(os.path.join(d, "subject.json"), "w"))
        np.save(os.path.join(d, "truth-occupancy.npy"), occ)
        print(name, size, occ.shape)


if __name__ == "__main__":
    main()
