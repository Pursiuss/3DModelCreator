"""Turn a character turnaround sheet (front, side and back figures on a white page) into a refs folder.

usage: python make_refs_from_sheet.py SHEET.jpg OUT_DIR --height 1.5 --front C0 C1 --side C0 C1 --back C0 C1
Each --view gives the column range of that figure on the sheet; the figure is the largest drawing in that range,
so small insets beside it (close-ups, separate parts) are left out, and so are thin pointer lines to notes. The sheet has no top view, so top.png is made
from the front and side outlines (the outline of the shape those two views allow, seen from above). It carries
no information of its own, and its colour is a flat grey: every part should list "top" in ignore_views.
On a sheet the figures may differ in pose (arms raised in one, lowered in another), so their widths disagree;
subject.json gets "scale_by": "height", and each front, side and back figure is scaled by its height alone.
"""
import argparse, json, os
import numpy as np
from PIL import Image
from scipy import ndimage


def figure(rgb, c0, c1, pad=8):
    ink = (255 - rgb).max(2) > 40
    holes = ndimage.binary_fill_holes(ink) & ~ink                 # white enclosed by ink: eyes, highlights, and
    hl, hn = ndimage.label(holes)                                  # the page showing between an arm and the body
    small = np.isin(hl, 1 + np.nonzero(ndimage.sum(holes, hl, range(1, hn + 1)) < 200)[0])
    fg = ink | small                                               # keep only the small ones (eyes)
    fg = ndimage.binary_opening(fg, iterations=2)                  # drop thin pointer lines to the notes and the
    lab, n = ndimage.label(fg)                                     # sheet's grid
    sizes = ndimage.sum(fg, lab, range(1, n + 1))
    centre = np.array([ndimage.center_of_mass(lab == i + 1)[1] for i in range(n)])
    inside = [i for i in range(n) if c0 <= centre[i] < c1]
    k = max(inside, key=lambda i: sizes[i]) + 1
    m = lab == k
    ys, xs = np.nonzero(m)
    r0, r1 = max(ys.min() - pad, 0), min(ys.max() + 1 + pad, m.shape[0])
    q0, q1 = max(xs.min() - pad, 0), min(xs.max() + 1 + pad, m.shape[1])
    rgba = np.dstack([rgb[r0:r1, q0:q1], np.where(m[r0:r1, q0:q1], 255, 0)]).astype(np.uint8)
    return rgba, m[r0:r1, q0:q1]


def bbox(m):
    ys, xs = np.nonzero(m); return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("sheet"); ap.add_argument("out")
    ap.add_argument("--height", type=float, default=1.5)
    ap.add_argument("--side-faces-right", action="store_true", help="the side figure looks to the right: mirror it so "
                    "the nose is on the left, as the skill expects")
    for v in ("front", "side", "back"): ap.add_argument(f"--{v}", type=int, nargs=2, required=True)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    rgb = np.array(Image.open(a.sheet).convert("RGB")).astype(int)
    masks = {}
    for v in ("front", "side", "back"):
        img, masks[v] = figure(rgb, *getattr(a, v))
        if v == "side" and a.side_faces_right: img, masks[v] = img[:, ::-1], masks[v][:, ::-1]
        Image.fromarray(img).save(os.path.join(a.out, f"{v}.png"))
    fb, sb = bbox(masks["front"]), bbox(masks["side"])
    ppm_f = (fb[3] - fb[1]) / a.height; ppm_s = (sb[3] - sb[1]) / a.height
    width = (fb[2] - fb[0]) / ppm_f; length = (sb[2] - sb[0]) / ppm_s
    # top silhouette: (x, y) is inside if some height z is inside both the front outline at x and the side at y
    nz = 600; zs = np.linspace(0, a.height, nz, endpoint=False) + a.height / nz / 2
    def columns(m, b, ppm, n_h):
        hs = np.linspace(-0.5, 0.5, n_h) * (b[2] - b[0]) / ppm
        cols = np.clip(((b[0] + b[2]) / 2 + hs * ppm).astype(int), 0, m.shape[1] - 1)
        rows = np.clip((b[3] - zs * ppm).astype(int), 0, m.shape[0] - 1)
        return m[np.ix_(rows, cols)].T                                     # [h, z]
    ppm_t = 400; nx, ny = int(width * ppm_t), int(length * ppm_t)
    fx = columns(masks["front"], fb, ppm_f, nx)                            # x from -W/2 (image left) to +W/2
    sy = columns(masks["side"], sb, ppm_s, ny)                             # y from nose (-L/2) to tail
    top = (fx.astype(np.uint8) @ sy.T.astype(np.uint8)) > 0                # [x, y]
    top = top[::-1].T                                                      # rows = +y down, cols = image right is -x
    pad = 8; T = np.zeros((ny + 2 * pad, nx + 2 * pad, 4), np.uint8)
    T[pad:-pad, pad:-pad, :3] = 128; T[pad:-pad, pad:-pad, 3] = np.where(top, 255, 0)
    T[..., :3] = np.where(T[..., 3:] > 0, T[..., :3], 255)
    Image.fromarray(T).save(os.path.join(a.out, "top.png"))
    front = Image.open(os.path.join(a.out, "front.png")); bg = Image.new("RGBA", front.size, (255, 255, 255, 255))
    bg.alpha_composite(front); bg.convert("RGB").save(os.path.join(a.out, "final.png"))
    json.dump({"height": a.height, "width": round(width, 3), "length": round(length, 3), "scale_by": "height"},
              open(os.path.join(a.out, "subject.json"), "w"))
    print(f"height {a.height} m, width {width:.3f} m, length {length:.3f} m; wrote front, side, back, top, final, subject")


if __name__ == "__main__":
    main()
