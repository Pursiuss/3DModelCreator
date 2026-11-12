"""Texture by projection: every triangle takes its colours from one reference view.

Cameras: front (at -y), back (at +y), side (at +x), mirrored side (at -x, reusing side.png: animals are close to
left/right symmetric, and an orthographic projection along x maps both flanks onto the same image), top (at +z).

Choosing the view for a triangle:
1. candidates: views that see all its corners (depth maps of the voxel model) and face it at a usable angle;
2. consensus: the median colour of the candidates. A view whose colour disagrees with the others there is showing
   something that is not at that spot (an eye painted onto the crown by the top view, belly white on a flipper edge),
   so the choice weighs facing angle against distance from the consensus;
   With a blockout, two more rules: a part never takes colour from a view listed in its ignore_views, and a view is
   trusted less where, as that view sees it, the spot lies right next to a different part (the reference may show
   that other part there: black flipper on a white chest, red beak on the face);
3. patches and seams: views are chosen for the whole surface at once (choose_views), so they form large patches
   with their borders where neighbouring views agree in colour; specks, streaks and saw-tooth borders disappear;
4. small mirrored parts (a foot with its toes and claws, an ear) take their colours from at most two views, so
   they are not stitched together from four differently shaded drawings;
5. triangles no view sees well (soles, undersides, gaps) take the colour of their seen neighbours on the same part,
   as flat swatches of that part's own main colours. Nothing is smeared on from a view that cannot see the spot.
The texture atlas is the four reference images cropped to the animal, side by side, plus a strip of swatches.
"""
import os, warnings
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
from views import load_rgba

CAMS = {  # camera: (image, direction towards the camera, grid axis looked along, camera at the high end of that axis)
    "front": ("front", (0, -1, 0), 1, False), "back": ("back", (0, 1, 0), 1, True),
    "side": ("side", (1, 0, 0), 0, True), "side_mirror": ("side", (-1, 0, 0), 0, False), "top": ("top", (0, 0, 1), 2, True)}
MIN_FACING = 0.35     # cos of the steepest usable viewing angle (about 70 degrees). Steeper, a picture is
                      # stretched across the surface (line art becomes stripes): better to fill the spot
                      # with the part's own colour
DISAGREE = 0.25       # weight of colour disagreement against facing angle: a tie-breaker only. A small feature
                      # (an eye) is seen properly by one view only, and a stronger vote would paint it out.
EDGE = 1.0            # weight against a view where, as that view sees it, the spot is right next to another part
GRAZE = 1.0           # weight against a view that sees the spot at a grazing angle (facing below 0.5, about 60 deg):
                      # there a picture shows whatever lies just past the model's edge (white belly beside a black
                      # back), so it should win only where no view sees the spot squarely
SWATCH = 32
UNDERSIDE = 0.5       # a surface facing further down than this (-z component of its normal, about 30 degrees below
                      # level) takes no colour from any picture: drawings show shadow there


def first_hit(occ, axis, high):
    """Index (along the viewing axis) of the first occupied voxel the camera meets, per cell of the other two axes."""
    o = np.moveaxis(occ, axis, -1); n = o.shape[-1]
    has = o.any(-1)
    if high:
        first = n - 1 - np.argmax(o[..., ::-1], -1); first = np.where(has, first, -1)
    else:
        first = np.argmax(o, -1); first = np.where(has, first, n)
    return first, has


def depth_ok(V, occ, origin, voxel, axis, high, tol):
    """Is each vertex at (or within tol voxels of) the first surface the camera meets?"""
    idx = np.clip(np.round((V - origin) / voxel).astype(int), 0, np.array(occ.shape) - 1)
    first, _ = first_hit(occ, axis, high)
    other = [a for a in range(3) if a != axis]
    f = first[idx[:, other[0]], idx[:, other[1]]]
    d = idx[:, axis]
    return d >= f - tol if high else d <= f + tol


def near_other_part(parts, occ, origin, voxel, axis, high, pid_face, cen, margin):
    """0..1 per triangle: how close, as this camera sees it, the triangle lies to where a different part is in front.
    Near such an edge the reference image may show the other part (the model is only approximately where the animal
    is), so colours from this camera are less trustworthy there: belly white on a flipper, beak red on the face."""
    import parts as PT
    first, has = first_hit(occ, axis, high)
    other = [a for a in range(3) if a != axis]
    I, J = np.nonzero(has)
    P = np.zeros((len(I), 3)); P[:, other[0]] = I; P[:, other[1]] = J; P[:, axis] = first[I, J]
    ids = -np.ones(has.shape, np.int32); ids[I, J] = PT.nearest_part(parts, origin + P * voxel)
    ci = np.clip(np.round((cen - origin) / voxel).astype(int), 0, np.array(occ.shape) - 1)
    out = np.zeros(len(cen))
    for p in np.unique(pid_face):
        dist = ndimage.distance_transform_edt(~((ids >= 0) & (ids != p)))
        sel = pid_face == p
        d = dist[ci[sel, other[0]], ci[sel, other[1]]]
        out[sel] = np.clip(1 - d / margin, 0, 1)
    return out


def find_features(rgb, sil, max_n=16):
    """Small round high-contrast spots (eyes, nostrils, claws, spots) in a reference image: peaks of the scale-
    normalised determinant of the Hessian of brightness, which responds to blobs but not to long edges such as the
    border of a white belly. Returns (row, col, radius px, strength) per feature; a feature seen at a slant is
    squashed and comes out weaker."""
    ys, xs = np.nonzero(sil)
    extent = max(np.ptp(ys), np.ptp(xs)) + 1
    L = rgb.astype(float) @ [0.299, 0.587, 0.114]
    found = []
    for rel in (0.006, 0.01):
        s = max(1.5, rel * extent)
        hxx = ndimage.gaussian_filter(L, s, order=(0, 2)); hyy = ndimage.gaussian_filter(L, s, order=(2, 0))
        hxy = ndimage.gaussian_filter(L, s, order=(1, 1))
        doh = s ** 4 * (hxx * hyy - hxy ** 2)
        inside = ndimage.binary_erosion(sil, iterations=max(1, int(2 * s)))
        if not inside.any(): continue
        resp = np.where(inside, doh, 0)
        thr = max(150.0, np.percentile(resp[inside], 99.9))
        peak = (resp == ndimage.maximum_filter(resp, size=int(6 * s) | 1)) & (resp > thr)
        for r, c in zip(*np.nonzero(peak)):
            found.append((resp[r, c], r, c, 2.0 * s))
    found.sort(key=lambda t: -t[0])
    out = []
    for st, r, c, rad in found:                                  # drop the same spot found at both scales
        if all((r - r2) ** 2 + (c - c2) ** 2 > max(rad, r3) ** 2 for r2, c2, r3, _ in out): out.append((r, c, rad, st))
    return out[:max_n]


def paddle_shadow(parts, pid_face, cen, n, cand, size, rel=0.02):
    """A paddle (flipper, wing, fin) is drawn standing a little off the body, with what lies between them (its inner
    face, the flank under it) drawn in the gap. The model's paddle never sits exactly where it is drawn, so those
    gap colours land on the body next to it, or on the paddle's edge: white slivers on a black flank. So the body
    within about 2% of the animal's size of a paddle takes no colour from the pictures that look along the paddle
    (front, back and top for a flipper), which draw that gap; the picture facing the paddle (the side) draws its
    edge there as it is, so it still paints that strip, or the flipper's white trailing edge turns into a flat
    blob. The paddle's own inner face (the side towards the body) takes no colour from any picture; only for a
    paddle that faces sideways (a flipper): one that faces forward or back (an ear) has no face towards the body,
    and the back picture draws its back as it is. What no picture paints is flood-filled from the colour regions
    around it. Not around the paddle's root: the shoulder it grows out of is drawn as it is."""
    import parts as PT
    reach = rel * max(size["width"], size["length"], size["height"])
    for i, p in enumerate(parts):
        if p["type"] != "paddle": continue
        for inst in PT.instances(p):
            d = PT.sdf_part(dict(inst, mirror=False), cen)
            away = np.linalg.norm(cen - inst["a"], axis=1) > float(p["ra"]) + 2 * reach   # (shoulder drawn as is)
            strip = (pid_face != i) & (d < reach) & away
            fn = PT.paddle_frame(inst)[2]
            for k, (_, dv, _, _) in enumerate(CAMS.values()):
                if abs(fn @ np.array(dv, float)) < 0.5: cand[strip, k] = False
        mine = np.nonzero(pid_face == i)[0]
        for inst in PT.instances(p):
            fn = PT.paddle_frame(inst)[2]
            if abs(fn[0]) < 0.5: continue                                 # faces forward or back: no inner face
            out = fn if fn[0] * inst["a"][0] >= 0 else -fn               # face normal pointing away from the body
            side = (cen[mine, 0] * inst["a"][0]) > 0                      # this instance's side of the animal
            cand[mine[side & ((n[mine] @ out) < -0.3)]] = False


def behind_paddles(parts, pid_face, cen, cand, k, d, voxel):
    """A flipper or wing stands a centimetre or two off the body, closer than the depth check's tolerance (a few
    voxels), so the camera facing it counted the body right behind it as seen, and painted the flipper's drawn
    colours a second time on the body there: from an angle, a black flipper shape on the white body beside the
    real one. Here each spot of another part is followed towards the camera; if it passes through a paddle, this
    camera does not see it."""
    import parts as PT
    for i, p in enumerate(parts):
        if p["type"] != "paddle": continue
        lo, hi = PT.bounds(p); ax = int(np.argmax(np.abs(d)))
        other = [a for a in range(3) if a != ax]
        sel = np.nonzero((pid_face != i) & cand[:, k] &
                         np.all((cen[:, other] >= lo[other]) & (cen[:, other] <= hi[other]), 1))[0]
        if not len(sel): continue
        reach = float(np.max(hi - lo)) + voxel; hit = np.zeros(len(sel), bool)
        for s in np.arange(0.5 * voxel, reach, 0.5 * voxel):
            todo = ~hit
            if not todo.any(): break
            hit[todo] = PT.sdf_part(p, cen[sel[todo]] + s * d) < 0
        cand[sel[hit], k] = False


def end_on(parts, pid_face, cen, cand, k, d):
    """A long part pointing at a camera (a beak, snout or horn seen tip-on) is drawn by that camera as a small blob
    squashed into its own base. Projected back, that blob paints the part's colours in a ring onto the face around
    it, and paints the part itself with colours it does not have. So that camera colours neither the part nor its
    footprint: whatever, as the camera sees it, lies within two and a half times the part's thickness of it (the
    views often disagree by about that much on where a small part sits), around and behind it: no nearer the camera
    than halfway along it. What stands further forward (a dog's snout above its lower jaw, with the nose at its
    tip) is drawn as it is, and that camera still colours it. So is a flat part that faces the camera squarely (a
    stag's ears beside its head seen face-on): the picture draws it at full size, the clearest thing in it."""
    import parts as PT
    face_on = np.array([p["type"] == "paddle" and max(abs(PT.paddle_frame(q)[2] @ d) for q in PT.instances(p)) > 0.7
                        for p in parts])
    for i, p in enumerate(parts):
        if p["type"] not in PT.LONG: continue
        for inst in PT.instances(p):
            A, B, ra, rb = PT.ends(inst)
            ab = B - A; L = float(np.linalg.norm(ab))
            r = max(ra, rb) if p["type"] != "chain" else float(np.median(inst["joints"][:, 3]))
            if p["type"] in ("capsule", "chain"): r *= max(1.0, float(p.get("aspect", 1.0)))
            if L < 2 * r or (ab @ d) / L < 0.75: continue              # its tip must point at the camera ...
            others = [q for j, q in enumerate(parts) if j != i]
            if others and PT.sdf(others, B[None], smooth=False)[0] < 0: continue   # ... and stick out
            cand[pid_face == i, k] = False
            def flat(X): return X - np.outer(X @ d, d)
            a2, b2 = flat(A[None])[0], flat(B[None])[0]; q = flat(cen) - a2; e = b2 - a2
            t = np.clip(q @ e / max(e @ e, 1e-12), 0, 1)
            dist = np.linalg.norm(q - np.outer(t, e), axis=1)
            depth = (cen - A) @ d                                     # towards the camera from the root
            behind = (depth < 0.5 * L + r) & (depth > -(L + 3 * r))
            cand[(dist < 2.5 * r) & behind & ~face_on[pid_face], k] = False


def dedupe_features(refs, maps, cand, facing, cen, names, vis_face, size, F):
    """One feature seen in two views (an eye in the front and the side image) lands on the model in two places
    unless the model's shape is exact, giving two eyes. Find each view's features on the model; where features from
    different cameras land close together, keep the one from the camera that faces it most squarely and stop the
    others from painting there. "Most squarely" = detection strength x facing: a slanted view squashes the feature."""
    reach = 0.05 * max(size["width"], size["length"], size["height"])
    blobs = []                                                   # (camera index, 3-D position, faces, score)
    for k, cam in enumerate(names):
        view = CAMS[cam][0]
        if maps[view].missing: continue                          # no picture for this view
        rgb = solid_rgb(refs, view); c, r = maps[view].project(cen)
        ok = vis_face[:, k] & (facing[:, k] > 0.1)
        for br, bc, rad, strength in find_features(rgb, maps[view].sil):
            sel = np.nonzero(ok & ((c - bc) ** 2 + (r - br) ** 2 < (1.5 * rad) ** 2))[0]
            if len(sel) < 3: continue
            blobs.append((k, cen[sel].mean(0), sel, strength * facing[sel, k].mean(), 1.5 * rad / maps[view].sc))
    removed = 0; kept = []
    for i, (ki, pi, si, qi, ri) in enumerate(blobs):
        for kj, pj, sj, qj, rj in blobs:
            if CAMS[names[kj]][0] == CAMS[names[ki]][0] or np.linalg.norm(pi - pj) > reach: continue
            if qj > 1.15 * qi:                                   # another view sees this feature more squarely
                keep = cand[si].sum(1) > 1                       # never leave a triangle without any view
                cand[si[keep], ki] = False; removed += 1
                break
        else:
            kept.append((ki, pi, ri, qi))
    return removed, kept


_SOLID = {}


def solid_rgb(refs, view, stray=70.0):
    """The reference's colours with every not-fully-opaque pixel (soft edges, which carry odd fringe colours) replaced
    by the nearest fully opaque one, and stray specks removed: a tiny patch (under 0.01% of the animal's picture, a
    few pixels) whose colour is far from every colour of the animal's palette, such as a green fringe left inside
    the cut-out. Eyes, claws and other small marks are close to a palette colour, or bigger, and stay."""
    key = (os.path.abspath(refs), view)
    if key in _SOLID: return _SOLID[key].copy()
    a = np.array(load_rgba(refs, view)); solid = a[..., 3] >= 250
    if not solid.any() or solid.all():
        _SOLID[key] = a[..., :3].copy(); return _SOLID[key].copy()
    _, feat, pal_f = palette(refs)
    rgb = a[..., :3].astype(float)
    far = np.zeros(solid.shape, bool)
    ys, xs = np.nonzero(solid)
    far[ys, xs] = np.sqrt(((feat(rgb[ys, xs])[:, None] - pal_f[None]) ** 2).sum(2)).min(1) > stray
    lab, nl = ndimage.label(far)
    if nl:
        sizes = ndimage.sum(far, lab, range(1, nl + 1))
        speck = np.isin(lab, 1 + np.nonzero(sizes <= max(12, 1e-4 * solid.sum()))[0])
        solid = solid & ~ndimage.binary_dilation(speck, iterations=1)
    _, (iy, ix) = ndimage.distance_transform_edt(~solid, return_indices=True)
    _SOLID[key] = a[..., :3][iy, ix]
    return _SOLID[key].copy()


def build_atlas(refs, maps, height=1024, pad=10):
    tiles, place, x0 = [], {}, 0
    for view in ("front", "back", "side", "top"):
        if maps[view].missing: continue                     # no picture for this view
        rgb_all = solid_rgb(refs, view); sil = maps[view].sil
        b = maps[view].box
        c0, r0 = max(b[0] - pad, 0), max(b[1] - pad, 0); c1, r1 = min(b[2] + pad, sil.shape[1]), min(b[3] + pad, sil.shape[0])
        rgb = rgb_all[r0:r1, c0:c1].astype(np.uint8); m = sil[r0:r1, c0:c1]
        dist, (iy, ix) = ndimage.distance_transform_edt(~m, return_indices=True)
        rgb = rgb[iy, ix]                                    # bleed edge colours outwards so seams don't pick up background
        rgb[dist > pad] = 0                                  # unused atlas space stays pure black
        s = height / (r1 - r0)
        tile = Image.fromarray(rgb).resize((max(1, round((c1 - c0) * s)), height), Image.LANCZOS)
        place[view] = (x0, c0, r0, s); tiles.append(tile); x0 += tile.width + 4
    atlas = Image.new("RGB", (x0 - 4, height), (0, 0, 0))
    for (view, (x, *_)), t in zip(place.items(), tiles): atlas.paste(t, (x, 0))
    return atlas, place


def face_neighbours(F):
    """(m, 3) index of the triangle across each edge, -1 where there is none."""
    m = len(F); e = np.sort(np.stack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]], 1), 2).reshape(-1, 2)
    key = e[:, 0] * (F.max() + 1) + e[:, 1]; fid = np.repeat(np.arange(m), 3)
    order = np.argsort(key, kind="stable"); k = key[order]; f = fid[order]
    nb = -np.ones(m * 3, np.int64)
    same = np.nonzero(k[1:] == k[:-1])[0]
    a, b = order[same], order[same + 1]
    nb[a] = f[same + 1]; nb[b] = f[same]
    return nb.reshape(m, 3)


def kmeans(X, k, iters=15, seed=0):
    rng = np.random.default_rng(seed); C = X[rng.choice(len(X), min(k, len(X)), replace=False)].astype(float)
    for _ in range(iters):
        lab = np.argmin(((X[:, None] - C[None]) ** 2).sum(2), 1)
        for j in range(len(C)):
            if (lab == j).any(): C[j] = X[lab == j].mean(0)
    return C, lab


def choose_views(cost, col, nb, seen, best, iters=10, seam=0.35, seam_base=0.08, seed=0):
    """Pick one view per triangle so that the whole texture reads well, not each triangle on its own.
    Each triangle pays its own cost for a view (facing angle etc.), plus, for every neighbour that uses a different
    view, a seam cost: seam_base plus how different the two views' colours are there. So views form large patches,
    and the borders between them move to where both pictures show the same colour, where they cannot be seen. Lone
    triangles and ragged, saw-tooth borders (a bib edge drawn a little higher in one picture than in another) are
    absorbed. Solved by iterated conditional modes, updating a random half of the triangles at a time."""
    m, K = cost.shape; rng = np.random.default_rng(seed)
    has = (nb >= 0) & seen[np.maximum(nb, 0)]
    nbi = np.maximum(nb, 0)
    norm = 255 * np.sqrt(3)
    for _ in range(iters):
        nl = np.where(has, best[nbi], -1)                                # neighbours' views
        total = cost.copy()
        for k in range(K):
            for j in range(3):
                l = nl[:, j]; diff_ = l >= 0
                differs = diff_ & (l != k)
                if not differs.any(): continue
                ll = np.maximum(l, 0)
                here = np.linalg.norm(col[:, k] - col[np.arange(m), ll], axis=1)
                there = np.linalg.norm(col[nbi[:, j], k] - col[nbi[:, j], ll], axis=1)
                total[:, k] += np.where(differs, seam * (seam_base + 0.5 * (here + there) / norm), 0)
        new = np.where(seen, np.argmin(total, 1), -1)
        upd = rng.random(m) < 0.5
        changed = upd & (new != best)
        best = np.where(upd, new, best)
        if not changed.any(): break
    return best


def small_part_groups(parts, pid_face, cen, size, voxel, rel=0.15):
    """Group the triangles of small mirrored parts into clusters, one per connected cluster per side: all the toes,
    claws and pad of one foot; one ear; one paw. Returns a group id per triangle (-1 = not in a small cluster)."""
    import parts as PT
    big = rel * max(size["width"], size["length"], size["height"])
    small = [i for i, p in enumerate(parts) if p["mirror"] and PT.scale_of(p) < big]
    group = -np.ones(len(cen), int)
    if not small: return group
    side = cen[:, 0] > 0
    for s in (True, False):
        boxes = {}
        for i in small:
            sel = (pid_face == i) & (side == s)
            if sel.sum() >= 3: boxes[i] = (cen[sel].min(0) - 2 * voxel, cen[sel].max(0) + 2 * voxel)
        root = {i: i for i in boxes}
        def find(i):
            while root[i] != i: i = root[i]
            return i
        ids = list(boxes)
        for a in ids:                                            # parts whose boxes touch belong together
            for b in ids:
                if a < b and np.all(boxes[a][0] <= boxes[b][1]) and np.all(boxes[b][0] <= boxes[a][1]):
                    root[find(a)] = find(b)
        for i in ids:
            group[(pid_face == i) & (side == s)] = find(i) * 2 + int(s)
    return group


def limit_views(cand, facing, area, group, max_views=2):
    """A small cluster (one foot with its toes and claws) takes its colours from at most max_views pictures: the ones
    that see the most of it squarely. Every picture draws a small part with its own shading and slightly off the
    model, so a foot stitched together from four pictures comes out as a patchwork of splotches."""
    out = cand.copy()
    for g in np.unique(group[group >= 0]):
        sel = np.nonzero(group == g)[0]
        score = (area[sel, None] * np.clip(facing[sel], 0, None) * cand[sel]).sum(0)
        keep = np.zeros(cand.shape[1], bool); keep[np.argsort(-score)[:max_views]] = True; keep &= score > 0
        lim = cand[sel] & keep
        none = ~lim.any(1)                                       # never leave a triangle without a view
        lim[none] = cand[sel][none]
        out[sel] = lim
    return out


def fill_unseen(fcol, seen, nb, pid_face, refs):
    """Colours for triangles no picture shows (soles, undersides, between toes). Nothing is guessed: each such area is
    flood-filled with one flat colour, the average colour of its part, so it stays consistent with the figure. A
    part may be several colours (a penguin's body is black and white, whose average would be a grey found nowhere
    on the bird), so the average is taken per colour region: every seen spot is assigned to one of the animal's
    palette colours, the regions grow into the unseen area from its border (within the part), and each filled spot
    takes the average colour of the region that reached it. Returns the colours, the fill colours, and per unseen
    triangle its fill index."""
    m = len(fcol); nbi = np.maximum(nb, 0)
    _, feat, pal_f = palette(refs)
    lab = -np.ones(m, int)
    if seen.any(): lab[seen] = np.argmin(((feat(fcol[seen])[:, None] - pal_f[None]) ** 2).sum(2), 1)
    part = pid_face if pid_face is not None else np.zeros(m, int)
    if pid_face is not None:                                        # a spot of a part on which that colour is rare
        for q in np.unique(part[seen]):                             # (pink smeared in from the legs onto the belly)
            sq = seen & (part == q)                                 # is not a region of that part
            share = np.bincount(lab[sq], minlength=len(pal_f)) / max(sq.sum(), 1)
            lab[sq & (share[np.maximum(lab, 0)] < 0.05)] = -2
    lab[lab == -2] = -1; spare = seen & (lab < 0)                   # (re-labelled by growing, but still seen)
    for same_part in (True, False):                                 # grow the regions into the unseen area
        for _ in range(2000):
            todo = lab < 0
            if not todo.any(): break
            nl = np.where(nb >= 0, lab[nbi], -1)
            if same_part: nl = np.where(part[nbi] == part[:, None], nl, -1)
            has = todo & (nl >= 0).any(1)
            if not has.any(): break
            nh = nl[has]; K = len(pal_f); votes = np.zeros((len(nh), K))
            for j in range(nh.shape[1]):
                ok = nh[:, j] >= 0; votes[np.nonzero(ok)[0], nh[ok, j]] += 1
            lab[np.nonzero(has)[0]] = np.argmax(votes, 1)                 # the region most neighbours belong to
    unseen = np.nonzero(~seen)[0]
    keys, fill = {}, []
    seen = seen & ~spare                                            # averages only from a part's main regions
    lab_u = np.zeros(len(unseen), int)
    glob = fcol[seen].mean(0) if seen.any() else np.full(3, 128.0)
    for j, ti in enumerate(unseen):
        key = (int(part[ti]), int(lab[ti]))
        if key not in keys:
            src = seen & (part == key[0]) & (lab == key[1])
            if not src.any(): src = seen & (part == key[0])             # the part's own average
            keys[key] = len(fill); fill.append(fcol[src].mean(0) if src.any() else glob)
        lab_u[j] = keys[key]
    fill = np.array(fill, float).reshape(-1, 3)
    if len(unseen): fcol[unseen] = fill[lab_u]
    return fcol, fill, lab_u


BAKE_SIZE = 2048     # texture image size (pixels per side)
FEATHER = 4          # how far (in mesh edges, about 2.5 mm each) one picture's colours fade into the next's
PLAN_SMOOTH = 0.018  # colour regions are smoothed over this distance (share of the animal's size): thinner slivers go
DETAIL_MM = 3.0      # fine detail (feather strokes, scales) is what varies within this distance in the drawings
DETAIL_MAX = 40.0    # strongest detail kept (colour levels): broad shading and misplaced edges are not detail


def palette(refs, k=12, merge=28.0, min_share=0.002, seed=0):
    """The few colours the animal is painted in, from all its pictures: k-means, then near-duplicates merged.
    Lightness counts half as much as hue, so a shaded and a lit patch of the same feathers count as one colour."""
    rng = np.random.default_rng(seed); X = []
    for v in ("front", "side", "back"):
        if not os.path.exists(os.path.join(refs, f"{v}.png")): continue          # no picture for this view
        a = np.array(load_rgba(refs, v)); m = a[..., 3] >= 250
        px = a[..., :3][m].astype(float)
        if len(px): X.append(px[rng.choice(len(px), min(len(px), 30000), replace=False)])
    X = np.concatenate(X)
    w = np.array([0.5, 1.0, 1.0])
    def feat(c):                                                     # lightness, then two colour axes
        L = c @ [0.299, 0.587, 0.114]
        return np.c_[L, c[:, 0] - c[:, 1], 0.5 * (c[:, 0] + c[:, 1]) - c[:, 2]] * w
    C, lab = kmeans(feat(X), k, seed=seed)
    groups = list(range(len(C)))
    for i in range(len(C)):
        for j in range(i):
            if np.linalg.norm(C[i] - C[j]) < merge: groups = [groups[j] if g == groups[i] else g for g in groups]
    out = []
    for g in sorted(set(groups)):
        sel = np.isin(lab, [i for i in range(len(C)) if groups[i] == g])
        if sel.mean() >= min_share: out.append(np.median(X[sel], 0))
    P = np.array(out)
    return P, (lambda c: feat(c)), feat(P)


def sample_views(refs, maps, names, cache, P, Wt):
    out = np.zeros((len(P), 3))
    for k, cam in enumerate(names):
        sel = Wt[:, k] > 1e-4
        if not sel.any(): continue
        view = CAMS[cam][0]
        if view not in cache: cache[view] = solid_rgb(refs, view).astype(np.float32)
        img = cache[view]; c, r = maps[view].project(P[sel])
        smp = np.stack([ndimage.map_coordinates(img[..., ch], [r - 0.5, c - 0.5], order=1, mode="nearest")
                        for ch in range(3)], 1)
        out[sel] += Wt[sel, k, None] * smp
    return out


def borrowed_detail(detail, gw, region, part, yy, xx, size, strength=0.8):
    """Fine texture for spots no picture sees. Their colour stays the flat fill (the region's own average); only
    the drawing's fine strokes (fur, feathers, scales) are borrowed, so a filled belly does not look like plastic
    beside drawn fur. Per part and colour region: the largest square of texture that a picture sees squarely and
    wholly in that region of that part is tiled, mirrored at its edges so the tiles meet without seams. Only from
    the same part: one palette region may hold a stag's cream throat and its antlers, and antler grain tiled
    across a throat reads as stripes. A part with no such square of its own stays plain. Returns per-texel
    detail (0 where there is none)."""
    out = np.zeros((len(yy), 3), np.float32)
    det = np.zeros((size, size, 3), np.float32); det[yy, xx] = detail
    patches = {}
    for i, c in set(zip(part.tolist(), region.tolist())):
        sel = (part == i) & (region == c) & (gw > 0.8)
        if sel.sum() < 256: continue
        good = np.zeros((size, size), bool); good[yy[sel], xx[sel]] = True
        ii = np.pad(good.astype(np.int32).cumsum(0).cumsum(1), ((1, 0), (1, 0)))
        for B in (64, 48, 32, 24, 16):                      # the largest square wholly seen
            full = ii[B:, B:] - ii[:-B, B:] - ii[B:, :-B] + ii[:-B, :-B] == B * B
            if full.any(): break
        else: continue
        r, q = np.argwhere(full)[0]
        patch = det[r:r + B, q:q + B]
        patches[(i, c)] = np.concatenate([np.concatenate([patch, patch[:, ::-1]], 1),
                                          np.concatenate([patch[::-1], patch[::-1, ::-1]], 1)], 0)
    for (i, c), tile in patches.items():
        B2 = len(tile); m = (part == i) & (region == c)
        out[m] = strength * tile[yy[m] % B2, xx[m] % B2]
    return out


def part_region_colours(pal, d2, raw_v, fill_w, vpart, A, deg, min_n=30):
    """The colour each palette region has on each part: the median of the drawings' colours there, from vertices a
    picture paints (not filled), wherever the part shows enough of that region; else the palette colour itself.
    Per vertex (vertices x regions x RGB), softened across part borders so neighbouring parts do not meet in a
    step (a slightly creamier neck than chest)."""
    vlab = np.argmin(d2, 1); src = fill_w < 0.5
    out = np.repeat(pal[None].astype(np.float32), len(vlab), 0)
    for i in np.unique(vpart):
        on = vpart == i
        for g in range(len(pal)):
            s = src & on & (vlab == g)
            if s.sum() >= min_n: out[on, g] = np.median(raw_v[s], 0)
    flat = out.reshape(len(vlab), -1)
    for _ in range(6): flat = 0.5 * flat + 0.5 * (A @ flat) / deg[:, None]
    return flat.reshape(out.shape)


def bake_uv(refs, S, F, V, N, best, cand, seen, fcol, names, pid_face, cen, facing, edge, features=()):
    """Paint the model into a proper UV texture (see uv.py). Where a picture sees the spot squarely, away from other
    parts and from a handover between pictures, the drawing is kept as drawn. Everywhere else (slanted views, part
    edges, handovers, unseen areas) a colour plan takes over:
    1. Palette: the few colours the animal is painted in.
    2. Plan: every spot of the surface votes for a palette colour, from the drawings (blended where one picture's
       area meets another's) or, where no picture sees it, from its part's own colour. The votes are smoothed over
       the surface within each part, so a colour patch thinner than about 2% of the animal (a sliver of white
       belly painted behind a flipper, beak red smeared onto the face) loses, and every border becomes a smooth
       curve. Each spot is painted in its region's flat colour: the artist's broad shading is gone. That colour is
       the region's colour on that part, as the pictures show it there (part_region_colours): one palette colour
       may cover the cream of a stag's throat and the grey of its antlers, whose average is on neither.
    3. Detail: the drawing's fine texture (feather strokes, scales), only where it belongs to the same colour
       region and the picture sees the spot squarely, added on top, so the regions are not flat plastic. Where no
       picture sees the spot, the fine texture is borrowed from elsewhere in the same region (borrowed_detail).
    4. Stickers: the strongest small features found in the drawings (eyes, nostrils) are copied as drawn from the
       one picture that shows them best, where that picture sees them, so the plan does not smooth them away."""
    import uv as UV
    from scipy import sparse
    maps = S["maps"]; K = len(names); size = S.get("bake_size", BAKE_SIZE)
    big = max(S["size"][k] for k in ("width", "length", "height"))
    uvm, island = UV.unwrap(V, F, S["parts"], pid_face, cen)
    px, scale = UV.pack(uvm, island, size)
    tid = UV.raster_ids(px, size)
    yy, xx = np.nonzero(tid >= 0); t = tid[yy, xx]
    w = UV.barycentric(px, t, yy, xx)
    P = (V[F[t]] * w[..., None]).sum(1)

    # which picture each vertex and texel takes its colour from (or the fill, channel K), cross-faded at handovers
    lab = np.where(seen, best, K)
    W = np.zeros((len(V), K + 1)); np.add.at(W, F.reshape(-1), np.eye(K + 1)[np.repeat(lab, 3)])
    e = np.r_[F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]
    A = sparse.coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(len(V), len(V))).tocsr()
    A = ((A + A.T) > 0).astype(float); deg = np.maximum(np.asarray(A.sum(1)).ravel(), 1)
    W /= np.maximum(W.sum(1, keepdims=True), 1e-12)
    for _ in range(FEATHER): W = 0.5 * W + 0.5 * (A @ W) / deg[:, None]
    vcand = np.zeros((len(V), K), bool)
    for c in range(3): vcand[F[:, c]] |= cand
    Wv = W.copy(); Wv[:, :K] *= vcand; Wv /= np.maximum(Wv.sum(1, keepdims=True), 1e-12)
    Wt = (W[F[t]] * w[..., None]).sum(1)
    Wt[:, :K] *= cand[t]
    Wt[np.arange(len(t)), lab[t]] += 1e-3
    Wt /= Wt.sum(1, keepdims=True)

    cache = {}
    raw_t = sample_views(refs, maps, names, cache, P, Wt)               # the drawings, blended
    raw_v = sample_views(refs, maps, names, cache, V, Wv)
    vc = np.zeros((len(V), 3)); cnt = np.zeros(len(V))                 # part colour where no picture sees
    np.add.at(vc, F.reshape(-1), np.repeat(fcol, 3, 0)); np.add.at(cnt, F.reshape(-1), 1)
    vc /= np.maximum(cnt, 1)[:, None]
    for _ in range(6): vc = 0.5 * vc + 0.5 * (A @ vc) / deg[:, None]     # soft, not stepped, where fills meet
    raw_t += Wt[:, K, None] * (vc[F[t]] * w[..., None]).sum(1)
    raw_v += Wv[:, K, None] * vc

    # 1-2. palette and plan: votes per vertex, smoothed within each part
    pal, feat, pal_f = palette(refs)
    d2 = ((feat(raw_v)[:, None] - pal_f[None]) ** 2).sum(2)
    vface = np.zeros((len(V), K)); vn = np.zeros(len(V))
    np.add.at(vface, F.reshape(-1), np.repeat(np.clip(facing, 0, 1), 3, 0)); np.add.at(vn, F.reshape(-1), 1)
    vface /= np.maximum(vn, 1)[:, None]
    conf = 0.1 + (Wv[:, :K] * vface).sum(1)                             # a square view outvotes a slanted one,
    vote = np.eye(len(pal))[np.argmin(d2, 1)] * conf[:, None]           # and both outvote a guess
    vpart = np.zeros(len(V), int); vpart[F.reshape(-1)] = np.repeat(pid_face, 3)
    ei, ej = A.nonzero(); keep = vpart[ei] == vpart[ej]
    As = sparse.coo_matrix((np.ones(keep.sum()), (ei[keep], ej[keep])), shape=A.shape).tocsr()
    degs = np.maximum(np.asarray(As.sum(1)).ravel(), 1)
    iters = int(np.clip(2 * (PLAN_SMOOTH * big / S["voxel"]) ** 2, 4, 80))
    for _ in range(iters): vote = 0.5 * vote + 0.5 * (As @ vote) / degs[:, None]
    vote /= np.maximum(vote.sum(1, keepdims=True), 1e-12)
    pt = (vote[F[t]] * w[..., None]).sum(1)
    pt = pt ** 6; pt /= np.maximum(pt.sum(1, keepdims=True), 1e-12)   # crisp but anti-aliased borders
    pcol = part_region_colours(pal, d2, raw_v, Wv[:, K], vpart, A, deg)
    plan = np.zeros((len(t), 3))
    for g in range(len(pal)): plan += pt[:, g, None] * (pcol[F[t], g] * w[..., None]).sum(1)

    # 3. detail: the drawing's fine texture within the same colour region, faded out where the picture grazes
    tex_raw = np.zeros((size, size, 3), np.float32); filled = np.zeros((size, size), bool)
    tex_raw[yy, xx] = raw_t; filled[yy, xx] = True
    tex_raw = UV.dilate(tex_raw, filled)
    sig = DETAIL_MM / (1000 / scale)
    low = np.stack([ndimage.gaussian_filter(tex_raw[..., c], sig) for c in range(3)], -1)[yy, xx]
    detail = np.clip(raw_t - low, -DETAIL_MAX, DETAIL_MAX)
    same_region = np.argmin(((feat(raw_t)[:, None] - pal_f[None]) ** 2).sum(2), 1) == np.argmax(pt, 1)
    face_t = (facing[t] * Wt[:, :K]).sum(1)
    gw = np.clip((face_t - 0.35) / 0.35, 0, 1) * same_region * (1 - Wt[:, K])
    borrowed = borrowed_detail(detail, gw, np.argmax(pt, 1), pid_face[t], yy, xx, size)
    planned = plan + gw[:, None] * detail + Wt[:, K, None] * borrowed
    # trust in the drawing: a picture that sees the spot squarely, away from other parts and away from a handover
    # between pictures, is right as drawn (eyes, faces, emblems, spots). Elsewhere the plan takes over.
    tri_trust = np.clip((np.where(seen, facing[np.arange(len(F)), np.maximum(best, 0)], 0) - 0.45) / 0.3, 0, 1)
    tri_trust *= 1 - np.where(seen, edge[np.arange(len(F)), np.maximum(best, 0)], 1)
    vt = np.zeros(len(V)); np.add.at(vt, F.reshape(-1), np.repeat(tri_trust, 3)); vt /= np.maximum(vn, 1)
    for _ in range(FEATHER): vt = 0.5 * vt + 0.5 * (A @ vt) / deg
    trust = (vt[F[t]] * w).sum(1) * (1 - Wt[:, K]) * Wt[:, :K].max(1)
    colour = trust[:, None] * raw_t + (1 - trust[:, None]) * planned

    # per-part colour: parts that say they are one colour are painted in it, with only the drawing's fine detail
    # on top, cross-faded into their neighbours over a few millimetres
    fixed = [(i, p["colour"]) for i, p in enumerate(S["parts"]) if p.get("colour")]
    if fixed:
        fv = np.zeros((len(V), 3)); fm = np.zeros(len(V))
        ptex = pid_face[t]
        for i, spec in fixed:
            if str(spec).lower() == "drawn":                            # the part's main palette colour
                sel = ptex == i
                if not sel.any(): continue
                c = pal[np.argmax((pt[sel] * (0.1 + trust[sel, None])).sum(0))]
            else:
                h = str(spec).lstrip("#"); c = np.array([int(h[j:j + 2], 16) for j in (0, 2, 4)], float)
            vs = np.unique(F[pid_face == i]); fv[vs] = c; fm[vs] = 1
        fcolv = fv.copy()
        for _ in range(2):
            num = (A @ (fcolv * fm[:, None])) + fcolv * fm[:, None]; den = (A @ fm) + fm
            fm = 0.5 * fm + 0.5 * (A @ fm) / deg
            fcolv = np.where(den[:, None] > 0, num / np.maximum(den, 1e-12)[:, None], fcolv)
        alpha = (fm[F[t]] * w).sum(1)
        paint = (fcolv[F[t]] * w[..., None]).sum(1)
        near = np.linalg.norm(feat(raw_t) - feat(paint), axis=1) < 45             # detail only where the drawing
        colour = (1 - alpha[:, None]) * colour + alpha[:, None] * (paint + (gw * near)[:, None] * detail)  # agrees

    # 4. stickers: features as drawn, faded in over their outer third
    qmax = max([f[3] for f in features], default=0)
    for k, c3, rad, q in features:
        if q < 0.3 * qmax: continue                                    # a faint mark, not an eye
        d = np.linalg.norm(P - c3, axis=1)
        a = np.clip((rad - d) / (0.35 * rad), 0, 1) * cand[t, k]       # only where that picture sees the spot
        if not (a > 0).any(): continue
        sel = a > 0
        one = np.zeros((sel.sum(), K)); one[:, k] = 1
        drawn = sample_views(refs, maps, names, cache, P[sel], one)
        colour[sel] = (1 - a[sel, None]) * colour[sel] + a[sel, None] * drawn

    tex = np.zeros((size, size, 3), np.float32); tex[yy, xx] = colour
    atlas = Image.fromarray(np.clip(UV.dilate(tex, filled), 0, 255).astype(np.uint8))
    V2, F2, N2, uv2 = UV.split_vertices(V, F, N, px, island, size)
    return V2, F2, uv2, atlas, N2, int(island.max() + 1), round(1000 / scale, 2), len(pal)


def texture_mesh(refs, S, tol=3, debug=None):
    V, F, occ, axes, voxel, maps = S["V"], S["F"], S["occ"], S["axes"], S["voxel"], S["maps"]
    origin = np.array([axes["x"][0], axes["y"][0], axes["z"][0]])
    tri = V[F]
    if S.get("N") is not None:                                       # smooth normals from the shape itself
        n = S["N"][F].mean(1)
    else:
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        if (n * (tri.mean(1) - V.mean(0))).sum(1).mean() < 0: n = -n # make normals point outwards
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    names = list(CAMS); m = len(F)
    facing = np.zeros((m, len(names))); cand = np.zeros((m, len(names)), bool); col = np.zeros((m, len(names), 3))
    edge = np.zeros((m, len(names))); vis_face = np.zeros((m, len(names)), bool)
    imgs = {v: np.asarray(Image.fromarray(solid_rgb(refs, v)).filter(ImageFilter.BoxBlur(2)), float)
            for v in maps if not maps[v].missing}                   # (a view with no picture paints nothing)
    cen = tri.mean(1)
    parts = S.get("parts")
    if parts:
        import parts as PT
        pid_face = PT.nearest_part(parts, cen)
        margin = max(3.0, 0.025 * max(S["size"][k] for k in ("width", "length", "height")) / voxel)   # in voxels
    for k, cam in enumerate(names):
        view, d, axis, high = CAMS[cam]
        if maps[view].missing: continue                              # no picture: this camera sees nothing
        occ_v = occ
        if view in S.get("ignored_space", {}):                       # a part that ignores this view (the picture
            occ_v = occ & ~S["ignored_space"][view]                  # leaves it out or draws it wrongly) does not
        vis = depth_ok(V, occ_v, origin, voxel, axis, high, tol)     # hide what is behind it from this camera
        facing[:, k] = n @ np.array(d, float)
        vis_face[:, k] = vis[F].all(1)
        cand[:, k] = vis_face[:, k] & (facing[:, k] > MIN_FACING)
        if parts:
            ignored = np.array([view in p.get("ignore", []) for p in parts])
            cand[ignored[pid_face], k] = False                       # this view draws that part wrongly
            for i, p in enumerate(parts):                            # a flat paddle seen edge-on: the picture
                if p["type"] != "paddle": continue                   # shows whatever lies beside its thin edge
                fn = PT.paddle_frame(p)[2]
                if abs(fn @ np.array(d, float)) < 0.5: cand[pid_face == i, k] = False
            end_on(parts, pid_face, cen, cand, k, np.array(d, float))
            behind_paddles(parts, pid_face, cen, cand, k, np.array(d, float), voxel)
            edge[:, k] = near_other_part(parts, occ, origin, voxel, axis, high, pid_face, cen, margin)
        c, r = maps[view].project(cen); im = imgs[view]
        col[:, k] = im[np.clip(r.astype(int), 0, im.shape[0] - 1), np.clip(c.astype(int), 0, im.shape[1] - 1)]

    deduped, features = dedupe_features(refs, maps, cand, facing, cen, names, vis_face, S["size"], F)
    if parts:
        area = 0.5 * np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
        cand = limit_views(cand, facing, area, small_part_groups(parts, pid_face, cen, S["size"], voxel))
    masked = np.where(cand[..., None], col, np.nan)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)       # triangles no view sees have no consensus
        consensus = np.nanmedian(masked, 1)
    disagree = np.linalg.norm(col - consensus[:, None], axis=2) / (255 * np.sqrt(3))
    graze = np.clip((0.5 - facing) / (0.5 - MIN_FACING), 0, 1)
    cost = np.where(cand, -facing + DISAGREE * np.nan_to_num(disagree) + EDGE * edge + GRAZE * graze, np.inf)
    # undersides: a picture looking across a downward-facing surface sees the shadow the artist drew under the body,
    # not its colour; such surfaces are treated as unseen and flood-filled (fill_unseen)
    cand[n[:, 2] < -UNDERSIDE] = False
    if parts: paddle_shadow(parts, pid_face, cen, n, cand, S["size"])
    seen = cand.any(1)
    best = np.where(seen, np.argmin(cost, 1), -1)

    nb = face_neighbours(F)
    best = choose_views(cost, col, nb, seen, best)

    fcol = np.zeros((m, 3)); fcol[seen] = col[np.nonzero(seen)[0], best[seen]]
    fcol, C, lab_u = fill_unseen(fcol, seen, nb, pid_face if parts else None, refs)

    if S.get("N") is not None:
        N = S["N"]
    else:
        from glb_io import vertex_normals
        N = vertex_normals(V, F) * (1 if (n * (tri.mean(1) - V.mean(0))).sum(1).mean() >= 0 else -1)
    if parts:
        unseen = np.nonzero(~seen)[0]
        if len(unseen): fcol[unseen] = C[lab_u]                     # unseen areas: the part's own main colour
        out = bake_uv(refs, S, F, V, N, best, cand, seen, fcol, names, pid_face, cen, facing, edge, features)
        stats = {cam: round(float((best == k).mean()), 3) for k, cam in enumerate(names)}
        stats.update(unseen_filled=round(float((~seen).mean()), 3), duplicate_features_removed=deduped,
                     uv_islands=out[5], texel_mm=out[6], palette_colours=out[7])
        if debug is not None: debug.update(best=best, seen=seen, cand=cand, facing=facing, edge=edge, col=col, names=names)
        return out[0], out[1], out[2], out[3], stats, out[4]

    atlas, place = build_atlas(refs, maps)
    unseen = np.nonzero(~seen)[0]
    if len(unseen):
        strip = Image.new("RGB", (max(atlas.width, SWATCH * len(C)), SWATCH), (0, 0, 0))
        for j, c in enumerate(C): strip.paste(tuple(int(v) for v in c), (j * SWATCH, 0, (j + 1) * SWATCH, SWATCH))
        full = Image.new("RGB", (strip.width, atlas.height + SWATCH), (0, 0, 0)); full.paste(atlas, (0, 0)); full.paste(strip, (0, atlas.height))
        atlas = full
        group = best.copy(); group[unseen] = len(names) + lab_u
    else:
        C = np.zeros((0, 3)); group = best

    if S.get("N") is not None:
        N = S["N"]
    else:
        from glb_io import vertex_normals
        N = vertex_normals(V, F) * (1 if (n * (tri.mean(1) - V.mean(0))).sum(1).mean() >= 0 else -1)
    Vs, Ns, Fs, UVs, base, stats = [], [], [], [], 0, {}
    for g in np.unique(group):
        sel = np.nonzero(group == g)[0]
        used, inv = np.unique(F[sel], return_inverse=True)
        if g < len(names):
            cam = names[g]; stats[cam] = round(len(sel) / m, 3)
            view = CAMS[cam][0]; c, r = maps[view].project(V[used]); x, c0, r0, s = place[view]
            uv = np.c_[(x + (c - c0) * s) / atlas.width, (r - r0) * s / atlas.height]
        else:
            j = g - len(names)
            uv = np.tile([((j + 0.5) * SWATCH) / atlas.width, (atlas.height - SWATCH / 2) / atlas.height], (len(used), 1))
        Vs.append(V[used]); Ns.append(N[used]); Fs.append(inv.reshape(-1, 3) + base); UVs.append(uv); base += len(used)
    stats["unseen_filled"] = round(float((~seen).mean()), 3); stats["duplicate_features_removed"] = deduped
    if debug is not None: debug.update(best=best, seen=seen, cand=cand, facing=facing, edge=edge, col=col, names=names)
    return np.vstack(Vs), np.vstack(Fs), np.vstack(UVs), atlas, stats, np.vstack(Ns)
