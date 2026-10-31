"""Reference views: loading, silhouettes, and the model <-> image mapping used by score_glb.py.

Model coordinates follow the scorer: z-up metres, x = animal's right/left, y = length, feet at z = 0.
  front: looks along +y (image right = +x)    back: looks along -y (image right = -x)
  side : looks along -x (image right = +y)    top : looks down     (image right = -x, image down = +y)
Note: in the practice kit the masks put the nose at -y (it faces the front camera), whatever the header says.
"""
import json, os
import numpy as np
from PIL import Image
from scipy import ndimage

VIEWS = {"front": ("x", +1, "z", -1), "back": ("x", -1, "z", -1), "side": ("y", +1, "z", -1), "top": ("x", -1, "y", +1)}
AX = {"x": 0, "y": 1, "z": 2}


def load_subject(refs):
    s = json.load(open(os.path.join(refs, "subject.json")))
    return s.get("size", s), s


def missing_views(refs):
    """Views with no picture (a turnaround sheet drawn without a top view, say). Every script treats them as skipped:
    they neither fit, trim nor paint the model, and the self-check does not score them."""
    return [v for v in VIEWS if not os.path.exists(os.path.join(refs, f"{v}.png"))]


def stand_in(refs, view, px=400, margin=20):
    """For a view with no picture: a plain box as big as subject.json says, so the view's mapping can still be
    made (and the model's grid sized). Nothing is fitted, trimmed or painted from it."""
    size, _ = load_subject(refs)
    ha, _, va, _ = VIEWS[view]
    real = {"x": size["width"], "y": size["length"], "z": size["height"]}
    sc = px / max(real[ha], real[va]); w, h = int(round(real[ha] * sc)), int(round(real[va] * sc))
    sil = np.zeros((h + 2 * margin, w + 2 * margin), bool); sil[margin:margin + h, margin:margin + w] = True
    return sil


def load_rgba(refs, view):
    return Image.open(os.path.join(refs, f"{view}.png")).convert("RGBA")


def segment_without_alpha(rgb):
    """Fallback when a view has no usable transparency: the background is the colour of the image border."""
    a = rgb.astype(int)
    border = np.r_[a[0], a[-1], a[:, 0], a[:, -1]]
    bg = np.median(border, 0)
    noise = np.percentile(np.abs(border - bg).max(1), 95)      # how much a clean background varies
    fg = np.abs(a - bg).max(2) > float(np.clip(3 * noise + 6, 8, 40))
    fg = ndimage.binary_opening(fg, iterations=2)
    fg = ndimage.binary_fill_holes(fg)
    lab, n = ndimage.label(fg)
    if n > 1:
        sizes = ndimage.sum(fg, lab, range(1, n + 1))
        fg = np.isin(lab, 1 + np.nonzero(sizes >= 0.02 * sizes.max())[0])
    return fg


def silhouette(refs, view, use_masks=False):
    """Boolean mask (True = animal) and a note on how it was obtained."""
    if view in missing_views(refs):
        return stand_in(refs, view), "no picture (skipped)"
    if use_masks:
        return np.array(Image.open(os.path.join(refs, f"{view}-mask.png")).convert("L")) > 127, "mask file"
    im = Image.open(os.path.join(refs, f"{view}.png"))
    if "A" in im.getbands():
        a = np.array(im.getchannel("A"))
        if (a < 128).mean() > 0.02:
            return a > 127, "alpha channel"
    return segment_without_alpha(np.array(im.convert("RGB"))), "background-colour segmentation (no alpha)"


class ViewMap:
    """Same anchoring and scale as score_glb.py: the silhouette's bounding box, scaled by subject.json."""

    def __init__(self, view, sil, size):
        self.view, self.sil = view, sil
        ys, xs = np.nonzero(sil)
        self.box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        ha, _, va, _ = VIEWS[view]
        real = {"x": size["width"], "y": size["length"], "z": size["height"]}
        b = self.box
        self.sc = 0.5 * ((b[2] - b[0]) / real[ha] + (b[3] - b[1]) / real[va])   # pixels per metre
        if size.get("scale_by") == "height" and va == "z":        # a sheet whose views differ in pose: the
            self.sc = (b[3] - b[1]) / real[va]                    # widths disagree, the heights do not
        self.half_h = (b[2] - b[0]) / self.sc / 2
        self.span_v = (b[3] - b[1]) / self.sc
        self.c0 = (b[0] + b[2]) / 2                                # image column of the centre line
        self.r0 = b[3] if va == "z" else (b[1] + b[3]) / 2          # image row of the ground (top view: the middle)
        self.aligned = None
        self.missing = False                                       # no picture: a stand-in box (missing_views)

    def align(self, sc, c0, r0):
        """Map this view with another scale and position than its bounding box gives (see align_back)."""
        b = self.box; self.sc, self.c0, self.r0 = sc, c0, r0
        self.half_h = max(c0 - b[0], b[2] - c0) / sc
        self.span_v = (r0 - b[1]) / sc if VIEWS[self.view][2] == "z" else 2 * max(r0 - b[1], b[3] - r0) / sc

    def project(self, P):
        """Model points (n,3), centred as carve.py builds them, -> image (col, row) floats."""
        ha, hs, va, vs = VIEWS[self.view]
        h = P[:, AX[ha]] * hs; v = P[:, AX[va]] * vs
        return self.c0 + h * self.sc, self.r0 + v * self.sc


def _overlap(f, b, sc, c0, r0, n=(120, 240)):
    """Overlap of the front outline with the mirrored back outline, the back mapped with (sc, c0, r0), compared on a
    grid in metres covering the front view."""
    X, Z = np.meshgrid(np.linspace(-1.3 * f.half_h, 1.3 * f.half_h, n[0]), np.linspace(0, 1.1 * f.span_v, n[1]))
    def inside(sil, col, row):
        c, r = np.floor(col).astype(int), np.floor(row).astype(int)
        ok = (c >= 0) & (c < sil.shape[1]) & (r >= 0) & (r < sil.shape[0])
        out = np.zeros(c.shape, bool); out[ok] = sil[r[ok], c[ok]]; return out
    F = inside(f.sil, f.c0 + X * f.sc, f.r0 - Z * f.sc)
    B = inside(b.sil, c0 - X * sc, r0 - Z * sc)                    # the back camera sees +x on the image left
    return (F & B).sum() / max((F | B).sum(), 1)


AGREE = 0.90             # front and mirrored back outlines overlapping less than this (lined up) differ enough to
                         # shave parts when trimmed to both: another pose, or legs drawn at other widths


def align_back(maps):
    """Line the back view up with the front before judging it. Each view is mapped by its own bounding box, so one
    part sticking out in the back view only (a tail hanging below the paws) shrinks and lifts the whole back view,
    and its outline stops matching the front's although the animal is drawn the same. So the back view's scale and
    position are searched (within 25% and 15-20%) for the best overlap with the mirrored front. If they then agree,
    the back view is mapped that way from then on (fitting, trimming, texturing, rulers); if they still disagree, it
    is drawn in another pose and left as it was (consistency() names it to skip). Sets maps["back"].aligned to
    (overlap before, overlap after, scale factor)."""
    f, b = maps["front"], maps["back"]
    if b.aligned is not None: return
    if f.missing or b.missing: b.aligned = (1.0, 1.0, 1.0); return
    before = _overlap(f, b, b.sc, b.c0, b.r0)
    b.aligned = (before, before, 1.0)
    if before >= AGREE: return
    W, H = b.box[2] - b.box[0], b.box[3] - b.box[1]
    p, best = np.zeros(3), before                                  # log scale, column shift, row shift
    step = np.array([0.04, 0.03 * W, 0.03 * H]); lim = np.array([np.log(1.25), 0.15 * W, 0.2 * H])
    def score(q): return _overlap(f, b, b.sc * np.exp(q[0]), b.c0 + q[1], b.r0 + q[2])
    while step[0] > 0.002:
        moved = False
        for k in range(3):
            for sgn in (1, -1):
                q = p.copy(); q[k] += sgn * step[k]
                if abs(q[k]) > lim[k]: continue
                sc_ = score(q)
                if sc_ > best + 1e-4: p, best, moved = q, sc_, True; break
        if not moved: step = step / 2
    b.aligned = (before, best, float(np.exp(p[0])))
    if best >= AGREE: b.align(b.sc * np.exp(p[0]), b.c0 + p[1], b.r0 + p[2])


def view_maps(refs, size, sils=None):
    """The four views' mappings, with the back view lined up with the front (align_back)."""
    maps = {v: ViewMap(v, sils[v] if sils else silhouette(refs, v)[0], size) for v in VIEWS}
    for v in missing_views(refs): maps[v].missing = True
    align_back(maps)
    return maps


def alignment_note(maps):
    a = maps["back"].aligned
    if a and a[1] >= AGREE and a[0] < AGREE:
        return (f"back view lined up with the front (scaled x{a[2]:.2f} and moved; outline overlap {a[0]:.2f} -> "
                f"{a[1]:.2f}): a part drawn only in the back view, such as a tail hanging below the paws, had thrown "
                f"its framing off; it is used as lined up")
    return None


def consistency(maps):
    """Do the views agree? Returns (warnings, views to skip). Views that disagree about a shared size (after scaling,
    in metres), or a back view drawn in another pose than the front, cut each other away when the model is trimmed
    to all of them, and pull parts to the wrong place when it is fitted to all of them. The top view is blamed when
    it disagrees with the front or the side (they agree with each other on the height, which the scale comes from);
    the back view when, lined up with the front as well as it can be (align_back), it is not its mirror image."""
    w, skip = [], []
    gone = [v for v, m in maps.items() if m.missing]
    for v in gone: w.append(f"no {v} picture: the {v} view is skipped (not fitted, trimmed, painted or scored)")
    skip += gone
    pairs = [("front height", maps["front"].span_v, "side height", maps["side"].span_v, None),
             ("front width", 2 * maps["front"].half_h, "top width", 2 * maps["top"].half_h, "top"),
             ("side length", 2 * maps["side"].half_h, "top length", maps["top"].span_v, "top")]
    pairs = [q for q in pairs if not any(g in q[0] or g in q[2] for g in gone)]
    for a, x, b, y, blame in pairs:
        if abs(x - y) / max(x, y) > 0.08:
            w.append(f"{a} {x:.3f} m vs {b} {y:.3f} m disagree by more than 8% (pose or framing differs)")
            if blame and blame not in skip: skip.append(blame)
    align_back(maps)
    iou = maps["back"].aligned[1]
    if iou < AGREE and "back" not in gone:
        w.append(f"front and mirrored back outlines overlap only {iou:.2f}, even lined up as well as they can be: "
                 f"pose differs between views")
        skip.append("back")
    return w, skip
