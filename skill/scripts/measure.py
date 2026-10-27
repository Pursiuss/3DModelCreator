"""Measurements for writing the blockout: the references with a metric grid, and outline profiles in metres.

usage: python measure.py REFS_DIR WORK_DIR
       python measure.py REFS_DIR WORK_DIR --zoom VIEW H0 V0 H1 V1   (a close-up with a 1 cm grid)
Writes WORK_DIR/ruler-{front,side,back,top}.png, WORK_DIR/palette.png and WORK_DIR/profiles.txt (also printed).
--zoom writes WORK_DIR/zoom-VIEW.png: the box from (H0, V0) to (H1, V1) in model metres (front/back: x, z;
side: y, z; top: x, y), enlarged, with a grid every centimetre (coarser for big boxes), for small parts (beak, toes,
claws, eyes, ears, antlers).
palette.png and the end of profiles.txt list the few colours the animal is painted in, with their "#rrggbb" codes,
for parts' "colour" in parts.json.
Grid labels are model coordinates (see parts.py): x across (front view: right = +x), y along (nose at -y),
z up from the ground. Read a part's x and z off the front ruler, y and z off the side ruler, x and y off the top.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
from views import VIEWS, ViewMap, load_subject, silhouette, load_rgba


def nice_step(span):
    raw = span / 14; mag = 10 ** np.floor(np.log10(raw))
    return float(min((1, 2, 2.5, 5, 10), key=lambda m: abs(m * mag - raw)) * mag)


def to_model(vm, col=None, row=None):
    ha, hs, va, vs = VIEWS[vm.view]; b = vm.box
    h = None if col is None else (np.asarray(col, float) - (b[0] + b[2]) / 2) / vm.sc * hs
    if row is None: return h, None
    v = (b[3] - np.asarray(row, float)) / vm.sc if va == "z" else (np.asarray(row, float) - (b[1] + b[3]) / 2) / vm.sc * vs
    return h, v


def to_pixel(vm, h=None, v=None):
    ha, hs, va, vs = VIEWS[vm.view]; b = vm.box
    col = None if h is None else (b[0] + b[2]) / 2 + h * hs * vm.sc
    row = None if v is None else (b[3] - v * vm.sc if va == "z" else (b[1] + b[3]) / 2 + v * vs * vm.sc)
    return col, row


def ruler(refs, vm, out_path, target=760):
    ha, hs, va, vs = VIEWS[vm.view]; b = vm.box; pad = int(0.08 * max(b[2] - b[0], b[3] - b[1]))
    rgba = load_rgba(refs, vm.view)
    bg = Image.new("RGBA", (rgba.width + 2 * pad, rgba.height + 2 * pad), (236, 238, 242, 255))
    bg.alpha_composite(rgba, (pad, pad))                     # room for the margin beyond the image edge
    c0, r0, c1, r1 = b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad
    s = target / max(c1 - c0, r1 - r0)
    im = bg.crop((c0 + pad, r0 + pad, c1 + pad, r1 + pad)).convert("RGB").resize((round((c1 - c0) * s), round((r1 - r0) * s)), Image.LANCZOS)
    margin = 64; W, H = im.width + margin, im.height + margin + 26
    canvas = Image.new("RGB", (W, H), "white"); canvas.paste(im, (margin, 26)); d = ImageDraw.Draw(canvas)
    hmin, vmax = to_model(vm, c0, r0); hmax, vmin = to_model(vm, c1, r1)
    step = nice_step(max(abs(hmax - hmin), abs(vmax - vmin)))
    X = lambda col: margin + (col - c0) * s
    Y = lambda row: 26 + (row - r0) * s
    lo, hi = sorted((hmin, hmax))
    for h in np.arange(np.ceil(lo / step) * step, hi + 1e-9, step):
        x = X(to_pixel(vm, h=h)[0]); major = abs(h) < 1e-9
        d.line([(x, 26), (x, 26 + im.height)], fill=(220, 40, 40) if major else (90, 120, 200), width=2 if major else 1)
        d.text((x - 14, 26 + im.height + 4), f"{h:+.3f}", fill="black")
    lo, hi = sorted((vmin, vmax))
    for v in np.arange(np.ceil(lo / step) * step, hi + 1e-9, step):
        y = Y(to_pixel(vm, v=v)[1]); major = abs(v) < 1e-9
        d.line([(margin, y), (margin + im.width, y)], fill=(220, 40, 40) if major else (90, 120, 200), width=2 if major else 1)
        d.text((2, y - 6), f"{v:+.3f}", fill="black")
    right = {"front": "+x", "back": "-x", "side": "+y", "top": "-x"}[vm.view]
    down = "y increases downwards" if va == "y" else "z up"
    d.text((4, 4), f"{vm.view}: horizontal = {ha} (right is {right}), vertical = {va} ({down}); grid {step:g} m", fill="black")
    canvas.save(out_path)


def runs(row_mask):
    m = np.r_[False, row_mask, False].astype(int); e = np.diff(m)
    return list(zip(np.nonzero(e == 1)[0], np.nonzero(e == -1)[0]))


def profile_lines(vm, n=20):
    ha, hs, va, vs = VIEWS[vm.view]; b = vm.box; lines = []
    for k in range(n + 1):
        row = int(round(b[1] + (b[3] - b[1] - 1) * k / n))
        _, v = to_model(vm, row=row + 0.5)
        segs = []
        for c0, c1 in runs(vm.sil[row]):
            h0, _ = to_model(vm, col=c0); h1, _ = to_model(vm, col=c1)
            segs.append((min(h0, h1), max(h0, h1)))
        segs = [f"[{a:+.3f}, {b:+.3f}]" for a, b in sorted(segs)]
        lines.append(f"  {va} = {v:+.3f}: {ha} " + " ".join(segs))
    return lines


def zoom(refs, vm, box, path, px=1200):
    """A close-up of one view with a grid labelled in model metres: a line every centimetre, or every 2, 5 or 10 cm
    when the box is too big for that to stay readable (at most about 25 lines across)."""
    h0, v0, h1, v1 = box
    span = max(abs(h1 - h0), abs(v1 - v0))
    step = next((s for s in (0.005, 0.01, 0.02, 0.05, 0.1, 0.2) if span / s <= 25), 0.5)
    c, r = to_pixel(vm, np.array([h0, h1]), np.array([v0, v1]))
    c0, c1 = sorted(c); r0, r1 = sorted(r)
    im = load_rgba(refs, vm.view); bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
    crop = bg.convert("RGB").crop((int(c0), int(r0), int(np.ceil(c1)), int(np.ceil(r1))))
    s = px / max(crop.width, crop.height)
    crop = crop.resize((max(1, int(crop.width * s)), max(1, int(crop.height * s))), Image.NEAREST)
    d = ImageDraw.Draw(crop); ha, _, va, _ = VIEWS[vm.view]
    for hh in np.arange(np.ceil(min(h0, h1) / step) * step, max(h0, h1) + 1e-9, step):
        x = (to_pixel(vm, hh, None)[0] - int(c0)) * s
        d.line([(x, 0), (x, crop.height)], fill=(0, 170, 110)); d.text((x + 2, 2), f"{ha}{hh:+.2f}", fill=(0, 110, 70))
    for vv in np.arange(np.ceil(min(v0, v1) / step) * step, max(v0, v1) + 1e-9, step):
        y = (to_pixel(vm, None, vv)[1] - int(r0)) * s
        d.line([(0, y), (crop.width, y)], fill=(0, 140, 255)); d.text((2, y + 2), f"{va}{vv:+.2f}", fill=(0, 90, 200))
    crop.save(path)


def palette_sheet(refs, path):
    """The few colours the animal is painted in, as swatches with their codes (for parts' "colour")."""
    from texture import palette
    P, _, _ = palette(refs)
    codes = ["#%02x%02x%02x" % tuple(int(v) for v in c) for c in P]
    im = Image.new("RGB", (160 * len(P), 140), "white"); d = ImageDraw.Draw(im)
    for i, (c, code) in enumerate(zip(P, codes)):
        d.rectangle([i * 160 + 10, 10, i * 160 + 150, 110], fill=tuple(int(v) for v in c), outline="black")
        d.text((i * 160 + 12, 116), code, fill="black")
    im.save(path)
    return codes


def main():
    refs, work = sys.argv[1], sys.argv[2]; os.makedirs(work, exist_ok=True)
    size, _ = load_subject(refs)
    if len(sys.argv) > 3 and sys.argv[3] == "--zoom":
        v = sys.argv[4]; box = [float(x) for x in sys.argv[5:9]]
        vm = ViewMap(v, silhouette(refs, v)[0], size); path = os.path.join(work, f"zoom-{v}.png")
        zoom(refs, vm, box, path); print("wrote", path); return
    out = [f"subject (m): width {size['width']} (x), length {size['length']} (y), height {size['height']} (z)",
           "Each line lists the solid stretches of the outline across that level (separate stretches = separate parts,",
           "e.g. two legs). Model coordinates in metres; nose towards -y; front view right = +x.", ""]
    for v in ("front", "side", "top", "back"):
        sil, how = silhouette(refs, v); vm = ViewMap(v, sil, size)
        ruler(refs, vm, os.path.join(work, f"ruler-{v}.png"))
        if v != "back":
            out.append(f"{v} view ({how}), top to bottom:" if v != "top" else f"top view ({how}), nose end (-y) to tail end:")
            pl = profile_lines(vm)
            out += pl if v != "top" else pl
            out.append("")
    from views import consistency
    maps = {v: ViewMap(v, silhouette(refs, v)[0], size) for v in ("front", "side", "back", "top")}
    cw, skip = consistency(maps)
    out[3:3] = (["view check: the four views agree" if not cw else "view check: the views DISAGREE:"] +
                [f"  {x}" for x in cw] +
                ([f"  -> use --skip-view {' '.join(skip)} with blockout.py and build.py, and model the parts those views "
                  f"draw differently from the other views"] if skip else []) + [""])
    codes = palette_sheet(refs, os.path.join(work, "palette.png"))
    out += ["palette (the colours the animal is painted in; see palette.png): " + "  ".join(codes), ""]
    open(os.path.join(work, "profiles.txt"), "w").write("\n".join(out))
    print("\n".join(out)); print(f"rulers: {work}/ruler-*.png")


if __name__ == "__main__":
    main()
