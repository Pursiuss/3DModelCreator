"""Whole pipeline: reference folder -> out/untextured.glb, out/textured.glb, previews, self-check, run-log section.

usage: python build.py REFS_DIR OUT_DIR --parts PARTS.json [--grow 0] [--res 280] [--blur 1.0] [--smooth 8] [--tol 3]
                                        [--skip-view VIEW ...] [--note TEXT]
       python build.py REFS_DIR OUT_DIR --hull-only [--round 2] ...     (fallback: outlines only, no blockout)

With --parts (normal use): the shape is the fitted blockout, trimmed where it sticks out of the reference outlines.
--grow (metres, default 0) enlarges the blockout before trimming: closer outlines, but flat cut surfaces.
Writes OUT_DIR/report.json (numbers for the agent) and appends a "pipeline run" section to OUT_DIR/run-log.md.
The self-check scores the models with the bundled copy of score_glb.py against masks made from the references' own
transparency (the staff make their own masks for the judged run, so expect small differences).
"""
import argparse, datetime, json, os, subprocess, sys, time
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from views import VIEWS, load_subject, consistency, alignment_note
from carve import build_shape, build_shape_parts, recentre
from texture import texture_mesh
from glb_io import write_glb
from render_preview import preview
from part_colours import write_part_model
import parts as PT

HERE = os.path.dirname(os.path.abspath(__file__))


def check_refs(refs, S):
    """Warnings about inputs that tend to break carving."""
    w = [f"{v}: silhouette from {S['notes'][v]} - check the preview for background left on"
         for v in VIEWS if S["notes"][v] != "alpha channel"]
    cw, skip = consistency(S["maps"])
    if alignment_note(S["maps"]): w.append(alignment_note(S["maps"]))
    skip = [v for v in skip if v not in S.get("skip", ())]
    return w + cw + ([f"not skipped although they disagree: {', '.join(skip)} (see measure.py's view check)"] if skip else [])


def self_score(model, refs, maps, out_dir, textured):
    md = os.path.join(out_dir, "selfcheck"); os.makedirs(md, exist_ok=True)
    for v, vm in maps.items(): Image.fromarray((vm.sil * 255).astype(np.uint8)).save(os.path.join(md, f"{v}-mask.png"))
    size, _ = load_subject(refs)                                    # the scorer reads only the three sizes
    json.dump({k: size[k] for k in ("height", "length", "width")}, open(os.path.join(md, "subject.json"), "w"))
    for f in ("front.png", "side.png", "back.png", "top.png"):     # pictures: for the colour score
        src = os.path.join(refs, f)
        if os.path.exists(src): open(os.path.join(md, f), "wb").write(open(src, "rb").read())
    cmd = [sys.executable, os.path.join(HERE, "score_glb.py"), model, md] + (["--textured"] if textured else [])
    return json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("refs"); ap.add_argument("out")
    ap.add_argument("--parts"); ap.add_argument("--hull-only", action="store_true")
    ap.add_argument("--grow", type=float); ap.add_argument("--round", type=float, default=2.0)
    ap.add_argument("--res", type=int, default=280); ap.add_argument("--blur", type=float)
    ap.add_argument("--smooth", type=int); ap.add_argument("--tol", type=int, default=3)
    ap.add_argument("--quick", action="store_true", help="for trying things out: coarser mesh and a 1024 texture, "
                    "about half the time; leave it off for the final build")
    ap.add_argument("--note", default=""); ap.add_argument("--skip-view", nargs="*", default=[], choices=list(VIEWS))
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); t0 = time.time()
    if a.quick and a.res == 280: a.res = 180
    if not a.parts and not a.hull_only: ap.error("give --parts PARTS.json (normal) or --hull-only (fallback)")

    if a.parts:
        parts = PT.load(a.parts)
        S = build_shape_parts(a.refs, parts, a.res, a.grow, 1.0 if a.blur is None else a.blur,
                              8 if a.smooth is None else a.smooth, tuple(a.skip_view))
        method = (f"blockout ({len(parts)} parts from {os.path.basename(a.parts)}) grown {S['grow'] * 1000:.1f} mm, "
                  f"trimmed to the outlines ({S['voxel'] * 1000:.2f} mm voxels), smoothed; "
                  f"kept {S['pieces'][0]} of {S['pieces'][1]} mesh pieces"
                  + (f"; built on a finer grid and joined on: {', '.join(S['fine'])}" if S.get("fine") else ""))
    else:
        S = build_shape(a.refs, a.res, a.round, False, 12 if a.smooth is None else a.smooth,
                        1.5 if a.blur is None else a.blur, tuple(a.skip_view))
        method = f"outlines only (visual hull, {S['voxel'] * 1000:.2f} mm voxels, rounded slices p = {a.round})"
    S["skip"] = tuple(a.skip_view); warnings = check_refs(a.refs, S)
    if S.get("auto_ignored"):
        warnings.append("views ignored for parts they disagree with (one view would have cut deep into a part the "
                        "others draw whole): " + "; ".join(f"{k}: {', '.join(v)}" for k, v in S["auto_ignored"].items()))
    if S.get("dropped_piece", 0) > 0.002:
        warnings.append(f"a loose piece ({S['dropped_piece']:.1%} of the model) came off and was dropped: a part "
                        f"(often a tail, ear or horn) joins the body only where trimming cuts it; start it inside the "
                        f"part it grows from, and build a thin tail, strand or leg as a chain (thin chains are built on "
                        f"a finer grid, with whatever hangs from them)")
    if S.get("untrimmed"):
        warnings.append("kept untrimmed, because trimming to the outlines would have removed most of them (they are "
                        "off their drawn place; move them onto it in parts-on-refs.png): " + ", ".join(S["untrimmed"]))
    shift = recentre(S["V"])[0] - S["V"][0]                     # same shift for both models
    untex = os.path.join(a.out, "untextured.glb"); tex = os.path.join(a.out, "textured.glb")
    write_glb(untex, S["V"] + shift, S["F"], normals=S.get("N"))
    if a.quick: S["bake_size"] = 1024
    V2, F2, UV, atlas, tstats, N2 = texture_mesh(a.refs, S, a.tol)
    write_glb(tex, V2 + shift, F2, UV, atlas, normals=N2)
    atlas.save(os.path.join(a.out, "texture-atlas.png"))
    preview(S["V"], S["F"], None, None, os.path.join(a.out, "preview-untextured.png"), N=S.get("N"))
    preview(V2, F2, UV, atlas, os.path.join(a.out, "preview-textured.png"), N=N2)
    key = (write_part_model(os.path.join(a.out, "parts-coloured.glb"), os.path.join(a.out, "preview-parts.png"),
                            S["V"], S["F"], S.get("N"), parts, shift, write_glb) if a.parts else None)
    s_shape = self_score(untex, a.refs, S["maps"], a.out, False)
    s_tex = self_score(tex, a.refs, S["maps"], a.out, True)
    ext = S["V"].max(0) - S["V"].min(0)
    report = {"params": vars(a), "method": method, "voxel_mm": round(S["voxel"] * 1000, 2), "triangles": len(S["F"]),
              "extent_m": {"width": round(ext[0], 3), "length": round(ext[1], 3), "height": round(ext[2], 3)},
              "subject_m": S["size"], "silhouettes": S["notes"], "warnings": warnings,
              "texture_views": tstats, "part_colours": key, "self_check": {"untextured_shape": s_shape["shape_score"],
              "textured_shape": s_tex["shape_score"], "gross_errors": s_shape.get("gross_errors", []),
              "colour_score": s_tex.get("colour_score"), "views": s_tex["views"]}, "seconds": round(time.time() - t0, 1)}
    json.dump(report, open(os.path.join(a.out, "report.json"), "w"), indent=1)

    log = os.path.join(a.out, "run-log.md"); new = not os.path.exists(log)
    args = " ".join(sys.argv[1:])
    with open(log, "a", encoding="utf-8") as f:
        if new: f.write("# Run log\n\n")
        f.write(f"## Pipeline run {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n\n")
        if a.note: f.write(f"Why this run: {a.note}\n\n")
        f.write(f"- Command: `build.py {args}`\n")
        f.write(f"- Shape: {method}\n")
        f.write(f"- Texture: projected from the reference views (share per view, and share filled from neighbours): {tstats}\n")
        sc = report["self_check"]
        f.write(f"- Self-check (own masks, kit v0.2 scorer): shape {sc['untextured_shape']} (textured "
                f"{sc['textured_shape']}), gross errors {', '.join(sc['gross_errors']) or 'none'}, colour {sc['colour_score']}\n")
        f.write(f"- Warnings: {'; '.join(warnings) if warnings else 'none'}\n- Time: {report['seconds']} s\n\n")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
