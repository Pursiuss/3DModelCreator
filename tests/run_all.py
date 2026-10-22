"""Run the skill's pipeline on every test animal and score it with the official scorer (using the true masks).

usage: python tests/run_all.py [ANIMAL_DIRS...]   (default: penguin/ and every folder in tests/animals/)
Uses the blockout tests/work/<name>/parts.fitted.json (out/work/ for the penguin) when there is one, else --hull-only.
Writes tests/results/<name>/ (the pipeline output) and tests/results/summary.md.
"""
import glob, json, os, subprocess, sys

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable


def main():
    dirs = sys.argv[1:] or [os.path.join(KIT, "penguin")] + sorted(d for d in glob.glob(os.path.join(KIT, "tests", "animals", "*")) if os.path.isdir(d))
    rows = []
    for d in dirs:
        name = os.path.basename(os.path.normpath(d)); out = os.path.join(KIT, "tests", "results", name)
        if os.path.exists(os.path.join(out, "run-log.md")): os.remove(os.path.join(out, "run-log.md"))
        parts = [p for p in (os.path.join(KIT, "tests", "work", name, "parts.fitted.json"),
                             os.path.join(KIT, "out", "work", "parts.fitted.json") if name == "penguin" else "")
                 if p and os.path.exists(p)]
        mode = ["--parts", parts[0]] if parts else ["--hull-only"]
        r = subprocess.run([PY, os.path.join(KIT, "skill", "scripts", "build.py"), d, out, *mode], capture_output=True, text=True)
        if r.returncode:
            rows.append(f"| {name} | FAILED | | | | {r.stderr.strip().splitlines()[-1]} |"); print(name, "FAILED"); continue
        rep = json.load(open(os.path.join(out, "report.json")))
        s = lambda m, *x: json.loads(subprocess.run([PY, os.path.join(KIT, "score_glb.py"), os.path.join(out, m), d, *x],
                                                     capture_output=True, text=True, check=True).stdout)
        a, b = s("untextured.glb"), s("textured.glb", "--textured")
        views = " ".join(f"{k} {v['iou']}" for k, v in a["views"].items())
        ok = a["shape_score"] >= 0.8 and not a.get("gross_errors") and (b.get("colour_score") or 0) >= 0.8
        rows.append(f"| {name} | {a['shape_score']} | {b.get('colour_score')} | {'pass' if ok else 'FAIL'} | {views} | "
                    f"{rep['seconds']} s; {'; '.join(rep['warnings']) or 'no warnings'} |")
        print(rows[-1], flush=True)
    with open(os.path.join(KIT, "tests", "results", "summary.md"), "w", encoding="utf-8") as f:
        f.write("| animal | shape | colour | bar | per-view IoU | notes |\n|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n")


if __name__ == "__main__":
    main()
