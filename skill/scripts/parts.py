"""Blockout parts: simple solids described in a JSON file, as signed distance functions (negative = inside).

Coordinates are the model's: metres, z up from the ground, x across the animal (image right in the front view = +x,
which is the animal's own left), y along it with the nose towards -y (the front camera sees the face).

parts.json:
{"parts": [
  {"name": "body",    "type": "ellipsoid", "center": [0, 0.01, 0.33], "radii": [0.11, 0.12, 0.27], "rotate": [0, 0, 0]},
  {"name": "beak",    "type": "capsule",   "a": [0, -0.06, 0.6], "b": [0, -0.12, 0.59], "ra": 0.015, "rb": 0.004},
  {"name": "flipper", "type": "paddle",    "a": [0.08, 0.0, 0.47], "b": [0.115, 0.02, 0.2], "ra": 0.04, "rb": 0.01,
   "thick": 0.008, "normal": [1, 0, 0], "bend": 0.01, "mirror": true, "blend": 0.004, "root_blend": 0.03},
  {"name": "shell",   "type": "box",       "center": [0, 0, 0.1], "half": [0.1, 0.15, 0.05], "round": 0.03},
  {"name": "tail",    "type": "chain",     "joints": [[0, 0.12, 0.2, 0.02], [0, 0.18, 0.12, 0.012], [0, 0.2, 0.05, 0.03]]}
]}
chain: a limb, tail or neck grown joint by joint, the way an artist extrudes one: "joints" = [x, y, z, radius] from
the root (put it inside the part it grows from) to the tip, joined by round cones, so the segments always meet and
fitting moves a joint together with both segments that share it. "aspect" (default 1) flattens every segment's
cross-section as for a capsule. A chain thinner than about three build voxels somewhere (a tail strand, a leg's
pastern) is built on its own finer grid and joined on, so it cannot break off; "fine": true forces that.
loft: a torso built slice by slice, the way a modeller lofts one from blueprints: "stations" =
[x, y, z, half_width, half_height] from the front end to the back end (y increasing); each station is an upright
slice across the animal at that y, an ellipse half_width wide (x) and half_height tall (z) around (x, z), and a
smooth surface runs through the stations. Read each station's top and bottom straight off the side view at its y,
and its width off the top or front view: the back can slope, the belly tuck up, the chest be deep and narrow, all in
one part. "caps": [front, back] metres the ends round off beyond the first and last station (default 0: as far as
the end slice is thin). Not for necks or anything running steeply up or down: use a capsule or chain there.
paddle: a flat tapered plate from a to b (flippers, wings, fins, ears, flat tails): half-width ra at a narrowing to
rb at b, half-thickness "thick", flat faces turned towards "normal" (default [1, 0, 0]: facing sideways), and
"bend": metres the middle bows out sideways within the plate (a crescent flipper), default 0, and "curl":
metres the long edges curl back away from the "normal" side, so the plate wraps round the body it lies on, default 0.
Optional on every part: "mirror": true (adds a copy at -x), "blend": metres (smooth join into the parts before it;
default 0 = sharp), "root_blend" (capsules and paddles): a larger blend used only near the root end a, so a
free-hanging part flows out of the body at its root and stands apart from it everywhere else, "colour": the
part is painted in one colour: "#rrggbb", or "drawn" for the colour the pictures mostly show on it (claws, toes,
boots, a shell: parts that are one colour, so they cannot pick up a neighbour's colour from a misaligned drawing), "fit": false (keep it exactly as written when fitting), "ignore_views": ["back", ...] (a
reference view that draws this part wrongly: it is not used to fit, trim or texture this part).
rotate = degrees about x, then y, then z (applied in that order, about the part's centre).
A part that is not mirrored and written exactly on the centre line (x = 0) stays on it: the fitter never moves it
sideways or turns it about y or z, so beaks, snouts and tails stay straight.
"""
VIEW_NAMES = ("front", "back", "side", "top")
import json, re
import numpy as np

TYPES = {"ellipsoid": ["center", "radii", "rotate"], "capsule": ["a", "b", "ra", "rb", "aspect", "droop"],
         "paddle": ["a", "b", "ra", "rb", "thick", "normal", "bend", "curl"], "box": ["center", "half", "rotate", "round"],
         "chain": ["joints", "aspect"], "loft": ["stations", "caps"]}
DEFAULTS = {"rotate": [0, 0, 0], "round": 0.0, "normal": [1, 0, 0], "bend": 0.0, "curl": 0.0, "aspect": 1.0,
            "droop": 0.0, "caps": [0.0, 0.0]}
TUBES = ("capsule", "paddle")                       # parts running from a root a to a tip b
LONG = TUBES + ("chain",)                           # parts with a root end and a tip end (see ends())


def rot(deg):
    ax, ay, az = np.radians(deg)
    Rx = np.array([[1, 0, 0], [0, np.cos(ax), -np.sin(ax)], [0, np.sin(ax), np.cos(ax)]])
    Ry = np.array([[np.cos(ay), 0, np.sin(ay)], [0, 1, 0], [-np.sin(ay), 0, np.cos(ay)]])
    Rz = np.array([[np.cos(az), -np.sin(az), 0], [np.sin(az), np.cos(az), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def load(path):
    spec = json.load(open(path))
    parts = spec["parts"] if isinstance(spec, dict) else spec
    out = []
    for p in parts:
        t = p.get("type")
        if t not in TYPES: raise SystemExit(f"part {p.get('name')}: unknown type {t!r} (use {', '.join(TYPES)})")
        q = {"name": p.get("name", t), "type": t, "mirror": bool(p.get("mirror", False)),
             "blend": float(p.get("blend", 0.0)), "fit": p.get("fit", True),
             "root_blend": float(p.get("root_blend", 0.0)), "colour": p.get("colour"),
             "ignore": [str(v) for v in p.get("ignore_views", [])], "fine": bool(p.get("fine", False))}
        bad = [v for v in q["ignore"] if v not in VIEW_NAMES]
        if bad: raise SystemExit(f"part {q['name']}: ignore_views {bad} (use {', '.join(VIEW_NAMES)})")
        for k in TYPES[t]:
            if k not in p and k not in DEFAULTS: raise SystemExit(f"part {q['name']}: missing {k!r}")
            q[k] = np.array(p.get(k, DEFAULTS.get(k)), float)
        if t == "chain" and (q["joints"].ndim != 2 or q["joints"].shape[1] != 4 or len(q["joints"]) < 2):
            raise SystemExit(f"part {q['name']}: joints must be at least two [x, y, z, radius] rows")
        if t == "loft" and (q["stations"].ndim != 2 or q["stations"].shape[1] != 5 or len(q["stations"]) < 2):
            raise SystemExit(f"part {q['name']}: stations must be at least two [x, y, z, half_width, half_height] rows")
        if t == "loft" and np.any(np.diff(q["stations"][:, 1]) <= 0):
            raise SystemExit(f"part {q['name']}: stations must run from the front end to the back end (y increasing)")
        out.append(q)
    return out


def save(parts, path):
    rows = []
    for p in parts:
        r = {"name": p["name"], "type": p["type"]}
        for k in TYPES[p["type"]]: r[k] = np.round(np.atleast_1d(p[k]), 4).tolist() if np.ndim(p[k]) else round(float(p[k]), 4)
        if p["mirror"]: r["mirror"] = True
        if p["blend"]: r["blend"] = round(p["blend"], 4)
        if p.get("root_blend"): r["root_blend"] = round(p["root_blend"], 4)
        if p.get("colour"): r["colour"] = p["colour"]
        if p["fit"] is not True: r["fit"] = p["fit"]
        if p.get("ignore"): r["ignore_views"] = p["ignore"]
        if p.get("fine"): r["fine"] = True
        rows.append(r)
    text = json.dumps({"parts": rows}, indent=1)
    text = re.sub(r"\[\s+([-\d.e,\s]+?)\s+\]", lambda m: "[" + ", ".join(m.group(1).split()).replace(",,", ",") + "]", text)
    open(path, "w").write(text)                       # number lists on one line: [0.1, -0.03, 1.2, 0.075]


def instances(p):
    """The part itself, plus its mirror image across x = 0 if requested."""
    yield p
    if p["mirror"]:
        m = dict(p); M = np.diag([-1.0, 1, 1])
        if p["type"] == "chain": m["joints"] = p["joints"] * [-1, 1, 1, 1]
        elif p["type"] == "loft": m["stations"] = p["stations"] * [-1, 1, 1, 1, 1]
        elif p["type"] in TUBES:
            m["a"] = p["a"] * [-1, 1, 1]; m["b"] = p["b"] * [-1, 1, 1]
            if p["type"] == "paddle":                # mirroring flips the frame's handedness: keep the bow's side
                m["normal"] = p["normal"] * [-1, 1, 1]; m["bend"] = -p["bend"]
        else:
            m["center"] = p["center"] * [-1, 1, 1]; m["_R"] = M @ rot(p["rotate"]) @ M
        yield m


def paddle_frame(p):
    """Unit vectors of a paddle: along (a to b), across its width, and its face normal."""
    u = p["b"] - p["a"]; u = u / max(np.linalg.norm(u), 1e-9)
    n = np.asarray(p["normal"], float); n = n - (n @ u) * u
    if np.linalg.norm(n) < 1e-6: n = np.cross(u, [0, 0, 1.0]) if abs(u[2]) < 0.9 else np.cross(u, [1.0, 0, 0])
    n = n / np.linalg.norm(n)
    return u, np.cross(n, u), n


def joints(p):
    """A chain's joints; for a loft, its stations as joints of the same cross-section area."""
    if p["type"] == "loft":
        S = p["stations"]; return np.c_[S[:, :3], np.sqrt(np.abs(S[:, 3] * S[:, 4]))]
    return p["joints"]


def segments(p):
    """A chain's segments (a loft's, roughly), as capsules from joint to joint."""
    J = joints(p)
    return [{"type": "capsule", "a": J[k, :3], "b": J[k + 1, :3], "ra": J[k, 3], "rb": J[k + 1, 3],
             "aspect": p.get("aspect", 1.0), "droop": 0.0} for k in range(len(J) - 1)]


def ends(p):
    """(root, tip, root radius, tip radius) of a capsule, paddle or chain."""
    if p["type"] == "chain": J = p["joints"]; return J[0, :3], J[-1, :3], float(J[0, 3]), float(J[-1, 3])
    return p["a"], p["b"], float(p["ra"]), float(p["rb"])


LOFT_STEPS = 8           # samples per span between two stations


def loft_slices(p):
    """The loft's stations with smooth curves (Catmull-Rom) through them, sampled LOFT_STEPS times per span."""
    S = np.asarray(p["stations"], float); n = len(S)
    E = np.r_[[2 * S[0] - S[1]], S, [2 * S[-1] - S[-2]]]
    out = []
    for i in range(n - 1):
        P0, P1, P2, P3 = E[i], E[i + 1], E[i + 2], E[i + 3]
        for t in np.arange(LOFT_STEPS) / LOFT_STEPS:
            out.append(0.5 * (2 * P1 + (P2 - P0) * t + (2 * P0 - 5 * P1 + 4 * P2 - P3) * t * t
                              + (3 * P1 - P0 - 3 * P2 + P3) * t ** 3))
    out.append(S[-1]); out = np.array(out); out[:, 3:] = np.maximum(np.abs(out[:, 3:]), 1e-3)
    out[:, 1] = np.maximum.accumulate(out[:, 1])                  # slices stay in order along the body
    return out


def _ellipse_d(u, v, rw, rh):
    """Distance to an ellipse (approximate away from it, exact on it): negative inside."""
    g = np.sqrt((u / rw) ** 2 + (v / rh) ** 2); k = np.sqrt((u / rw ** 2) ** 2 + (v / rh ** 2) ** 2)
    return np.where(k > 1e-12, g * (g - 1) / np.maximum(k, 1e-12), -np.minimum(rw, rh))


def sdf_loft(p, P):
    """Distance to a loft: at each point's y, the slice there (centre and half-sizes read off the smooth curves
    through the stations), closed beyond the first and last station by half-ellipsoid caps."""
    D = loft_slices(p); y = P[:, 1]
    xc, zc, rw, rh = (np.interp(y, D[:, 1], D[:, k]) for k in (0, 2, 3, 4))
    dr = _ellipse_d(P[:, 0] - xc, P[:, 2] - zc, rw, rh)
    ds = np.maximum(D[0, 1] - y, y - D[-1, 1])
    out = np.minimum(np.maximum(dr, ds), 0) + np.hypot(np.maximum(dr, 0), np.maximum(ds, 0))
    caps = np.asarray(p.get("caps", [0.0, 0.0]), float)
    for k, cap in ((0, caps[0]), (-1, caps[1])):                  # rounded ends
        r = np.array([D[k, 3], float(cap) if cap > 0 else float(min(D[k, 3], D[k, 4])), D[k, 4]])
        q = (P - D[k, :3]) / r; q2 = (P - D[k, :3]) / r ** 2
        k0 = np.linalg.norm(q, axis=1); k1 = np.linalg.norm(q2, axis=1)
        out = np.minimum(out, np.where(k1 > 1e-12, k0 * (k0 - 1) / np.maximum(k1, 1e-12), -r.min()))
    return out


def sdf_one(p, P):
    t = p["type"]
    if t == "loft": return sdf_loft(p, P)
    if t == "chain":                                # round cones sharing a ball at every joint: smooth over the
        return np.min([sdf_one(c, P) for c in segments(p)], 0)    # outside of a bend, creased inside it (a knee)
    if t == "paddle":                               # a round cone's outline in a plane, given a rounded thickness
        u, w, n = paddle_frame(p); L = float(np.linalg.norm(p["b"] - p["a"]))
        q = P - p["a"]; s = q @ u; x = q @ w; z = q @ n
        tt = np.clip(s / max(L, 1e-9), 0, 1); x = x - p["bend"] * 4 * tt * (1 - tt)
        r_here = np.maximum(float(p["ra"]) + (float(p["rb"]) - float(p["ra"])) * tt, 1e-4)
        z = z + p["curl"] * np.minimum((x / r_here) ** 2, 1.5)     # long edges curl back, wrapping round the body
        h = float(p["thick"])
        flat = {"type": "capsule", "a": p["a"], "b": p["b"], "ra": max(float(p["ra"]) - h, 1e-4),
                "rb": max(float(p["rb"]) - h, 1e-4)}
        d2 = sdf_one(flat, p["a"] + np.outer(s, u) + np.outer(x, w))     # outline, inset by the edge rounding
        az = np.abs(z)                                                   # rounded extrusion, edge radius = h
        return np.minimum(np.maximum(d2, az), 0) + np.hypot(np.maximum(d2, 0), np.maximum(az, 0)) - h
    if t == "capsule" and (float(p.get("aspect", 1.0)) != 1.0 or float(p.get("droop", 0.0)) != 0.0):
        # oval cross-section (aspect = width / height) and a tip that hooks down by "droop" metres: warp the point
        # into the frame of a plain round cone (an upper beak, a snout, a lower jaw)
        u = p["b"] - p["a"]; L = max(float(np.linalg.norm(u)), 1e-9); u = u / L
        up = np.array([0, 0, 1.0]) - u[2] * u
        up = up / np.linalg.norm(up) if np.linalg.norm(up) > 1e-6 else np.array([0, 1.0, 0])
        side = np.cross(u, up); asp = float(p.get("aspect", 1.0))
        q = P - p["a"]; s = q @ u; v = q @ up; w = q @ side
        tt = np.clip(s / L, 0, 1); v = v + float(p.get("droop", 0.0)) * tt * tt
        plain = dict(p, aspect=1.0, droop=0.0)
        return sdf_one(plain, p["a"] + np.outer(s, u) + np.outer(v, up) + np.outer(w / asp, side)) * min(asp, 1.0)
    if t == "capsule":                              # exact round cone: balls ra at a and rb at b, joined by a tangent cone
        a, b, r1, r2 = p["a"], p["b"], float(p["ra"]), float(p["rb"])
        ba = b - a; l2 = float(ba @ ba); rr = r1 - r2; a2 = l2 - rr * rr
        if a2 <= 1e-12:                             # one ball swallows the other
            return np.minimum(np.linalg.norm(P - a, axis=1) - r1, np.linalg.norm(P - b, axis=1) - r2)
        pa = P - a; y = pa @ ba; z = y - l2
        x2 = ((pa * l2 - y[:, None] * ba) ** 2).sum(1); y2 = y * y * l2; z2 = z * z * l2
        k = np.sign(rr) * rr * rr * x2
        cone = (np.sqrt(x2 * a2 / l2) + y * rr) / l2 - r1
        return np.where(np.sign(z) * a2 * z2 > k, np.sqrt(x2 + z2) / l2 - r2,
                        np.where(np.sign(y) * a2 * y2 < k, np.sqrt(x2 + y2) / l2 - r1, cone))
    R = p.get("_R", None)
    if R is None: R = rot(p["rotate"])
    Q = (P - p["center"]) @ R                       # into the part's frame
    if t == "ellipsoid":
        r = np.maximum(np.abs(p["radii"]), 1e-4)
        k0 = np.linalg.norm(Q / r, axis=1); k1 = np.linalg.norm(Q / r ** 2, axis=1)
        return np.where(k1 > 1e-12, k0 * (k0 - 1) / np.maximum(k1, 1e-12), -r.min())
    h = np.maximum(np.abs(p["half"]), 1e-4); rr = float(np.clip(p["round"], 0, h.min()))
    q = np.abs(Q) - h + rr
    return np.linalg.norm(np.maximum(q, 0), axis=1) + np.minimum(q.max(1), 0) - rr


def sdf_part(p, P):
    d = None
    for inst in instances(p):
        e = sdf_one(inst, P); d = e if d is None else np.minimum(d, e)
    return d


def smin(a, b, k):
    if np.ndim(k) == 0 and k <= 0: return np.minimum(a, b)
    h = np.maximum(k - np.abs(a - b), 0) / k
    return np.minimum(a, b) - h * h * k / 4


def grad_part(p, P, eps=1e-4):
    d = sdf_part(p, P); g = np.empty((len(P), 3))
    for i in range(3):
        Q = P.copy(); Q[:, i] += eps; g[:, i] = (sdf_part(p, Q) - d) / eps
    return g


def round_union(a, b, ga, gb, k):
    """Union of two distance fields with the crease between them rounded like a rolling ball, sized from the angle
    the two surfaces meet at (from their gradients ga, gb). Locally each surface is a plane; the ball radius is chosen
    so the rounding runs over about 1.5 x blend along the surface. A real crease (a neck into a body, about 90 deg)
    gets an ordinary fillet. A shallow crossing (two ellipsoids both fitted to the same outline, meeting at 10-20 deg)
    gets a long, gentle transition that adds only a millimetre or two: smooth-min would add up to blend/4 all along
    such an overlap and print a ring around the animal, and a sharp union would leave a visible crease line."""
    cos = np.clip((ga * gb).sum(1) / np.maximum(np.linalg.norm(ga, axis=1) * np.linalg.norm(gb, axis=1), 1e-12),
                  -0.98, 0.9999)
    sin = np.sqrt(1 - cos * cos); tan_half = sin / (1 + cos)
    R = np.minimum(np.maximum(0.6 * k, 0.75 * k / np.maximum(tan_half, 1e-6)), 20 * k)
    al, be = a - R, b - R
    keep = ((a >= R) & (b >= R)) | ((a < R) & (b + (R - a) * cos >= R)) | ((b < R) & (a + (R - b) * cos >= R))
    apex = R - np.sqrt(np.maximum(al * al + be * be - 2 * al * be * cos, 0)) / sin
    m = np.minimum(a, b)
    return np.minimum(np.where(keep, m, apex), m)


def thinnest(p):
    if p["type"] == "capsule": return float(max(p["ra"], p["rb"]))
    if p["type"] == "chain": return float(p["joints"][:, 3].max())
    if p["type"] == "loft": return float(np.median(p["stations"][:, 3:].min(1)))
    if p["type"] == "paddle": return float(p["thick"])
    return float(np.min(np.abs(p["radii" if p["type"] == "ellipsoid" else "half"])))


def joined_normal(prev, Ds, Q, tau):
    """Surface direction of the blockout built so far, at points Q: the gradients of the parts already there, each
    weighted by how close it is to being the outermost (softmin over distance, width tau). Using only the nearest
    part's gradient would jump where two earlier parts swap (the head meeting the body-and-neck join), and that jump
    prints a thin groove."""
    D = np.stack(Ds); dmin = D.min(0)
    W = np.exp(-(D - dmin) / max(tau, 1e-6)); g = np.zeros((len(Q), 3))
    for j, p in enumerate(prev):
        sel = W[j] > 1e-3
        if sel.any(): g[sel] += W[j][sel, None] * grad_part(p, Q[sel])
    return g / np.maximum(W.sum(0), 1e-12)[:, None]


def _union(parts, P, grow=0.0, smooth=True, chunk=400_000):
    """Distance to the blockout, and the part each point is nearest to. Worked through in chunks to bound memory."""
    d_all = np.empty(len(P)); id_all = np.empty(len(P), np.int16)
    for c0 in range(0, len(P), chunk):
        Q = P[c0:c0 + chunk]; d = None; best = np.full(len(Q), np.inf); idx = np.zeros(len(Q), np.int16); Ds = []
        for i, p in enumerate(parts):
            e = sdf_part(p, Q)
            if grow: e = e - min(grow, 0.25 * thinnest(p))
            if smooth: Ds.append(e.astype(np.float32))
            if d is None: d = e
            elif smooth and max(p["blend"], p.get("root_blend", 0)) > 0:
                kmax = max(p["blend"], p.get("root_blend", 0))
                M = np.nonzero(np.abs(d - e) < 1.5 * kmax)[0]
                if len(M):
                    QM = Q[M]; ge = grad_part(p, QM); k = np.full(len(M), p["blend"])
                    if p.get("root_blend", 0) > p["blend"] and p["type"] in LONG:
                        reach = max(ends(p)[2:]) + 2 * p["root_blend"]
                        near = np.min([np.linalg.norm(QM - ends(inst)[0], axis=1) for inst in instances(p)], 0)
                        k = k + (p["root_blend"] - p["blend"]) * np.clip(1 - near / reach, 0, 1)
                    gd = joined_normal(parts[:i], [x[M] for x in Ds], QM, 0.5 * kmax)
                    dM = round_union(d[M], e[M], gd, ge, np.maximum(k, 1e-6))
                d = np.minimum(d, e)
                if len(M): d[M] = dM
            else: d = np.minimum(d, e)
            closer = e < best; best[closer] = e[closer]; idx[closer] = i
        d_all[c0:c0 + chunk] = d; id_all[c0:c0 + chunk] = idx
    return d_all, id_all


def sdf(parts, P, smooth=True, grow=0.0):
    """grow: metres added all round, but never more than a quarter of a part's thinnest size,
    so thin parts (flippers, fins, ears) stay thin."""
    return _union(parts, P, grow, smooth)[0]


def nearest_part(parts, P):
    best = np.full(len(P), np.inf); idx = np.zeros(len(P), np.int16)
    for i, p in enumerate(parts):
        e = sdf_part(p, P); closer = e < best; best[closer] = e[closer]; idx[closer] = i
    return idx


def sdf_with_parts(parts, P, grow=0.0):
    """Smooth-union distance, plus which part each point is nearest to (for per-part view rules)."""
    return _union(parts, P, grow, True)


def on_centre_line(p):
    if p["mirror"]: return False
    if p["type"] == "chain": return bool(np.all(np.abs(p["joints"][:, 0]) < 1e-9))
    if p["type"] == "loft": return bool(np.all(np.abs(p["stations"][:, 0]) < 1e-9))
    if p["type"] in TUBES: return abs(p["a"][0]) < 1e-9 and abs(p["b"][0]) < 1e-9
    return abs(p["center"][0]) < 1e-9


def bounds(p):
    """Axis-aligned box (lo, hi) around a part and its mirror copy."""
    los, his = [], []
    for q in instances(p):
        if q["type"] == "chain":
            J = q["joints"]; r = float(J[:, 3].max()); lo, hi = J[:, :3].min(0) - r, J[:, :3].max(0) + r
        elif q["type"] == "loft":
            S = q["stations"]; r = float(S[:, 3:].max()) + float(np.max(q.get("caps", [0, 0])))
            lo, hi = S[:, :3].min(0) - r, S[:, :3].max(0) + r
        elif q["type"] in TUBES:
            r = max(q["ra"], q["rb"]) + (abs(q["bend"]) + abs(q["curl"]) if q["type"] == "paddle" else 0)
            lo, hi = np.minimum(q["a"], q["b"]) - r, np.maximum(q["a"], q["b"]) + r
        else:
            R = q.get("_R"); R = rot(q["rotate"]) if R is None else R
            ext = np.abs(R) @ np.abs(q["radii"] if q["type"] == "ellipsoid" else q["half"])
            lo, hi = q["center"] - ext, q["center"] + ext
        los.append(lo); his.append(hi)
    return np.min(los, 0), np.max(his, 0)


# ---- parameter vectors for fitting ---------------------------------------------------------------------------------

def volume(p):
    """Rough volume (all mirrored copies), from a 16-cube grid over the part's box."""
    lo, hi = bounds(p); g = [np.linspace(lo[k], hi[k], 16) for k in range(3)]
    G = np.stack(np.meshgrid(*g, indexing="ij"), -1).reshape(-1, 3)
    return float((sdf_part(p, G) < 0).mean() * np.prod(hi - lo))


def scale_of(p):
    if p["type"] == "loft":
        S = p["stations"]; return max(float(np.linalg.norm(np.diff(S[:, :3], axis=0), axis=1).sum()), float(S[:, 3:].max()))
    if p["type"] == "chain":
        J = p["joints"]; return max(float(np.linalg.norm(np.diff(J[:, :3], axis=0), axis=1).sum()), float(J[:, 3].max()))
    if p["type"] in TUBES: return max(np.linalg.norm(p["b"] - p["a"]), p["ra"], p["rb"])
    return float(np.max(np.abs(p["radii" if p["type"] == "ellipsoid" else "half"])))


def params(p):
    """(name, index or None, kind) for every tunable number of a part. kind: pos, size, angle."""
    if p["fit"] is False: return []
    axes = (1, 2) if on_centre_line(p) else (0, 1, 2)          # centre-line parts never move sideways
    if p["type"] == "loft":                          # stations move up and down (and sideways), not along
        return [("stations", (j, i), "pos") for j in range(len(p["stations"])) for i in axes if i != 1] + \
               [("stations", (j, i), "size") for j in range(len(p["stations"])) for i in (3, 4)]
    if p["type"] == "chain":
        return [("joints", (j, i), "pos") for j in range(len(p["joints"])) for i in axes] + \
               [("joints", (j, 3), "size") for j in range(len(p["joints"]))]
    if p["type"] in TUBES:
        out = [("a", i, "pos") for i in axes] + [("b", i, "pos") for i in axes] + [("ra", None, "size"), ("rb", None, "size")]
        return out + ([("thick", None, "size")] if p["type"] == "paddle" else [])
    size = "radii" if p["type"] == "ellipsoid" else "half"
    turns = (0,) if on_centre_line(p) else (0, 1, 2)           # ... nor turn about y or z
    out = [("center", i, "pos") for i in axes] + [(size, i, "size") for i in range(3)] + [("rotate", i, "angle") for i in turns]
    if p["type"] == "box": out.append(("round", None, "size"))
    return out


def label(key, i):
    """A tunable number's name for reports: center[x], ra, joints[2].z"""
    if i is None: return key
    if isinstance(i, tuple):
        return f"{key}[{i[0]}]." + (["x", "y", "z", "half_width", "half_height"] if key == "stations" else list("xyzr"))[i[1]]
    return f"{key}[{'xyz'[i]}]"


def fit_scale(p):
    """The size the fitter scales a part's steps and limits by: a loft's stations move by fractions of its
    thickness, not of its length."""
    if p["type"] == "loft": return float(p["stations"][:, 3:].max())
    return scale_of(p)


def get(p, key, i):
    return float(p[key][i]) if i is not None else float(p[key])


def put(p, key, i, v):
    if i is None: p[key] = np.array(v, float)
    else: p[key] = p[key].copy(); p[key][i] = v
