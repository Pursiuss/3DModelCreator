# 3DModelCreator
An AI skill that takes 2D reference images and create a 3D model

Entry for the Algoma "Can you ask AI to make a penguin?" challenge: an agent skill that, given a folder of reference
views of an animal (`front.png`, `side.png`, `back.png`, `top.png`, `final.png`, `subject.json`), builds an
untextured and a textured `.glb` model unattended, by blocking the animal out in simple shapes, fitting them to the
outlines, and texturing from the drawings.

| Path | What |
|---|---|
| `skill/` | the skill itself: `SKILL.md` (the agent's instructions), `requirements.txt` and `scripts/` |
| `kit-README.md`, `score_glb.py` | the organizers' practice kit: rules and scorer (their penguin references are in `references/penguin/`) |
| `references/` | the reference subjects (penguin, cow, dog, giraffe, stag, sheep), each with its four views, `final.png` and `subject.json`; `sheets/` holds the original turnaround sheets they were cut from |
| `tests/` | `make_test_workspace.py` (sets up `../penguin-skill-test` for a test run), `score_all.py` (scores every animal with the current skill, see below), `make_refs_from_sheet.py`, the model viewer, and the results: `test-00` (the first penguin build) onwards, one folder per test with a folder per animal; `quick-tests/`; `auto-scores/` (one folder per `score_all.py` run); `inspection/` (before/after sheets for each fix) |
| `OLD/` | superseded material kept for reference (see `OLD/README.md`) |
| `organizer-questions.md` | open questions for the organizers |

To try the skill on the penguin:
```
python -m venv .venv
.venv/Scripts/python -m pip install -r skill/requirements.txt
```
then follow `skill/SKILL.md` with `references/penguin` as the references folder.

## Scoring all the animals

After a change to the skill, check that no animal got worse:
```
.venv/Scripts/python tests/score_all.py
```
It rebuilds every animal in `references/` from the blockout its latest saved test ended with (so only the skill's
code changes between runs, not the agent's work), scores both models with the kit's own `score_glb.py` (run as it
is), and prints one table: shape, the IoU per view, gross errors, colour, pass or not, and the change since the last
run. Each run is saved in `tests/auto-scores/<date_time>/` (`table.md`, `results.json`). A full run takes about
15 minutes; `--quick` is faster but coarser, `--animals cow dog` scores only some, `--jobs` sets how many build at
once. The penguin is scored against the kit's own masks; the others against masks made from their pictures'
transparency (the staff make their own for the judged run). Miku is left out: she has no top view, which the kit's
scorer needs.

## Viewing the models

Each run writes three models to its output folder: `untextured.glb`, `textured.glb`, and `parts-coloured.glb`
(each body part in its own flat colour, for spotting shape problems; `preview-parts.png` is its key).

**Local viewer (recommended).** Double-click `view-models.bat` in the kit folder: it starts the viewer and opens
http://localhost:8765 in the browser; close its window to stop it. Or, from the kit folder:
```
.venv/Scripts/python tests/viewer/serve.py
```
then open http://localhost:8765. The drop-down lists every `.glb` in this folder and in the test workspace next to
it (`../penguin-skill-test`), newest first; press **Reload** after a new run. Drag to turn, scroll to zoom,
right-drag to pan; the buttons switch the texture (or the part colours) on and off, show the wireframe, spin the
model and jump to the front, side, back, top and 3/4 views. Use `--port` for another port. The page loads three.js
from a CDN, so it needs an internet connection; nothing is uploaded, and the server only answers on this computer.

**Without the viewer.** A `.glb` also opens in Blender (File > Import > glTF 2.0), or by dragging it onto an online glTF viewer such as https://gltf-viewer.donmccurdy.com (the file
stays in the browser). Each run's `preview-textured.png`, `preview-untextured.png` and `preview-parts.png` show the
model from five angles without opening it.
