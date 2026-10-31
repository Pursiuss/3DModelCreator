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
| `tests/` | `make_test_workspace.py` (sets up `../penguin-skill-test` for a test run), `make_refs_from_sheet.py`, the model viewer, and the results: `test-00` (the first penguin build) to `test-10`, one folder per test with a folder per animal; `quick-tests/`; `inspection/` (before/after sheets for each fix) |
| `OLD/` | superseded material kept for reference (see `OLD/README.md`) |
| `organizer-questions.md` | open questions for the organizers |

To try the skill on the penguin:
```
python -m venv .venv
.venv/Scripts/python -m pip install -r skill/requirements.txt
```
then follow `skill/SKILL.md` with `references/penguin` as the references folder.

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
