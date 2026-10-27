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

    def project(self, P):
        """Model points (n,3), centred as carve.py builds them, -> image (col, row) floats."""
        ha, hs, va, vs = VIEWS[self.view]
        h = P[:, AX[ha]] * hs; v = P[:, AX[va]] * vs
        b = self.box
        col = (b[0] + b[2]) / 2 + h * self.sc
        row = b[3] + v * self.sc if va == "z" else (b[1] + b[3]) / 2 + v * self.sc
        return col, row


def consistency(maps):
    """Do the views agree? Returns (warnings, views to skip). Views that disagree about a shared size (after scaling,
    in metres), or a back view drawn in another pose than the front, cut each other away when the model is trimmed
    to all of them, and pull parts to the wrong place when it is fitted to all of them. The top view is blamed when
    it disagrees with the front or the side (they agree with each other on the height, which the scale comes from);
    the back view when it is not the mirror image of the front."""
    w, skip = [], []
    pairs = [("front height", maps["front"].span_v, "side height", maps["side"].span_v, None),
             ("front width", 2 * maps["front"].half_h, "top width", 2 * maps["top"].half_h, "top"),
             ("side length", 2 * maps["side"].half_h, "top length", maps["top"].span_v, "top")]
    for a, x, b, y, blame in pairs:
        if abs(x - y) / max(x, y) > 0.08:
            w.append(f"{a} {x:.3f} m vs {b} {y:.3f} m disagree by more than 8% (pose or framing differs)")
            if blame and blame not in skip: skip.append(blame)
    f, b = maps["front"], maps["back"]
    fb = np.array(Image.fromarray(f.sil).crop(f.box).resize((128, 256))) > 0
    bb = np.array(Image.fromarray(b.sil).crop(b.box).resize((128, 256)))[:, ::-1] > 0
    iou = (fb & bb).sum() / max((fb | bb).sum(), 1)
    if iou < 0.85:
        w.append(f"front and mirrored back outlines overlap only {iou:.2f}: pose differs between views")
        skip.append("back")
    return w, skip
