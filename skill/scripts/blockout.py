"""Fit a blockout (parts.json) to the reference outlines, and show how well it matches.

usage: python blockout.py REFS_DIR PARTS.json WORK_DIR [--sweeps 6] [--no-fit]
Writes WORK_DIR/parts.fitted.json, blockout-overlay.png, blockout-parts.png, parts-on-refs.png,
parts-on-refs-detail.png and fit-report.txt.

Fitting nudges every part (position, size, rotation) to make the four outlines of the blockout match the references,
one number at a time, keeping a change only if the match improves. It cannot add a part you left out or remove one
you put in the wrong place: read the overlay and fix parts.json for that.
  overlay colours: green = blockout and reference agree, red = blockout sticks out, blue = reference not covered,
  grey = not counted because a part there lists that view in ignore_views.
"""
import argparse, copy, os, sys
import numpy as np
from PIL import Image, ImageDraw
from skimage import measure
from scipy import ndimage
sys.path.insert(0, os.path.dirname(__file__))
import parts as PT
from views import VIEWS, ViewMap, load_subject, silhouette
from carve import make_grid, sample, capped_res
from render_preview import render

PALETTE = np.array([(230, 90, 70), (70, 140, 230), (90, 190, 90), (240, 190, 50), (170, 100, 210), (60, 200, 200),
                    (240, 130, 190), (150, 150, 60), (120, 80, 50), (100, 100, 110), (250, 150, 90), (60, 90, 160)], float)


class Fitter:
    def __init__(self, refs, res, skip=()):
        size, _ = load_subject(refs); self.skip = tuple(skip)
        self.maps = {v: ViewMap(v, silhouette(refs, v)[0], size) for v in VIEWS}
        self.axes, self.voxel = make_grid(self.maps, size, capped_res(self.maps, size, res, 250_000))
        self.L = {v: sample(self.maps[v], self.axes) for v in VIEWS}
        self.shape = tuple(len(self.axes[a]) for a in "xyz")
        X, Y, Z = np.meshgrid(self.axes["x"], self.axes["y"], self.axes["z"], indexing="ij")
        self.P = np.c_[X.ravel(), Y.ravel(), Z.ravel()]
        self.care = {v: np.ones_like(self.L[v]) & (v not in self.skip) for v in VIEWS}

    def set_ignores(self, parts):
        """Where a part ignores a view (that view draws it wrongly), that view's outline does not count there."""
        for v in VIEWS:
            ign = [p for p in parts if v in p.get("ignore", [])]
            if v in self.skip: continue
            if not ign: self.care[v] = np.ones_like(self.L[v]); continue
            near = self.projections(np.min([PT.sdf_part(p, self.P) for p in ign], 0) - 2 * self.voxel)[v]
            self.care[v] = ~ndimage.binary_dilation(near, iterations=2)

    def projections(self, d):
        o = (d < 0).reshape(self.shape)
        fx = o.any(1)
        return {"front": fx, "back": fx, "side": o.any(0), "top": o.any(2)}

    def ious(self, d):
        pr = self.projections(d); out = {}
        for v, s in pr.items():
            m = self.L[v]; c = self.care[v]
            out[v] = (s & m & c).sum() / max(((s | m) & c).sum(), 1)
        return out

    def score(self, d):
        return float(np.mean([x for v, x in self.ious(d).items() if v not in self.skip]))

    def fit(self, parts, sweeps=6, log=print):
        D = [PT.sdf_part(p, self.P) for p in parts]
        best = self.score(np.min(D, 0))
        log(f"start: mean outline overlap {best:.3f}")
        steps = []
        for p in parts:
            s = PT.scale_of(p)
            steps.append({(k, i): (0.12 * s if kind == "pos" else 0.15 if kind == "size" else 8.0)
                          for k, i, kind in PT.params(p)})
        # Limits around what was written, so a part keeps its role (a beak must not swell to fill the head):
        # position within 25% of the part's size, size between 0.8x and 1.25x, rotation within 25 degrees.
        limits = []
        for p in parts:
            s = PT.scale_of(p); lim = {}
            for k, i, kind in PT.params(p):
                v0 = PT.get(p, k, i)
                if kind == "pos": lim[(k, i)] = (v0 - 0.25 * s - 2 * self.voxel, v0 + 0.25 * s + 2 * self.voxel)
                elif kind == "size": lim[(k, i)] = (0.8 * v0, max(1.25 * v0, v0 + 0.5 * self.voxel))
                else: lim[(k, i)] = (v0 - 25, v0 + 25)
            limits.append(lim)
        order = np.argsort([-PT.scale_of(p) for p in parts])
        for sweep in range(sweeps):
            changed = 0
            for pi in order:
                p = parts[pi]; prm = PT.params(p)
                if not prm: continue
                others = np.min([D[j] for j in range(len(parts)) if j != pi], 0) if len(parts) > 1 else np.full(len(self.P), np.inf)
                for k, i, kind in prm:
                    st = steps[pi][(k, i)]; v0 = PT.get(p, k, i); ok = False
                    for sgn in (1, -1):
                        if kind == "size": v = max(v0 * (1 + sgn * st), 0.4 * self.voxel)
                        else: v = v0 + sgn * st
                        lo, hi = limits[pi][(k, i)]
                        if not lo <= v <= hi: continue
                        q = dict(p); PT.put(q, k, i, v)
                        d = PT.sdf_part(q, self.P); sc = self.score(np.minimum(others, d))
                        if sc > best + 1e-5:
                            parts[pi] = p = q; D[pi] = d; best = sc; ok = True; changed += 1; break
                    if not ok: steps[pi][(k, i)] = st * 0.6
            log(f"sweep {sweep + 1}: overlap {best:.3f} ({changed} changes)")
            if not changed: break
        return parts, best


def orient(a, view):
    """[h, v] grid array -> image array (rows top to bottom, columns left to right as the reference shows it)."""
    if view in ("front", "side"): return a.T[::-1]
    if view == "back": return a.T[::-1, ::-1]
    return a.T[:, ::-1]                                    # top: right = -x, down = +y


def overlay(f, parts, path):
    d = PT.sdf(parts, f.P, smooth=False); pr = f.projections(d); tiles = []
    for v in ("front", "side", "back", "top"):
        s, m = orient(pr[v], v), orient(f.L[v], v)
        img = np.full(s.shape + (3,), 245, np.uint8)
        img[s & m] = (120, 200, 120); img[s & ~m] = (230, 60, 50); img[~s & m] = (60, 110, 230)
        img[~orient(f.care[v], v) & (s | m)] = (170, 170, 170)          # ignored here (ignore_views)
        t = Image.fromarray(img).resize((s.shape[1] * 3, s.shape[0] * 3), Image.NEAREST)
        t.thumbnail((380, 520)); tiles.append((v, t))
    W = sum(t.width for _, t in tiles) + 10 * len(tiles); H = max(t.height for _, t in tiles) + 40
    sheet = Image.new("RGB", (W, H), "white"); dr = ImageDraw.Draw(sheet); x = 0
    ious = f.ious(d)
    for v, t in tiles:
        sheet.paste(t, (x, 22)); dr.text((x + 4, 4), f"{v}  overlap {ious[v]:.2f}", fill="black"); x += t.width + 10
    dr.text((4, H - 16), "green = match   red = blockout sticks out   blue = reference not covered   grey = ignored (ignore_views)", fill="black")
    sheet.save(path)


def blockout_mesh(parts, f, res_scale=1.6, max_points=550_000):
    n = np.prod([len(f.axes[a]) for a in "xyz"]); res_scale = min(res_scale, (max_points / n) ** (1 / 3))
    ax = {a: np.linspace(f.axes[a][0], f.axes[a][-1], int(len(f.axes[a]) * res_scale)) for a in "xyz"}
    X, Y, Z = np.meshgrid(ax["x"], ax["y"], ax["z"], indexing="ij")
    P = np.c_[X.ravel(), Y.ravel(), Z.ravel()]
    vol = PT.sdf(parts, P).reshape(X.shape)
    vol = np.pad(vol, 1, constant_values=1.0)
    verts, faces, _, _ = measure.marching_cubes(vol, 0.0)
    step = np.array([ax[a][1] - ax[a][0] for a in "xyz"])
    V = (verts - 1) * step + np.array([ax[a][0] for a in "xyz"])
    return V, faces[:, ::-1].astype(np.int64)


def parts_preview(parts, f, path):
    V, F = blockout_mesh(parts, f)
    pid = PT.nearest_part(parts, V[F].mean(1)); cols = PALETTE[pid % len(PALETTE)]
    angles = [("front", 0, 5), ("front 3/4", -40, 12), ("side", -90, 5), ("back 3/4", 140, 15), ("from above", 0, 70)]
    px = 300; sheet = Image.new("RGB", (px * len(angles), px + 40 + 16 * ((len(parts) + 3) // 4)), "white")
    d = ImageDraw.Draw(sheet)
    for k, (name, yaw, pitch) in enumerate(angles):
        sheet.paste(render(V, F, cols, yaw, pitch, px), (px * k, 20)); d.text((px * k + 6, 4), name, fill="black")
    for i, p in enumerate(parts):
        x, y = 8 + (i % 4) * 300, px + 26 + 16 * (i // 4)
        d.rectangle([x, y, x + 10, y + 10], fill=tuple(int(c) for c in PALETTE[i % len(PALETTE)]))
        d.text((x + 16, y - 1), p["name"] + (" (x2, mirrored)" if p["mirror"] else ""), fill="black")
    sheet.save(path)


def long_axis(p):
    """Centre and unit direction of a part's longest axis."""
    if p["type"] in PT.TUBES:
        d = p["b"] - p["a"]; return (p["a"] + p["b"]) / 2, d / max(np.linalg.norm(d), 1e-9)
    R = PT.rot(p["rotate"]); k = int(np.argmax(np.abs(p["radii"] if p["type"] == "ellipsoid" else p["half"])))
    return p["center"], R[:, k]


def part_checks(parts, f, build_voxel):
    """Problems a part can have that the overall outline overlap does not show. Returns report lines."""
    out = []
    D = [PT.sdf_part(p, f.P) for p in parts]
    for i, p in enumerate(parts):
        name = p["name"]; thin = PT.thinnest(p)
        sizes = np.abs(p["radii"]) if p["type"] == "ellipsoid" else np.abs(p["half"]) if p["type"] == "box" else None
        longest = float(sizes.max()) if sizes is not None else 0.5 * float(np.linalg.norm(p["b"] - p["a"])) + thin
        if p["type"] == "capsule": thin = 0.5 * float(p["ra"] + p["rb"])        # a cone may end in a point
        if p["type"] == "paddle": thin = float(p["thick"])
        if thin < 1.5 * build_voxel:
            out.append(f"  {name}: thinnest radius {thin * 1000:.1f} mm is under 1.5 build voxels "
                       f"({1.5 * build_voxel * 1000:.1f} mm), so it melts into a blob or a dent; make it at least "
                       f"that thick, or drop it and let the texture show it")
        bigger = [j for j in range(len(parts)) if j != i and PT.scale_of(parts[j]) > 1.5 * PT.scale_of(p)]
        if bigger and 2 * f.voxel <= thin < 0.3 * longest:            # (too thin to judge on this grid)
            others = np.min([D[j] for j in bigger], 0)
            shell = np.nonzero(np.abs(D[i]) < f.voxel)[0]
            if len(shell) >= 40:
                c, ax = long_axis(p)
                t = (f.P[shell] - c) @ ax; edges = np.quantile(t, np.linspace(0, 1, 11))
                sl = np.clip(np.searchsorted(edges, t, side="right") - 1, 0, 9)
                buried = others[shell] < 0
                share = np.array([buried[sl == k].mean() if (sl == k).any() else 0 for k in range(10)])
                along = float((share > 0.2).mean())
                if along >= 0.7:
                    out.append(f"  {name}: lies against a bigger part along {along:.0%} of its length. If it should "
                               f"hang free (flipper, wing, ear, tail, fin), move it outward so only its root end goes "
                               f"in; lying along the body it reads as a stuck-on patch with a groove round it")
        pr = f.projections(D[i])
        for v in ("front", "side", "top"):
            if v in p.get("ignore", []) or v in f.skip: continue
            s = pr[v]; n = s.sum()
            if n < 15: continue
            outside = float((s & ~f.L[v]).sum() / n)
            if outside > 0.2:
                out.append(f"  {name}: {outside:.0%} of it lies outside the {v} outline: too big, or in the wrong place")
    return out or ["  no problems found"]


CAMERA = {"front": (1, False), "back": (1, True), "side": (0, True), "top": (2, True)}   # axis looked along, from high end


def first_hit_labels(parts, axes, axis, high, occ=None):
    """For a camera looking along `axis` (from its high end if `high`): which part it sees first at each cell of the
    other two axes (-1 = nothing). The grid may be coarser along the viewing axis than across it."""
    if occ is None:
        X, Y, Z = np.meshgrid(axes["x"], axes["y"], axes["z"], indexing="ij")
        P = np.c_[X.ravel(), Y.ravel(), Z.ravel()]
        occ = (PT.sdf(parts, P, smooth=False) < 0).reshape(X.shape)
    o = np.moveaxis(occ, axis, -1); n = o.shape[-1]; has = o.any(-1)
    first = (n - 1 - np.argmax(o[..., ::-1], -1)) if high else np.argmax(o, -1)
    other = [a for a in range(3) if a != axis]
    I, J = np.nonzero(has)
    Q = np.zeros((len(I), 3)); Q[:, other[0]] = axes["xyz"[other[0]]][I]; Q[:, other[1]] = axes["xyz"[other[1]]][J]
    Q[:, axis] = axes["xyz"[axis]][first[I, J]]
    lab = -np.ones(has.shape, int); lab[I, J] = PT.nearest_part(parts, Q)
    return lab


def label_tile(parts, refs, vm, v, axes, lab, crop, height, name_px=30):
    """The reference picture, dimmed, cropped to `crop` (pixel box) and scaled to `height`, with the edges of the
    part labels `lab` (on the grid `axes`) drawn on it in each part's colour, and each part named."""
    axis, _ = CAMERA[v]; other = [a for a in range(3) if a != axis]
    im = Image.open(os.path.join(refs, f"{v}.png")).convert("RGBA")
    white = Image.new("RGBA", im.size, (255, 255, 255, 255)); white.alpha_composite(im)
    c0, r0, c1, r1 = crop
    s = height / (r1 - r0); Wt = max(1, int(round((c1 - c0) * s)))
    rgba = np.array(white.convert("RGB").crop(crop).resize((Wt, height), Image.LANCZOS), float)
    rows, cols = np.mgrid[0:height, 0:Wt]
    col = c0 + (cols + 0.5) / s; row = r0 + (rows + 0.5) / s              # picture pixel under each tile pixel
    ha, hs, va, vs = VIEWS[v]; b = vm.box
    val = {ha: (col - (b[0] + b[2]) / 2) / vm.sc * hs,
           va: (b[3] - row) / vm.sc if va == "z" else (row - (b[1] + b[3]) / 2) / vm.sc * vs}
    idx = []
    for a in other:
        ax = axes["xyz"[a]]; step = ax[1] - ax[0]
        idx.append(np.round((val["xyz"[a]] - ax[0]) / step).astype(int))
    ok = (idx[0] >= 0) & (idx[0] < lab.shape[0]) & (idx[1] >= 0) & (idx[1] < lab.shape[1])
    L = -np.ones((height, Wt), int); L[ok] = lab[idx[0][ok], idx[1][ok]]
    edge = np.zeros(L.shape, bool)
    edge[:, 1:] |= L[:, 1:] != L[:, :-1]; edge[1:] |= L[1:] != L[:-1]
    edge = ndimage.binary_dilation(edge, iterations=max(1, height // 400))
    img = 0.45 * rgba + 0.55 * 255
    pid = np.maximum(ndimage.grey_dilation(L, size=3), 0)
    img[edge] = PALETTE[pid[edge] % len(PALETTE)]
    t = Image.fromarray(img.astype(np.uint8)); dr = ImageDraw.Draw(t)
    for i, p in enumerate(parts):                               # name each part at the middle of its biggest patch
        m = L == i
        if m.sum() < name_px: continue
        comp, k = ndimage.label(m); big = 1 + np.argmax(ndimage.sum(m, comp, range(1, k + 1)))
        yy, xx = np.nonzero(comp == big)
        dr.text((xx.mean() - 3 * len(p["name"]), yy.mean() - 5), p["name"],
                fill=tuple(int(c * 0.6) for c in PALETTE[i % len(PALETTE)]))
    return t


def part_box(p):
    """Axis-aligned box around a part (as written, not its mirror copy)."""
    if p["type"] in PT.TUBES:
        r = max(p["ra"], p["rb"]) + (abs(p["bend"]) if p["type"] == "paddle" else 0)
        return (np.minimum(p["a"], p["b"]) - r, np.maximum(p["a"], p["b"]) + r)
    ext = np.abs(PT.rot(p["rotate"])) @ np.abs(p["radii"] if p["type"] == "ellipsoid" else p["half"])
    return p["center"] - ext, p["center"] + ext


def small_clusters(parts, size, rel=0.12, max_n=4):
    """Groups of small parts that touch each other (a foot with its toes and claws; a head with its beak), as
    model-space boxes, largest groups first."""
    big = rel * max(size["width"], size["length"], size["height"])
    idx = [i for i, p in enumerate(parts) if PT.scale_of(p) < big]
    boxes = {i: part_box(parts[i]) for i in idx}; root = {i: i for i in idx}
    def find(i):
        while root[i] != i: i = root[i]
        return i
    for a in idx:
        for b in idx:
            if a < b and np.all(boxes[a][0] - 0.005 <= boxes[b][1]) and np.all(boxes[b][0] - 0.005 <= boxes[a][1]):
                root[find(a)] = find(b)
    groups = {}
    for i in idx: groups.setdefault(find(i), []).append(i)
    out = []
    for members in sorted(groups.values(), key=len, reverse=True)[:max_n]:
        lo = np.min([boxes[i][0] for i in members], 0); hi = np.max([boxes[i][1] for i in members], 0)
        out.append((members, lo, hi))
    return out


def parts_on_refs(parts, refs, size, maps, path, res=200, height=520, detail_path=None):
    """Each reference picture, dimmed, with the outline of the part the camera sees first at every spot drawn on top
    in that part's colour. This is the check the outlines cannot give: where a part lies inside the body's outline
    (a flipper or wing seen from the side, a beak seen from the front, eyes, toes over the belly), only the picture
    shows whether it is the right size and in the right place. The texture is taken from these pictures, so a part
    that misses its drawn shape here gets the wrong colours: a flipper painted twice, a beak smeared onto the face.
    detail_path: a second sheet, zoomed in on each group of small parts (a foot's toes and claws, a beak) and drawn
    on a fine grid, because at the whole-animal scale a claw is two or three grid cells."""
    axes, voxel = make_grid(maps, size, capped_res(maps, size, res, 600_000))
    X, Y, Z = np.meshgrid(axes["x"], axes["y"], axes["z"], indexing="ij")
    occ = (PT.sdf(parts, np.c_[X.ravel(), Y.ravel(), Z.ravel()], smooth=False) < 0).reshape(X.shape)
    del X, Y, Z
    tiles = []
    for v in ("front", "side", "back", "top"):
        vm = maps[v]; axis, high = CAMERA[v]; b = vm.box; H, W = vm.sil.shape
        lab = first_hit_labels(parts, axes, axis, high, occ)
        crop = (max(b[0] - 20, 0), max(b[1] - 20, 0), min(b[2] + 20, W), min(b[3] + 20, H))
        tiles.append((v, label_tile(parts, refs, vm, v, axes, lab, crop, height)))
    Wt = sum(t.width for _, t in tiles) + 10 * len(tiles)
    sheet = Image.new("RGB", (Wt, height + 40), "white"); dr = ImageDraw.Draw(sheet); x = 0
    for v, t in tiles:
        sheet.paste(t, (x, 22)); dr.text((x + 4, 4), v, fill="black"); x += t.width + 10
    dr.text((4, height + 26), "lines = edges of the part the camera sees first, over the reference picture: each part "
             "should cover the shape drawn for it", fill="black")
    sheet.save(path)
    if detail_path is None: return
    rows = []
    for members, lo, hi in small_clusters(parts, size):
        pad = 0.3 * (hi - lo).max(); lo, hi = lo - pad, hi + pad
        fine = (hi - lo).max() / 100
        row = []
        for v in ("front", "side", "back", "top"):
            vm = maps[v]; axis, high = CAMERA[v]; H, W = vm.sil.shape
            ax = {a: np.arange(lo[k], hi[k], fine) for k, a in enumerate("xyz")}
            ax["xyz"[axis]] = axes["xyz"[axis]][::2]               # full depth, so nearer parts still hide it
            lab = first_hit_labels(parts, ax, axis, high)
            corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
            c, r = vm.project(corners)
            crop = (int(max(c.min(), 0)), int(max(r.min(), 0)), int(min(c.max(), W)), int(min(r.max(), H)))
            if crop[2] - crop[0] < 4 or crop[3] - crop[1] < 4: continue
            t = label_tile(parts, refs, vm, v, ax, lab, crop, 300, name_px=60)
            ImageDraw.Draw(t).text((4, 4), v, fill="black"); row.append(t)
        rows.append((", ".join(parts[i]["name"] for i in members), row))
    if not rows: return
    Wd = max(sum(t.width for t in row) + 10 * len(row) for _, row in rows)
    sheet = Image.new("RGB", (Wd, 320 * len(rows) + 24), "white"); dr = ImageDraw.Draw(sheet); y = 0
    for title, row in rows:
        dr.text((4, y + 4), "close-up: " + title + " (one side shown where mirrored)", fill="black"); x = 0
        for t in row: sheet.paste(t, (x, y + 18)); x += t.width + 10
        y += 320
    dr.text((4, y + 6), "each small part's outline should sit on the shape drawn for it: toe on toe, claw on claw",
            fill="black")
    sheet.save(detail_path)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("refs"); ap.add_argument("parts"); ap.add_argument("work")
    ap.add_argument("--sweeps", type=int, default=6); ap.add_argument("--res", type=int, default=120)
    ap.add_argument("--no-fit", action="store_true")
    ap.add_argument("--skip-view", nargs="*", default=[], choices=list(VIEWS),
                    help="views that disagree with the others (measure.py's view check): not fitted to")
    a = ap.parse_args(); os.makedirs(a.work, exist_ok=True)
    parts = PT.load(a.parts); start = copy.deepcopy(parts)
    f = Fitter(a.refs, a.res, a.skip_view); f.set_ignores(parts)
    lines = []
    def log(s): print(s); lines.append(s)
    before = f.ious(PT.sdf(parts, f.P, smooth=False))
    if not a.no_fit: parts, _ = f.fit(parts, a.sweeps, log)
    after = f.ious(PT.sdf(parts, f.P, smooth=False))
    log("outline overlap per view (before -> after): " + ", ".join(
        f"{v} {before[v]:.2f} -> {after[v]:.2f}" + (" (skipped)" if v in f.skip else "") for v in VIEWS))
    for p0, p1 in zip(start, parts):
        moved = []
        for k, i, kind in PT.params(p0):
            v0, v1 = PT.get(p0, k, i), PT.get(p1, k, i)
            if abs(v1 - v0) > 1e-4: moved.append(f"{k}{'' if i is None else '[' + 'xyz'[i] + ']'} {v0:+.3f}->{v1:+.3f}")
        log(f"  {p0['name']}: " + ("; ".join(moved) if moved else "unchanged"))
    _, build_voxel = make_grid(f.maps, load_subject(a.refs)[0], 280)
    log("part checks:"); [log(s) for s in part_checks(parts, f, build_voxel)]
    out = os.path.join(a.work, "parts.fitted.json"); PT.save(parts, out)
    overlay(f, parts, os.path.join(a.work, "blockout-overlay.png"))
    parts_preview(parts, f, os.path.join(a.work, "blockout-parts.png"))
    size, _ = load_subject(a.refs)
    parts_on_refs(parts, a.refs, size, f.maps, os.path.join(a.work, "parts-on-refs.png"),
                  detail_path=os.path.join(a.work, "parts-on-refs-detail.png"))
    open(os.path.join(a.work, "fit-report.txt"), "w").write("\n".join(lines) + "\n")
    print(f"wrote {out}, blockout-overlay.png, blockout-parts.png, parts-on-refs.png, parts-on-refs-detail.png, "
          f"fit-report.txt in {a.work}")


if __name__ == "__main__":
    main()
