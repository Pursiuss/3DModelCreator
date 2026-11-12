"""UV unwrap from the blockout, the way an artist unwraps simple shapes, and baking colours into that texture.

Every triangle belongs to the blockout part it lies on (each side of a mirrored part separately), and each part is
unrolled along its own shape:
- capsule (limb, neck, beak, toe): unrolled like a sleeve: across = around the tube, along = down the tube, with the
  rounded ends continuing the strip;
- paddle (flipper, wing, fin, ear): unrolled like a flat sleeve: across = over its outer face from one long edge to the
  other, round that edge and back over its inner face (an angle round its middle line would squeeze each whole face
  into a strip as wide as the plate is thick, too few pixels for a flipper's white trailing edge);
- chain (a limb or tail of several segments): the same sleeve, following the bends from joint to joint;
- loft (a torso): a sleeve slice by slice: along = down the body through the slices, across = around each slice,
  with the cut underneath;
- ellipsoid (body, head, flipper): a sinusoidal map, like a world map that does not stretch near the poles: along
  = from end to end along its longest axis, across = around it, shrinking towards the ends;
- box: one flat piece per face.
Distances are real arc lengths in metres, so the texture has the same sharpness everywhere and nothing is
stretched. The cut where the map wraps round is put on the side least seen: the back, or underneath for parts that
run front to back. Pieces are packed into one square image at a single scale.
"""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import parts as PT

SEAM_DIRS = (np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, -1.0]))   # back, else underneath


def _seam_dir(axis):
    for s in SEAM_DIRS:
        p = s - (s @ axis) * axis
        if np.linalg.norm(p) > 0.5: return p / np.linalg.norm(p)
    p = np.array([1.0, 0, 0]) - axis[0] * axis
    return p / np.linalg.norm(p)


def _arc_table(a, b, n=2048):
    """Arc length along the ellipse (a cos t, b sin t) for t in [-pi, pi], as a lookup table."""
    t = np.linspace(-np.pi, np.pi, n)
    speed = np.sqrt((a * np.sin(t)) ** 2 + (b * np.cos(t)) ** 2)
    A = np.concatenate([[0], np.cumsum(0.5 * (speed[1:] + speed[:-1]) * np.diff(t))])
    return t, A - np.interp(0.0, t, A), A[-1]


def _arc(table, t):
    """Arc length at angle t (any real number; whole turns add whole perimeters)."""
    ts, A, per = table
    turns = np.floor((t + np.pi) / (2 * np.pi))
    return np.interp(t - turns * 2 * np.pi, ts, A) + turns * per


class Unroller:
    """Maps points on one part instance to (angle around, distance along); angle 0 faces away from the seam."""

    def __init__(self, inst):
        self.p = inst; t = inst["type"]; self.kind = t
        if t == "loft":
            D = PT.loft_slices(inst); self.Ys, self.D = D[:, 1], D
            self.cl = np.r_[0, np.cumsum(np.linalg.norm(np.diff(D[:, :3], axis=0), axis=1))]
            self.L = float(self.cl[-1]); self.ra, self.rb = float(D[0, 3:].min()), float(D[-1, 3:].min())
        elif t == "chain":
            J = PT.joints(inst); self.ra, self.rb = float(J[0, 3]), float(J[-1, 3])
            d = np.diff(J[:, :3], axis=0); ln = np.maximum(np.linalg.norm(d, axis=1), 1e-6)
            self.A, self.len = J[:-1, :3], ln; self.cum = np.r_[0, np.cumsum(ln)[:-1]]; self.L = float(ln.sum())
            self.axs = d / ln[:, None]; e1 = -_seam_dir(self.axs[0]); E1 = []
            for ax in self.axs:                                           # carry the seam along the bends
                e1 = e1 - (e1 @ ax) * ax
                e1 = e1 / np.linalg.norm(e1) if np.linalg.norm(e1) > 1e-6 else -_seam_dir(ax)
                E1.append(e1)
            self.E1 = np.array(E1); self.E2 = np.cross(self.axs, self.E1)
            self.segs = PT.segments(inst)
        elif t == "paddle":
            self.kind = "plate"; a, b = inst["a"], inst["b"]; L = float(np.linalg.norm(b - a))
            self.a, self.L = a, max(L, 1e-6); self.ra, self.rb = float(inst["ra"]), float(inst["rb"])
            self.ax, self.w, n = PT.paddle_frame(inst)
            self.n = n if (abs(n[0]) < 0.5 or n[0] * a[0] >= 0) else -n  # (sideways plates: + away from the body)
            self.R = max(self.ra, self.rb, float(np.max(inst.get("widest", [0, 0])[1:]))) + float(inst["thick"])
            self.bend = float(inst["bend"])
        elif t in PT.TUBES:
            self.kind = t = "capsule"
            a, b = inst["a"], inst["b"]; L = float(np.linalg.norm(b - a))
            self.a, self.L = a, max(L, 1e-6); self.ra, self.rb = float(inst["ra"]), float(inst["rb"])
            self.ax = (b - a) / self.L if L > 1e-9 else np.array([0, 0, 1.0])
            sd = _seam_dir(self.ax); self.e1 = -sd; self.e2 = np.cross(self.ax, self.e1)
        elif t == "ellipsoid":
            R = inst.get("_R"); R = PT.rot(inst["rotate"]) if R is None else R
            self.R, self.c = R, inst["center"]; r = np.abs(inst["radii"]); self.r = r
            k = int(np.argmax(r)); i, j = [q for q in range(3) if q != k]; self.k, self.i, self.j = k, i, j
            sd = _seam_dir(R[:, k]) @ R                                   # seam direction in the part's frame
            self.t_seam = np.arctan2(sd[j] / r[j], sd[i] / r[i])
            self.ring = _arc_table(r[i], r[j])
            self.req = 0.5 * (r[i] + r[j])
            self.merid = _arc_table(self.req, r[k])
        else:
            R = inst.get("_R"); R = PT.rot(inst["rotate"]) if R is None else R
            self.R, self.c, self.h = R, inst["center"], np.abs(inst["half"])

    def angles(self, X):
        """(angle around the part, position along it, face id for boxes). Angles in (-pi, pi]."""
        if self.kind == "plate":                                          # lap: outer face, edge, inner face
            q = X - self.a; s = q @ self.ax; tt = np.clip(s / self.L, 0, 1)
            across = q @ self.w - self.bend * 4 * tt * (1 - tt); up = q @ self.n; R = self.R
            lap = np.where(up >= 0, R - across, 3 * R + across)           # 0 .. 4R
            return lap / (4 * R) * 2 * np.pi - np.pi, s, np.zeros(len(X), int), np.full(len(X), 4 * R / (2 * np.pi))
        if self.kind == "capsule":
            w = X - self.a; s = w @ self.ax; w = w - s[:, None] * self.ax
            th = np.arctan2(w @ self.e2, w @ self.e1)
            return th, s, np.zeros(len(X), int), np.linalg.norm(w, axis=1)
        if self.kind == "loft":
            y = X[:, 1]; xc = np.interp(y, self.Ys, self.D[:, 0]); zc = np.interp(y, self.Ys, self.D[:, 2])
            s = np.interp(y, self.Ys, self.cl)
            s = np.where(y < self.Ys[0], y - self.Ys[0], np.where(y > self.Ys[-1], self.L + y - self.Ys[-1], s))
            u, v = X[:, 0] - xc, X[:, 2] - zc                             # angle 0 on top, the cut underneath
            return np.arctan2(u, v), s, np.zeros(len(X), int), np.hypot(u, v)
        if self.kind == "chain":
            j = np.argmin([PT.sdf_one(c, X) for c in self.segs], 0); n = len(self.segs)
            w = X - self.A[j]; s = (w * self.axs[j]).sum(1)
            s = np.where(j > 0, np.maximum(s, 0), s); s = np.where(j < n - 1, np.minimum(s, self.len[j]), s)
            w = w - s[:, None] * self.axs[j]
            th = np.arctan2((w * self.E2[j]).sum(1), (w * self.E1[j]).sum(1))
            return th, self.cum[j] + s, np.zeros(len(X), int), np.linalg.norm(w, axis=1)
        if self.kind == "ellipsoid":
            Q = (X - self.c) @ self.R; q = Q / self.r
            t = np.arctan2(q[:, self.j], q[:, self.i]) - self.t_seam - np.pi
            t = (t + np.pi) % (2 * np.pi) - np.pi
            phi = np.arctan2(q[:, self.k], np.hypot(q[:, self.i], q[:, self.j]))
            return t, phi, np.zeros(len(X), int), None
        Q = (X - self.c) @ self.R; q = Q / self.h
        f = np.argmax(np.abs(q), 1) * 2 + (np.take_along_axis(q, np.argmax(np.abs(q), 1)[:, None], 1)[:, 0] > 0)
        return None, Q, f, None

    def to_metres(self, th, along, rho):
        """Unrolled coordinates in metres from angles (th may have been unwrapped past +-pi); rho = distance from
        the axis (capsules only)."""
        if self.kind in ("capsule", "chain", "loft", "plate"):
            s = along
            u = th * rho
            v = s.copy()
            lo = s < 0; hi = s > self.L
            v[lo] = -self.ra * np.arctan2(-s[lo], rho[lo])
            v[hi] = self.L + self.rb * np.arctan2(s[hi] - self.L, rho[hi])
            return np.c_[u, v]
        if self.kind == "ellipsoid":
            phi = along
            return np.c_[_arc(self.ring, th) * np.cos(phi), _arc(self.merid, phi)]
        raise ValueError


def instances(parts):
    """All part instances (mirror copies separately): list of (part index, side, instance dict)."""
    out = []
    for i, p in enumerate(parts):
        for s, inst in enumerate(PT.instances(p)): out.append((i, s, inst))
    return out


def unwrap(V, F, parts, pid_face, cen):
    """Per triangle corner, unrolled coordinates in metres, and an island id per triangle."""
    insts = instances(parts)
    key = {(i, s): n for n, (i, s, _) in enumerate(insts)}
    side = np.where(np.array([parts[i]["mirror"] for i in pid_face]) & (cen[:, 0] < 0), 1, 0)
    inst_id = np.array([key[(i, s)] for i, s in zip(pid_face, side)])
    uvm = np.zeros((len(F), 3, 2)); island = np.zeros(len(F), int)
    next_island = 0
    for n, (_, _, inst) in enumerate(insts):
        sel = np.nonzero(inst_id == n)[0]
        if not len(sel): continue
        un = Unroller(inst); X = V[F[sel]].reshape(-1, 3)
        th, along, face, extra = un.angles(X)
        if un.kind == "box":
            Q = along.reshape(-1, 3, 3); fc = face.reshape(-1, 3)
            tf = np.array([np.bincount(r, minlength=6).argmax() for r in fc])  # one face per triangle
            ax = tf // 2
            others = np.array([[1, 2], [0, 2], [0, 1]])[ax]
            for c in range(3):
                uvm[sel, c, 0] = Q[np.arange(len(sel)), c, others[:, 0]]
                uvm[sel, c, 1] = Q[np.arange(len(sel)), c, others[:, 1]]
            island[sel] = next_island + tf; next_island += 6
            continue
        th = th.reshape(-1, 3)
        span = th.max(1) - th.min(1)
        wrap = span > np.pi                                                 # triangle straddles the cut
        th = np.where(wrap[:, None] & (th < 0), th + 2 * np.pi, th)
        th = th.reshape(-1)
        uvm[sel] = un.to_metres(th, along, extra).reshape(-1, 3, 2)
        island[sel] = next_island; next_island += 1
    _, island = np.unique(island, return_inverse=True)
    return uvm, island


def pack(uvm, island, size=2048, pad=6):
    """Lay the islands out on one square image at one scale (shelf packing, tallest first).
    Returns per-corner pixel coordinates and the scale (pixels per metre)."""
    n = island.max() + 1
    lo = np.full((n, 2), np.inf); hi = np.full((n, 2), -np.inf)
    np.minimum.at(lo, island, uvm.min(1)); np.maximum.at(hi, island, uvm.max(1))
    ext = hi - lo
    order = np.argsort(-ext[:, 1])

    def place(scale):
        pos = np.zeros((n, 2)); x = y = row_h = 0.0
        for k in order:
            w, h = ext[k] * scale + 2 * pad
            if x + w > size:
                x, y, row_h = 0.0, y + row_h, 0.0
            if w > size: return None
            pos[k] = (x + pad, y + pad); x += w; row_h = max(row_h, h)
        return pos if y + row_h <= size else None

    lo_s, hi_s = 1.0, 1e5
    for _ in range(40):                                                  # largest scale that fits
        mid = np.sqrt(lo_s * hi_s)
        if place(mid) is None: hi_s = mid
        else: lo_s = mid
    scale = lo_s; pos = place(scale)
    px = (uvm - lo[island][:, None]) * scale + pos[island][:, None]
    return px, scale


def raster_ids(px, size):
    """Which triangle covers each texel (-1 = none)."""
    img = Image.new("I", (size, size), 0); d = ImageDraw.Draw(img)
    for t in range(len(px)):
        pts = [tuple(p) for p in px[t]]
        d.polygon(pts, fill=t + 1, outline=t + 1)
    return np.asarray(img, np.int64) - 1


def barycentric(px, tid, yy, xx):
    A = px[tid]; p = np.c_[xx + 0.5, yy + 0.5]
    v0, v1, v2 = A[:, 1] - A[:, 0], A[:, 2] - A[:, 0], p - A[:, 0]
    den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
    den = np.where(np.abs(den) < 1e-12, 1e-12, den)
    w1 = (v2[:, 0] * v1[:, 1] - v1[:, 0] * v2[:, 1]) / den
    w2 = (v0[:, 0] * v2[:, 1] - v2[:, 0] * v0[:, 1]) / den
    w = np.clip(np.c_[1 - w1 - w2, w1, w2], 0, 1)
    return w / np.maximum(w.sum(1, keepdims=True), 1e-12)


def dilate(img, filled):
    """Fill every empty texel with the nearest filled one, so filtering at island edges never picks up a gap."""
    _, (iy, ix) = ndimage.distance_transform_edt(~filled, return_indices=True)
    return img[iy, ix]


def split_vertices(V, F, N, px, island, size):
    """Mesh with vertices split where the UV changes (island edges, the wrap cut). Returns V, F, N, uv (0..1)."""
    corner_v = F.reshape(-1); corner_uv = px.reshape(-1, 2) / size
    key = np.c_[corner_v, np.repeat(island, 3), np.round(corner_uv * 1e5).astype(np.int64)]
    _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inv = inv.reshape(-1)
    return V[corner_v[first]], inv.reshape(-1, 3), N[corner_v[first]], corner_uv[first]
