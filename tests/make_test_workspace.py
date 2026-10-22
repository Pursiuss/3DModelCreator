"""Create or refresh a clean folder for testing the skill in a fresh Claude Code conversation.

usage: python tests/make_test_workspace.py [WORKSPACE] [--fresh]
  default WORKSPACE: ../penguin-skill-test (next to the kit folder)

The workspace holds only what a judged run would get:
  .claude/skills/animal-model-from-views/   copy of skill/ (Claude Code finds project skills here)
  refs/<animal>/                             front/side/back/top.png, final.png, subject.json (no masks, no answers)
Rerun after changing the skill; it replaces the skill copy and refs. --fresh also deletes out/ and .venv-skill/
there, so the next run repeats the setup step from scratch.
Score a finished run from the kit folder:  .venv/Scripts/python score_glb.py WORKSPACE/out/textured.glb penguin/ --textured
"""
import os, shutil, sys

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILES = ["front.png", "side.png", "back.png", "top.png", "final.png", "subject.json"]
ANIMALS = {"penguin": os.path.join(KIT, "penguin"),
           "turtle": os.path.join(KIT, "tests", "animals", "turtle"),
           "giraffe": os.path.join(KIT, "tests", "animals", "giraffe")}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ws = os.path.abspath(args[0] if args else os.path.join(KIT, "..", "penguin-skill-test"))
    os.makedirs(ws, exist_ok=True)
    if "--fresh" in sys.argv:
        for d in ("out", ".venv-skill"): shutil.rmtree(os.path.join(ws, d), ignore_errors=True)

    dst = os.path.join(ws, ".claude", "skills", "animal-model-from-views")
    shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(os.path.join(KIT, "skill"), dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    for name, src in ANIMALS.items():
        if not os.path.isdir(src): print("skipped", name, "(run tests/make_synthetic.py first)"); continue
        d = os.path.join(ws, "refs", name); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
        for f in INPUT_FILES: shutil.copy(os.path.join(src, f), d)
    print("workspace ready:", ws)


if __name__ == "__main__":
    main()
