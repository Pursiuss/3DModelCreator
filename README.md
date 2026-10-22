# 3DModelCreator
An AI skill that takes 2D reference images and create a 3D model

Entry for the Algoma "Can you ask AI to make a penguin?" challenge: an agent skill that, given a folder of reference
views of an animal (`front.png`, `side.png`, `back.png`, `top.png`, `final.png`, `subject.json`), builds an
untextured and a textured `.glb` model unattended, by blocking the animal out in simple shapes, fitting them to the
outlines, and texturing from the drawings.

| Path | What |
|---|---|
| `skill/` | the skill itself: `SKILL.md` (the agent's instructions), `requirements.txt` and `scripts/` |
| `kit-README.md`, `score_glb.py`, `penguin/` | the organizers' practice kit: rules, scorer and the penguin references |
| `organizer-questions.md` | open questions for the organizers |
| `out/` | the latest penguin build |
| `tests/` | test animals, test scripts, results and inspection renders |

To try the skill on the penguin:
```
python -m venv .venv
.venv/Scripts/python -m pip install -r skill/requirements.txt
```
then follow `skill/SKILL.md` with `penguin` as the references folder.
