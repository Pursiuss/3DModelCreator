"""Score every reference animal with the current skill, in one table.

usage (from the kit folder):
  .venv/Scripts/python tests/score_all.py                     # all animals, full builds
  .venv/Scripts/python tests/score_all.py --animals cow dog   # some of them
  .venv/Scripts/python tests/score_all.py --quick --jobs 3    # faster, coarser builds; 3 at a time

For each animal in references/, the blockout its latest saved test ended with (tests/test-NN/<animal>, else
tests/quick-tests/<animal>) is rebuilt with skill/scripts/build.py, with that test's build options. The blockout is
fixed, so only changes to the skill's code move the scores: this is a check for regressions, not a fresh agent run.

Both models are scored with the kit's own score_glb.py (the organizers' scorer, run as it is). It needs a mask per
view: the official <view>-mask.png where the references have one (the penguin), else a mask made from the picture's
transparency, as the build's self-check makes them (the staff make their own masks for the judged run, so expect
small differences). A subject with a missing view (Miku has no top) cannot be scored by it and is left out.

Results go to tests/auto-scores/<label>/ (results.json, table.md, and each animal's build); the table also shows
the change since the previous run."""
import argparse, glob, json, os, re, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFS = os.path.join(KIT, "references")
OUT = os.path.join(KIT, "tests", "auto-scores")
SCORER = os.path.join(KIT, "score_glb.py")                      # the kit's scorer, unchanged
BUILD = os.path.join(KIT, "skill", "scripts", "build.py")
VIEWS = ("front", "side", "back", "top")
BAR = 0.80                                                      # pass bar for shape and colour (kit-README.md)
sys.path.insert(0, os.path.join(KIT, "skill", "scripts"))
from views import silhouette, load_subject


def latest_test(animal):
    """The newest saved test of an animal that has a report and its blockout: (folder, report)."""
    tests = sorted(glob.glob(os.path.join(KIT, "tests", "test-*", animal)),
                   key=lambda p: int(re.search(r"test-(\d+)", p).group(1)), reverse=True)
    for d in tests + [os.path.join(KIT, "tests", "quick-tests", animal)]:
        rp = os.path.join(d, "report.json")
        if not os.path.exists(rp): continue
        rep = json.load(open(rp))
        if rep["params"].get("parts") and os.path.exists(os.path.join(d, "work", os.path.basename(rep["params"]["parts"]))):
            return d, rep
    return None, None


def scoring_refs(animal):
    """A folder the kit's scorer can read: pictures, masks and the three sizes."""
    src, dst = os.path.join(REFS, animal), os.path.join(OUT, "masks", animal)
    os.makedirs(dst, exist_ok=True)
    for v in VIEWS:
        shutil.copyfile(os.path.join(src, f"{v}.png"), os.path.join(dst, f"{v}.png"))
        official = os.path.join(src, f"{v}-mask.png")
        if os.path.exists(official): shutil.copyfile(official, os.path.join(dst, f"{v}-mask.png"))
        else: Image.fromarray(silhouette(src, v)[0].astype(np.uint8) * 255).save(os.path.join(dst, f"{v}-mask.png"))
    size, _ = load_subject(src)
    json.dump({k: size[k] for k in ("height", "length", "width")}, open(os.path.join(dst, "subject.json"), "w"))
    return dst


def build_args(params, quick):
    """build.py options of the saved test (only those that differ from build.py's defaults)."""
    args = []
    if params.get("skip_view"): args += ["--skip-view", *params["skip_view"]]
    for key, flag, default in (("grow", "--grow", None), ("round", "--round", 2.0), ("res", "--res", 280),
                               ("blur", "--blur", None), ("smooth", "--smooth", None), ("tol", "--tol", 3)):
        if params.get(key) is not None and params[key] != default: args += [flag, str(params[key])]
    if params.get("hull_only"): args.append("--hull-only")
    if quick: args.append("--quick")                             # (a quick test's blockout is built in full)
    return args


def score(model, refs, textured):
    cmd = [sys.executable, SCORER, model, refs] + (["--textured"] if textured else [])
    return json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)


def run_animal(animal, run_dir, quick):
    src, rep = latest_test(animal)
    if src is None: return {"animal": animal, "error": "no saved test with a blockout"}
    out = os.path.join(run_dir, animal); work = os.path.join(out, "work"); os.makedirs(work, exist_ok=True)
    parts = os.path.join(work, os.path.basename(rep["params"]["parts"]))
    shutil.copyfile(os.path.join(src, "work", os.path.basename(parts)), parts)
    t0 = time.time()
    cmd = [sys.executable, BUILD, os.path.join(REFS, animal), out, "--parts", parts, "--note", "auto-score"]
    cmd += build_args(rep["params"], quick)
    b = subprocess.run(cmd, capture_output=True, text=True)
    open(os.path.join(out, "build-log.txt"), "w").write(b.stdout + b.stderr)
    if b.returncode: return {"animal": animal, "source": os.path.relpath(src, KIT), "error": "build failed (see build-log.txt)"}
    refs = scoring_refs(animal)
    s = score(os.path.join(out, "untextured.glb"), refs, False)
    c = score(os.path.join(out, "textured.glb"), refs, True)
    shape, colour, gross = s["shape_score"], c.get("colour_score"), s.get("gross_errors", [])
    return {"animal": animal, "source": os.path.relpath(src, KIT).replace("\\", "/"), "shape": shape, "colour": colour,
            "gross_errors": gross, "iou": {v: s["views"][v]["iou"] for v in VIEWS},
            "view_colour": {v: c["views"][v].get("colour") for v in VIEWS},
            "pass": shape >= BAR and not gross and colour is not None and colour >= BAR,
            "build_seconds": round(time.time() - t0, 1), "options": cmd[cmd.index("auto-score") + 1:]}


def previous_results(label):
    runs = sorted(d for d in glob.glob(os.path.join(OUT, "*", "results.json")) if os.path.basename(os.path.dirname(d)) != label)
    return {r["animal"]: r for r in json.load(open(max(runs, key=os.path.getmtime)))["animals"]} if runs else {}, \
           (os.path.basename(os.path.dirname(max(runs, key=os.path.getmtime))) if runs else None)


def table(results, prev, prev_label):
    def delta(a, b): return "" if a is None or b is None else f" ({a - b:+.3f})" if abs(a - b) >= 0.0005 else " (=)"
    rows = ["| animal | from | shape | front / side / top IoU | gross errors | colour | pass |",
            "|---|---|---|---|---|---|---|"]
    for r in results:
        if "error" in r: rows.append(f"| {r['animal']} | {r.get('source', '')} | {r['error']} | | | | |"); continue
        p = prev.get(r["animal"], {})
        iou = " / ".join(f"{r['iou'][v]:.3f}" for v in ("front", "side", "top"))
        rows.append(f"| {r['animal']} | {r['source']} | {r['shape']:.3f}{delta(r['shape'], p.get('shape'))} | {iou} | "
                    f"{', '.join(r['gross_errors']) or 'none'} | {r['colour']:.3f}{delta(r['colour'], p.get('colour'))} | "
                    f"{'yes' if r['pass'] else 'NO'} |")
    note = f"changes in brackets are against run '{prev_label}'" if prev_label else "first run: nothing to compare with"
    return "\n".join(rows) + f"\n\nScored with the kit's score_glb.py; pass = shape >= {BAR}, no gross errors, colour >= {BAR}; {note}.\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--animals", nargs="*", help="default: every folder in references/ that has all four views")
    ap.add_argument("--quick", action="store_true", help="coarser, faster builds (scores drop a little)")
    ap.add_argument("--jobs", type=int, default=3, help="builds at the same time (each needs a few GB of memory)")
    ap.add_argument("--label", default=time.strftime("%Y-%m-%d_%H%M"), help="name of this run's folder")
    a = ap.parse_args()
    animals = a.animals or sorted(d for d in os.listdir(REFS) if os.path.exists(os.path.join(REFS, d, "subject.json")))
    skipped = [x for x in animals if any(not os.path.exists(os.path.join(REFS, x, f"{v}.png")) for v in VIEWS)]
    animals = [x for x in animals if x not in skipped]
    for x in skipped: print(f"{x}: left out (a view has no picture, so the kit's scorer cannot score it)")
    run_dir = os.path.join(OUT, a.label); os.makedirs(run_dir, exist_ok=True)
    prev, prev_label = previous_results(a.label)
    print(f"building {', '.join(animals)} ({a.jobs} at a time) into {os.path.relpath(run_dir, KIT)}", flush=True)
    with ThreadPoolExecutor(a.jobs) as ex:
        results = list(ex.map(lambda x: run_animal(x, run_dir, a.quick), animals))
    for r in results: print(f"  {r['animal']}: {r.get('error') or 'done in %.0f s' % r['build_seconds']}")
    json.dump({"label": a.label, "quick": a.quick, "animals": results, "left_out": skipped},
              open(os.path.join(run_dir, "results.json"), "w"), indent=1)
    t = table(results, prev, prev_label)
    open(os.path.join(run_dir, "table.md"), "w").write(f"# Auto-score {a.label}{' (quick builds)' if a.quick else ''}\n\n" + t)
    print("\n" + t)


if __name__ == "__main__":
    main()
