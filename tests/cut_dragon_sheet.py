"""Cut the dragon turnaround sheet (grid background, labels, dimension lines) into a refs folder.

usage: python tests/cut_dragon_sheet.py references/sheets/dragon-sheet.webp references/dragon
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

# view: (col0, row0, col1, row1) on the 1024x559 sheet; each box holds one figure plus labels and lines
BOXES = {"top": (0, 30, 512, 430), "side": (512, 30, 1024, 280), "front": (512, 300, 768, 559), "back": (768, 300, 1024, 559)}
HEIGHT = 1.1          # sheet label H: 1.1 m (front, side and back agree on it)


def figure(rgb, box):
    c0, r0, c1, r1 = box
    a = rgb[r0:r1, c0:c1].astype(int)
    lum = a.mean(2); chroma = a.max(2) - a.min(2)
    ink = (lum < 165) | (chroma > 28)                   # the dragon: dark outlines or coloured; the page: light grey
    core = ndimage.binary_opening(ink, iterations=1)    # drops 1-2 px grid, divider and dimension lines
    lab, n = ndimage.label(core)
    k = 1 + int(np.argmax(ndimage.sum(core, lab, range(1, n + 1))))
    m = lab == k                                        # the biggest piece: the figure (labels and lines are apart)
    edge = ink.copy()                                   # rows and columns a sheet divider runs along (inked across
    edge[ink.mean(1) > 0.5] = False; edge[:, ink.mean(0) > 0.5] = False   # most of the box) get nothing back
    m = (edge & ndimage.binary_dilation(m, iterations=2)) | m   # give back the fine edges the opening shaved (claw tips)
    lab, n = ndimage.label(m)                           # ...but nothing that only touches it (a line end)
    m = lab == 1 + int(np.argmax(ndimage.sum(m, lab, range(1, n + 1))))
    holes = ndimage.binary_fill_holes(m) & ~m           # page showing through: keep the big gaps (between wing and
    hl, hn = ndimage.label(holes)                       # body, between the legs), fill specks and highlights
    small = np.isin(hl, 1 + np.nonzero(ndimage.sum(holes, hl, range(1, hn + 1)) < 30)[0])
    m = m | small
    ys, xs = np.nonzero(m); pad = 8
    q0, q1, p0, p1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    out = np.zeros((p1 - p0 + 2 * pad, q1 - q0 + 2 * pad, 4), np.uint8)
    out[pad:-pad, pad:-pad, :3] = a[p0:p1, q0:q1]
    out[pad:-pad, pad:-pad, 3] = np.where(m[p0:p1, q0:q1], 255, 0)
    return out, (q1 - q0, p1 - p0)


def main():
    sheet, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
    rgb = np.array(Image.open(sheet).convert("RGB"))
    size = {}
    for v, box in BOXES.items():
        img, size[v] = figure(rgb, box)
        Image.fromarray(img).save(os.path.join(out, f"{v}.png"))
        print(f"{v}: {size[v][0]} x {size[v][1]} px")
    ppm_f = size["front"][1] / HEIGHT; ppm_s = size["side"][1] / HEIGHT
    width, length = size["front"][0] / ppm_f, size["side"][0] / ppm_s
    side = Image.open(os.path.join(out, "side.png")); bg = Image.new("RGBA", side.size, (255, 255, 255, 255))
    bg.alpha_composite(side); bg.convert("RGB").save(os.path.join(out, "final.png"))
    json.dump({"height": HEIGHT, "length": round(length, 3), "width": round(width, 3), "scale_by": "height"},
              open(os.path.join(out, "subject.json"), "w"))
    t = size["top"]; print(f"subject: height {HEIGHT}, length {length:.3f}, width {width:.3f} (front and side figures)")
    print(f"top figure: wingspan/length = {t[0] / t[1]:.2f} -> wingspan {t[0] / t[1] * length:.2f} m at that length")


if __name__ == "__main__":
    main()

