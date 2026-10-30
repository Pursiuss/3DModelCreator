"""Shape from the four silhouettes: visual hull, rounded cross-sections, smooth closed mesh.

usage: python carve.py REFS_DIR OUT.glb [--res 280] [--round 2] [--blur 1.5] [--smooth 12] [--masks]

1. Visual hull. Each view is mapped exactly as score_glb.py maps it. Orthographic axis-aligned views make it separable:
     keep(x, y, z) = front(x, z) & back(x, z) & side(y, z) & top(x, y)
2. Rounding. A hull from four straight-on views has box-like cross-sections. In every horizontal slice, each connected
   region is intersected with the superellipse inscribed in its bounding box (|u|^p + |v|^p <= 1; p = 2 is an ellipse,
   larger p is boxier, 0 turns rounding off). Bodies become round; outlines barely change.
3. Mesh. Marching cubes on the voxels, then Taubin smoothing (smooths stair-steps without shrinking thin parts).
"""
import argparse, os, sys
import numpy as np
from scipy import ndimage, sparse
from skimage import measure
sys.path.insert(0, os.path.dirname(__file__))
from views import VIEWS, AX, ViewMap, load_subject, silhouette, view_maps
from glb_io import write_glb


def sample(vm, axes):
    """This view's silhouette on the grid axes it sees, indexed [h, v]."""
    ha, _, va, _ = VIEWS[vm.view]
    P_h = np.zeros((len(axes[ha]), 3)); P_h[:, AX[ha]] = axes[ha]
    P_v = np.zeros((len(axes[va]), 3)); P_v[:, AX[va]] = axes[va]
    c = np.floor(vm.project(P_h)[0]).astype(int)
    r = np.floor(vm.project(P_v)[1]).astype(int)
    ok_c = (c >= 0) & (c < vm.sil.shape[1]); ok_r = (r >= 0) & (r < vm.sil.shape[0])
    out = np.zeros((len(c), len(r)), bool)
    out[np.ix_(ok_c, ok_r)] = vm.sil[np.ix_(r[ok_r], c[ok_c])].T
    return out


def capped_res(maps, size, res, max_points):
    """res, lowered if needed so that the grid make_grid builds has at most max_points points. Grids are sized by the
    animal's longest dimension, so a long, wide animal (a deer with spread antlers) gets many times the points of an
    upright one at the same res; the cap keeps fitting and checking times about the same for every animal."""
    for _ in range(4):
        axes, _ = make_grid(maps, size, res)
        n = len(axes["x"]) * len(axes["y"]) * len(axes["z"])
        if n <= max_points: break
        res = int(res * (max_points / n) ** (1 / 3))
    return res


def make_grid(maps, size, res):
    half_x = max(maps[v].half_h for v in ("front", "back", "top"))
    half_y = max(maps["side"].half_h, maps["top"].span_v / 2)
    top = max(maps[v].span_v for v in ("front", "back", "side"))
    voxel = max(2 * half_x, 2 * half_y, top) / res
    axes = {"x": np.arange(-half_x * 1.08, half_x * 1.08, voxel) + voxel / 2,
            "y": np.arange(-half_y * 1.08, half_y * 1.08, voxel) + voxel / 2,
            "z": np.arange(0, top * 1.04, voxel) + voxel / 2}
    return axes, voxel


def visual_hull(maps, axes, skip=()):
    """skip: views left out of the carving (e.g. a back view drawn in a different pose). Each skipped view stops
    constraining the shape, so only skip one that clearly disagrees with the others."""
    L = {v: sample(maps[v], axes) for v in VIEWS}
    occ = np.ones((len(axes["x"]), len(axes["y"]), len(axes["z"])), bool)
    if "front" not in skip: occ &= L["front"][:, None, :]
    if "back" not in skip: occ &= L["back"][:, None, :]
    if "side" not in skip: occ &= L["side"][None, :, :]
    if "top" not in skip: occ &= L["top"][:, :, None]
    return occ


def round_slices(occ, p):
    if p <= 0: return occ
    out = np.zeros_like(occ)
    for k in range(occ.shape[2]):
        s = occ[:, :, k]
        if not s.any(): continue
        lab, n = ndimage.label(s)
        for i, sl in enumerate(ndimage.find_objects(lab), 1):
            comp = lab[sl] == i
            nx, ny = comp.shape
            u = (np.arange(nx) + 0.5) / nx * 2 - 1; v = (np.arange(ny) + 0.5) / ny * 2 - 1
            ell = (np.abs(u)[:, None] ** p + np.abs(v)[None, :] ** p) <= 1.0
            if nx <= 2 or ny <= 2: ell[:] = True        # too thin to round
            out[:, :, k][sl] |= comp & ell
    return out


def taubin(V, F, iters=12, lam=0.5, mu=-0.53):
    n = len(V)
    e = np.r_[F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]
    A = sparse.coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n)).tocsr()
    A = ((A + A.T) > 0).astype(float)
    deg = np.asarray(A.sum(1)).ravel(); Dinv = sparse.diags(1 / np.maximum(deg, 1))
    W = Dinv @ A
    for _ in range(iters):
        V = V + lam * (W @ V - V)
        V = V + mu * (W @ V - V)
    return V


def soft_volume(occ, blur):
    """Blurred occupancy for marching cubes. Parts thinner than the blur would vanish, so they are kept at full strength."""
    vol = occ.astype(np.float32)
    if blur <= 0: return vol
    r = max(1, int(round(blur * 1.5)))
    thin = occ & ~ndimage.binary_opening(occ, structure=np.ones((3, 3, 3)), iterations=r)
    soft = ndimage.gaussian_filter(vol, blur)
    return np.maximum(soft, 0.6 * thin)


def to_mesh(occ, axes, voxel, smooth_iters=12, blur=1.5):
    vol = np.pad(soft_volume(occ, blur), 1)
    verts, faces, _, _ = measure.marching_cubes(vol, 0.5)
    V = (verts - 1) * voxel + np.array([axes["x"][0], axes["y"][0], axes["z"][0]])
    F = faces[:, ::-1].astype(np.int64)      # outward-facing winding
    if smooth_iters: V = taubin(V, F, smooth_iters)
    return V, F


def recentre(V):
    """What the scorer assumes: feet at z = 0, centred sideways and lengthwise on the model's own extent."""
    shift = np.array([-(V[:, 0].min() + V[:, 0].max()) / 2, -(V[:, 1].min() + V[:, 1].max()) / 2, -V[:, 2].min()])
    return V + shift


def build_shape(refs, res=280, roundness=2.0, use_masks=False, smooth_iters=12, blur=1.5, skip=()):
    size, _ = load_subject(refs)
    sils, notes = {}, {}
    for v in VIEWS: sils[v], notes[v] = silhouette(refs, v, use_masks)
    maps = view_maps(refs, size, sils)
    axes, voxel = make_grid(maps, size, res)
    hull = visual_hull(maps, axes, skip)
    occ = round_slices(hull, roundness)
    V, F = to_mesh(occ, axes, voxel, smooth_iters, blur)
    return dict(size=size, maps=maps, notes=notes, axes=axes, voxel=voxel, hull=hull, occ=occ, V=V, F=F)


def signed_distance(occ, voxel):
    """Metres to the surface of a voxel solid: negative inside, positive outside."""
    return (ndimage.distance_transform_edt(~occ) - ndimage.distance_transform_edt(occ)) * voxel


def smoothed_outline_distance(vm, rel_sigma=0.025, rel_close=0.012):
    """Signed distance to a reference outline in pixels (negative inside), cleaned of the drawing's wobble.
    Trimming only ever removes material, so only the outline's dents matter: the notches between feather tips on a
    tail, or between tufts of fur, cut grooves across the model. A morphological closing fills dents narrower than
    about 2.4% of the animal (it never removes anything, so thin parts survive it). Then, where the animal is thick,
    the outline is smoothed as well, which irons out the gentle scallops along a feathered belly; thin parts (wing
    membranes, legs, antennae) keep their exact outline, so smoothing never cuts them away."""
    b = vm.box; extent = max(b[2] - b[0], b[3] - b[1])
    sil = vm.sil
    r = int(round(rel_close * extent))
    if r >= 1:
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1]; disk = xx * xx + yy * yy <= r * r
        sil = ndimage.binary_closing(np.pad(sil, r + 1), disk)[r + 1:-r - 1, r + 1:-r - 1] | sil
    d = ndimage.distance_transform_edt(~sil) - ndimage.distance_transform_edt(sil)
    sigma = rel_sigma * extent
    if sigma < 1: return d
    # Blurring a distance field moves a curved surface inwards by sigma^2/2 times its curvature (a head of radius R by
    # sigma^2/R); add that back, measured on a coarser blur so that it follows the overall form, not the dips.
    smooth = ndimage.gaussian_filter(d, sigma) - 0.5 * sigma ** 2 * ndimage.gaussian_laplace(d, 2 * sigma)
    half = ndimage.grey_dilation(np.maximum(-d, 0), size=int(6 * sigma) | 1)   # local half-thickness nearby
    w = np.clip((half - 2 * sigma) / (2 * sigma), 0, 1)
    return w * smooth + (1 - w) * d


def hull_distance(maps, axes, skip=(), ignore=None, second=False):
    """Smooth signed distance (metres) to the visual hull, built from each outline's 2-D distance map at full image
    resolution: the hull is the intersection of the outlines pushed straight back, so its distance is the largest of
    the per-view distances. No voxel steps, and thin parts keep their full width.
    ignore: {view: boolean grid} of voxels that view must not trim (parts that list it in ignore_views).
    second: also return the second largest distance among the three viewing directions (front and back look along
    the same line, so they count as one): where it is positive, two directions agree a point is outside."""
    out = None; shape = (len(axes["x"]), len(axes["y"]), len(axes["z"]))
    by_dir = {}
    for v, vm in maps.items():
        if v in skip: continue
        d2 = smoothed_outline_distance(vm) / vm.sc
        ha, _, va, _ = VIEWS[v]
        P_h = np.zeros((len(axes[ha]), 3)); P_h[:, AX[ha]] = axes[ha]
        P_v = np.zeros((len(axes[va]), 3)); P_v[:, AX[va]] = axes[va]
        c = vm.project(P_h)[0] - 0.5; r = vm.project(P_v)[1] - 0.5         # pixel centres
        C, R = np.meshgrid(c, r, indexing="ij")
        s = ndimage.map_coordinates(d2, [R.ravel(), C.ravel()], order=1, mode="nearest").reshape(C.shape)
        s = s.astype(np.float32)                                            # indexed [h, v]
        if (ha, va) == ("x", "z"): e = s[:, None, :]
        elif (ha, va) == ("y", "z"): e = s[None, :, :]
        else: e = s[:, :, None]
        if ignore is not None and v in ignore:
            e = np.where(ignore[v], np.float32(-1e3), np.broadcast_to(e, shape))
        out = e if out is None else np.maximum(out, e)
        k = "side" if v == "side" else "top" if v == "top" else "front"
        by_dir[k] = e if k not in by_dir else np.maximum(by_dir[k], e)
    if not second: return np.broadcast_to(out, shape)
    d = [np.broadcast_to(x, shape) for x in by_dir.values()]
    if len(d) < 2: return np.broadcast_to(out, shape), np.full(shape, -1e3, np.float32)
    s2 = np.minimum(d[0], d[1]) if len(d) == 2 else np.maximum(np.maximum(np.minimum(d[0], d[1]),
                                                                          np.minimum(d[0], d[2])), np.minimum(d[1], d[2]))
    return np.broadcast_to(out, shape), s2


def field_normals(field, V, origin, voxel):
    """Unit normals from the gradient of the smooth distance field (not from the mesh facets), so the shading does not
    show the faint terraces that marching cubes leaves on gently sloping surfaces."""
    g = np.gradient(field, voxel)
    idx = ((V - origin) / voxel).T
    N = np.stack([ndimage.map_coordinates(gi, idx, order=1, mode="nearest") for gi in g], 1)
    return N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)


def keep_main_pieces(V, F, min_share=0.02):
    """Drop loose fragments: mesh pieces with under min_share of the largest piece's triangles."""
    from scipy.sparse.csgraph import connected_components
    n = len(V); e = np.r_[F[:, [0, 1]], F[:, [1, 2]]]
    g = sparse.coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n))
    _, lab = connected_components(g, directed=False)
    fl = lab[F[:, 0]]; counts = np.bincount(fl)
    keep = counts[fl] >= min_share * counts.max()
    used = np.unique(F[keep]); remap = -np.ones(n, np.int64); remap[used] = np.arange(len(used))
    dropped = counts[counts < min_share * counts.max()]
    keep_main_pieces.biggest_dropped = float(dropped.max() / counts.max()) if len(dropped) else 0.0
    return V[used], remap[F[keep]], int((counts >= min_share * counts.max()).sum()), int(len(counts))


TRUNK_THICK = 0.06       # a part at least this thick (share of the animal's largest size) belongs to the trunk
TRUNK_SIGMA = 0.035      # smoothing scale of the trunk (share of the animal's largest size)


def fair_trunk(parts, P, blk, pid, size, voxel):
    """Smooth the trunk: the thick parts (body, belly, chest, neck, head) as one surface. Several ellipsoids stacked
    along a body never line up exactly: where a lower one is wider than the one above, the outline swells, pinches
    in and swells again, and that prints a ring round the animal however the joins are blended. A sculptor would
    smooth such a trunk as one form. So the thick parts' combined distance field is blurred at 3.5% of the animal's
    size (a dip several centimetres long fills in), the shrinking that blurring causes is added back, and the result
    is used wherever one of them is the nearest surface. Thin parts (beaks, flippers, ears, legs, toes, claws, tails) are
    left exactly as written."""
    import parts as PT
    big_size = max(size["width"], size["length"], size["height"])
    def slimmest(p):                                         # a tapering part counts by its thin end: a thigh
        if p["type"] == "capsule": return float(min(p["ra"], p["rb"]))   # narrowing to a knee is a limb
        if p["type"] == "chain": return float(p["joints"][:, 3].min())
        if p["type"] == "loft": return PT.thinnest(p)
        return PT.thinnest(p)
    trunk = [i for i, p in enumerate(parts) if slimmest(p) >= TRUNK_THICK * big_size]
    if not trunk: return blk
    sigma = min(TRUNK_SIGMA * big_size, min(slimmest(parts[i]) for i in trunk) / 3) / voxel   # never eats a part
    if len(trunk) < 2 or sigma < 1: return blk
    d = PT.sdf([parts[i] for i in trunk], P).reshape(blk.shape).astype(np.float32)
    # Blurring a distance field moves a curved surface inwards by sigma^2/2 times its curvature (a head of radius R by
    # sigma^2/R); add that back, measured on a coarser blur so that it follows the overall form, not the dips.
    smooth = ndimage.gaussian_filter(d, sigma) - 0.5 * sigma ** 2 * ndimage.gaussian_laplace(d, 2 * sigma)
    w = ndimage.gaussian_filter(np.isin(pid, trunk).astype(np.float32), 1.5)   # soft edge where thin parts take over
    return blk + w * (smooth - d)


def disagreeing_views(parts, maps, axes, skip, blk, pid, size, voxel, rel=0.025, share=0.03):
    """{part index: views} where one view alone would cut deep into a part that the other viewing directions draw
    whole: more than `share` of the part's surface lies over 2.5% of the animal's size outside that view's outline
    while inside the others'. That view is drawn at other proportions or in another pose there (a top view with the
    rump 15 cm short), so it is ignored for that part, as the part's ignore_views would; trimming to it would slice
    a flat face into the body. Only the top and back views are judged this way: the front and side views set the
    animal's scale, and a part sticking out of them is too big. Front and back count as one direction."""
    deep = rel * max(size["width"], size["length"], size["height"])
    surf = np.abs(blk) < 1.5 * voxel
    e = {v: np.broadcast_to(hull_distance({v: maps[v]}, axes), blk.shape) for v in maps if v not in skip}
    dirs = {"front": ("front", "back"), "back": ("front", "back"), "side": ("side",), "top": ("top",)}
    out = {}
    for i in range(len(parts)):
        mine = surf & (pid == i); n = int(mine.sum())
        if n < 50: continue
        for v in e:
            if v not in ("top", "back"): continue          # front and side set the scale: their cuts are trusted
            others = [e[u][mine] for u in e if u not in dirs[v]]
            if not others: continue
            inside_others = np.max(others, 0) <= 0.3 * deep
            if ((e[v][mine] > deep) & inside_others).sum() > share * n:
                out.setdefault(i, []).append(v)
    return out


FINE_VOXELS = 3.0        # a chain thinner than this many build voxels somewhere is built on a finer grid
FINE_STEP = 3            # ... that many times finer
FINE_MAX_POINTS = 3_000_000


def fine_parts(parts, voxel):
    """Indices of the parts built on a finer grid: thin chains (a tail strand, a leg down to its pastern), parts
    marked "fine", and whatever hangs from them alone (the tuft at the end of a tail, a hoof under a thin leg), which
    on the coarse grid would be left floating once the thin part is taken out. Never the biggest part."""
    import parts as PT
    fine = {i for i, p in enumerate(parts)
            if p.get("fine") or (p["type"] == "chain" and p["joints"][:, 3].min() < FINE_VOXELS * voxel)}
    fine.discard(int(np.argmax([PT.volume(p) for p in parts])))
    changed = bool(fine)
    while changed:
        changed = False
        for i, p in enumerate(parts):
            if i in fine: continue
            lo, hi = PT.bounds(p); g = [np.linspace(lo[k], hi[k], 20) for k in range(3)]
            G = np.stack(np.meshgrid(*g, indexing="ij"), -1).reshape(-1, 3)
            cell = float((hi - lo).max()) / 19
            S = G[np.abs(PT.sdf_part(p, G)) < max(cell, voxel)]          # points on its surface
            if not len(S): continue
            def touch(js): return bool(js) and float(np.min([PT.sdf_part(parts[j], S) for j in js])) < voxel
            if touch(sorted(fine)) and not touch([j for j in range(len(parts)) if j != i and j not in fine]):
                fine.add(i); changed = True
    return sorted(fine)


def build_fine(maps, axes, voxel, field, parts, fine, skip, tol_max, occ, ignore):
    """Build the fine parts on their own grids (one box per group of touching parts) and join them to the body.
    In each box the shape is the fine parts, trimmed to the outlines at the fine resolution, smoothly joined
    (blend) onto the body as the coarse build made it, sunk half a coarse voxel so that the edge of the fillet lies
    just under the body's own surface. Only the fine parts and their fillets are kept from that mesh; the body
    surface in the box comes from the coarse mesh. occ and ignore (coarse grids) are updated in place so texturing
    sees the fine parts. Returns (meshes [(V, F, N)], untrimmed part names, largest dropped share)."""
    import parts as PT
    fp = [parts[i] for i in fine]
    kmax = max([max(p["blend"], p.get("root_blend", 0)) for p in fp] + [voxel])
    margin = 1.5 * kmax + 2 * voxel
    boxes = []                                       # one box per instance (mirror copies apart), merged on overlap
    for p in fp:
        for q in PT.instances(p):
            lo, hi = PT.bounds(dict(q, mirror=False)); boxes.append([lo - margin, hi + margin])
    merged = True
    while merged:
        merged = False
        for a in range(len(boxes)):
            for b in range(a + 1, len(boxes)):
                if np.all(boxes[a][0] <= boxes[b][1]) and np.all(boxes[b][0] <= boxes[a][1]):
                    boxes[a] = [np.minimum(boxes[a][0], boxes[b][0]), np.maximum(boxes[a][1], boxes[b][1])]
                    del boxes[b]; merged = True; break
            if merged: break
    origin = np.array([axes["x"][0], axes["y"][0], axes["z"][0]])
    meshes, untrimmed, dropped = [], set(), 0.0
    for lo, hi in boxes:
        vf = max(voxel / FINE_STEP, float(np.prod(hi - lo) / FINE_MAX_POINTS) ** (1 / 3))
        ax = {a: np.arange(lo[k], hi[k] + vf, vf) for k, a in enumerate("xyz")}
        X, Y, Z = np.meshgrid(ax["x"], ax["y"], ax["z"], indexing="ij"); shape = X.shape
        P = np.c_[X.ravel(), Y.ravel(), Z.ravel()]; del X, Y, Z
        here = [p for p in fp if np.all(PT.bounds(p)[0] <= hi) and np.all(lo <= PT.bounds(p)[1])]
        e, pid = PT.sdf_with_parts(here, P)
        e = e.reshape(shape).astype(np.float32); pid = pid.reshape(shape)
        dm = ndimage.map_coordinates(field, ((P - origin) / voxel).T, order=1, mode="nearest").reshape(shape)
        del P
        ign = {}
        for v in VIEWS:
            ids = [j for j, p in enumerate(here) if v in p.get("ignore", [])]
            if ids: ign[v] = np.isin(pid, ids)
        def tol_of(p):                               # as for the coarse parts: 15% of its typical thickness
            t = float(np.median(p["joints"][:, 3])) if p["type"] == "chain" else PT.thinnest(p)
            return min(tol_max, 0.15 * t)
        hd = hull_distance(maps, ax, skip, ign) - np.array([tol_of(p) for p in here], np.float32)[pid]
        k = 2 * vf
        h = np.clip(k - np.abs(e - hd), 0, None) / k
        ft = np.maximum(e, hd) + h * h * k / 4; del hd, h
        for j, p in enumerate(here):                 # trimming shaves, it never deletes (as for the coarse parts)
            mine = (pid == j) & (e < 0); n = int(mine.sum())
            if n and (ft[mine] < 0).sum() < 0.5 * n:
                untrimmed.add(p["name"]); keep = ndimage.binary_dilation(pid == j, iterations=1)
                ft = np.where(keep, np.minimum(ft, e), ft)
        kb = max([max(p["blend"], p.get("root_blend", 0)) for p in here] + [2 * vf])
        d = PT.smin(dm + 0.5 * voxel, ft, kb).astype(np.float32)
        if not (d < 0).any(): continue
        verts, faces, _, _ = measure.marching_cubes(np.pad(d, 1, constant_values=4 * voxel), 0.0)
        o = np.array([ax["x"][0], ax["y"][0], ax["z"][0]])
        V = (verts - 1) * vf + o; F = faces[:, ::-1].astype(np.int64)
        c = (V[F].mean(1) - o) / vf
        near = ndimage.map_coordinates(ft, c.T, order=1, mode="nearest") < kb + vf   # the fine parts and fillets,
        F = F[near]                                                                  # not the body under them
        if not len(F): continue
        used = np.unique(F); remap = -np.ones(len(V), np.int64); remap[used] = np.arange(len(used))
        V, F = V[used], remap[F]
        V, F, _, _ = keep_main_pieces(V, F)
        dropped = max(dropped, keep_main_pieces.biggest_dropped)
        meshes.append((V, F, field_normals(d, V, o, vf)))
        # the coarse grids that texturing reads: where the fine shape is, and which views ignore it there
        sl = tuple(slice(np.searchsorted(axes[a], lo[q]), np.searchsorted(axes[a], hi[q])) for q, a in enumerate("xyz"))
        G = np.meshgrid(*[axes[a][sl[q]] for q, a in enumerate("xyz")], indexing="ij")
        idx = [(G[q] - o[q]) / vf for q in range(3)]
        inside = ndimage.map_coordinates(ft, idx, order=1, mode="nearest") < 0
        occ[sl] |= inside
        near_pid = ndimage.map_coordinates(pid, idx, order=0, mode="nearest")
        for v in VIEWS:
            ids = [j for j, p in enumerate(here) if v in p.get("ignore", [])]
            if ids:
                ignore.setdefault(v, np.zeros(occ.shape, bool))[sl] |= inside & np.isin(near_pid, ids)
    return meshes, sorted(untrimmed), dropped


def build_shape_parts(refs, parts, res=280, grow=0.0, blur=1.0, smooth_iters=8, skip=()):
    """Blockout first, then trim where it sticks out of the outlines.
    shape = blockout (optionally grown by `grow`) intersected with the visual hull, with the cut edges rounded.
    The blockout decides what exists and gives the surface its shape; the hull only shaves off what pokes outside an
    outline. Growing makes the outlines match more closely but lets the flat hull surfaces take over (a body grown by
    1.4 cm came out boxy), so keep grow at 0 and fix gaps by adding or adjusting parts."""
    import parts as PT
    size, _ = load_subject(refs)
    sils, notes = {}, {}
    for v in VIEWS: sils[v], notes[v] = silhouette(refs, v)
    maps = view_maps(refs, size, sils)
    axes, voxel = make_grid(maps, size, res)
    grow = grow or 0.0
    hull = visual_hull(maps, axes, skip)
    all_parts = parts
    fine = fine_parts(parts, voxel)                  # built on their own finer grid, after the body
    parts = [p for i, p in enumerate(parts) if i not in fine]
    X, Y, Z = np.meshgrid(axes["x"], axes["y"], axes["z"], indexing="ij")
    P = np.c_[X.ravel(), Y.ravel(), Z.ravel()]
    blk, pid = PT.sdf_with_parts(parts, P, grow=grow)
    blk = blk.reshape(hull.shape).astype(np.float32); pid = pid.reshape(hull.shape)
    blk = fair_trunk(parts, P, blk, pid, size, voxel)
    del P, X, Y, Z
    auto = disagreeing_views(parts, maps, axes, skip, blk, pid, size, voxel)
    ignore = {}
    for v in VIEWS:
        ids = [i for i, p in enumerate(parts) if v in p.get("ignore", []) or v in auto.get(i, ())]
        if ids: ignore[v] = np.isin(pid, ids)
    # Trim only where the blockout sticks out by more than 1% of the animal's size: drawn outlines wobble (feather tufts,
    # fur), and trimming right to them copies the wobble across the surface as ridges. Thin parts (a beak, toes, a
    # flipper) are trimmed closer, to 15% of their thickness, or a toe drawn 1 cm thick could stay 2 cm thick.
    tol_max = 0.01 * max(size["width"], size["length"], size["height"])
    tol_part = np.array([min(tol_max, 0.15 * PT.thinnest(p)) for p in parts], np.float32)
    tol = ndimage.gaussian_filter(tol_part[pid], 2.0)
    hd = hull_distance(maps, axes, skip, ignore) - tol
    del tol
    k = 2 * voxel                                             # rounded cut instead of a sharp crease
    h = np.clip(k - np.abs(blk - hd), 0, None) / k
    field = np.maximum(blk, hd) + h * h * k / 4
    del hd, h
    # Trimming shaves parts, it never deletes them: a part that would lose most of its volume is placed off its
    # drawing (an antler tine a few centimetres from where one view draws it), and the animal looks wrong without
    # it. Such a part is kept as blocked out, and reported, so the agent can move it onto the drawing.
    protected = []
    for i, p in enumerate(parts):
        mine = (pid == i) & (blk < 0)
        n = int(mine.sum())
        if n and (field[mine] < 0).sum() < 0.5 * n:
            protected.append(i)
    if protected:
        keep = ndimage.binary_dilation(np.isin(pid, protected), iterations=1)
        field = np.where(keep, np.minimum(field, blk), field)
    del pid
    if blur > 0: field = ndimage.gaussian_filter(field, blur)
    vol = np.pad(field, 1, constant_values=voxel * 4)
    verts, faces, _, _ = measure.marching_cubes(vol, 0.0)
    V = (verts - 1) * voxel + np.array([axes["x"][0], axes["y"][0], axes["z"][0]])
    F = faces[:, ::-1].astype(np.int64)
    V, F, kept, pieces = keep_main_pieces(V, F)
    if smooth_iters: V = taubin(V, F, smooth_iters)
    dropped = keep_main_pieces.biggest_dropped
    origin = np.array([axes["x"][0], axes["y"][0], axes["z"][0]])
    N = field_normals(field, V, origin, voxel)
    occ = field < 0
    untrimmed = [parts[i]["name"] for i in protected]
    if fine:
        meshes, fine_untrimmed, fine_dropped = build_fine(maps, axes, voxel, field, all_parts, fine, skip, tol_max,
                                                          occ, ignore)
        for Vf, Ff, Nf in meshes:
            F = np.r_[F, Ff + len(V)]; V = np.r_[V, Vf]; N = np.r_[N, Nf]
        untrimmed += fine_untrimmed; dropped = max(dropped, fine_dropped)
    return dict(size=size, maps=maps, notes=notes, axes=axes, voxel=voxel, hull=hull, occ=occ, V=V, F=F, N=N,
                grow=grow, pieces=(kept, pieces), parts=all_parts, ignored_space=ignore,
                untrimmed=untrimmed, dropped_piece=dropped, fine=[all_parts[i]["name"] for i in fine],
                auto_ignored={parts[i]["name"]: list(v) for i, v in auto.items()})


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("refs"); ap.add_argument("out")
    ap.add_argument("--res", type=int, default=280); ap.add_argument("--round", type=float, default=2.0)
    ap.add_argument("--smooth", type=int, default=12); ap.add_argument("--blur", type=float, default=1.5)
    ap.add_argument("--masks", action="store_true")
    a = ap.parse_args()
    S = build_shape(a.refs, a.res, a.round, a.masks, a.smooth, a.blur)
    write_glb(a.out, recentre(S["V"]), S["F"])
    print(f"voxel {S['voxel'] * 1000:.2f} mm, grid {S['occ'].shape}, hull {S['hull'].sum()} -> rounded {S['occ'].sum()} voxels,"
          f" {len(S['F'])} triangles")


if __name__ == "__main__":
    main()
