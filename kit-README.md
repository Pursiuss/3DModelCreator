# Practice kit (v0.2)

v0.2 replaces v0.1. Changes: the colour score now compares your model with the reference views (background removed), not with the scene picture; both scores use the best two of the front, side and top views; a check for gross errors was added; and the header now states the camera directions correctly (the nose points towards -y).

## Input format your skill receives
A folder `refs/` for one animal:

| File | What |
|---|---|
| `front.png`, `side.png`, `back.png`, `top.png` | reference views of the animal, cut out on a transparent background |
| `final.png` | the finished look, in a scene. The experts judge your texture against it. The script does not use it. |
| `subject.json` | real size in metres: `{"height": .., "length": .., "width": ..}` |

The hidden animals follow the same four-view layout.

## The reference pictures are not perfectly consistent
They are made with AI image tools, so the views do not agree exactly with each other. For example, in the penguin's back view the feet are drawn facing the same way as in the front view, which is wrong for a back view. **We will not repair them.** Finding and handling such errors is part of the task. You may use AI image tools to fix, repair or generate new views for your own process.

## Cameras (all orthographic, no perspective)
z is up, x is left-right, y is along the length of the animal. **The nose points towards -y.** The feet are at z = 0.

| View | Camera | Image right | The animal faces |
|---|---|---|---|
| front | at -y, looking along +y | +x | the camera |
| back | at +y, looking along -y | -x | away from the camera |
| side | at +x, looking along -x | +y | the left of the picture |
| top | above, looking down | -x | the top of the picture |

## Output your skill must write
`out/untextured.glb`, `out/textured.glb`, `out/run-log.md` (models used, effort, steps, what failed, every image-generation call).

## Scoring script (`score_glb.py`)
```
python score_glb.py out/untextured.glb penguin/ --out score.json
python score_glb.py out/textured.glb  penguin/ --out score.json --textured
```
Needs Python, numpy and Pillow only. The `penguin/` folder is a complete example. For the hidden animals the staff make the masks.

- **Shape score:** in each of front, side and top, the overlap (IoU) of your model's silhouette with the reference silhouette. The score is the mean of the **best two** of the three. The back view is shown in the report but not scored.
- **Gross errors:** a view where more than 2% of the animal's picture is wrong by more than a tolerance of 3% of its longest dimension (about 2 cm on a 70 cm animal). It means a missing or misplaced body part, such as a missing head or foot, or a nose at the wrong end. Your shape test passes only with an empty `gross_errors` list.
- **Colour score** (`--textured`): your textured model is drawn in each view and compared, cell by cell, with the reference picture. The background is removed on both sides, so only the animal counts. The score is the mean of the **best two** of front, side and top. Your model needs a base-colour texture and UV coordinates.
- **Best two of three:** the references are not perfectly consistent, so the two views that agree best with your model decide the score.

## Pass bar (each of the three hidden animals)
**Shape score 0.80 or more with no gross errors, and colour score 0.80 or more.** Then expert review.

## Read this before you tune to the score
- Overlap is generous: a model of a *building* scores about 0.5 against the penguin, and our finished penguin models score about 0.93. The gross-error check is there because overlap alone lets some wrong models through.
- The script cannot see a flat foot where a webbed foot should be, or a fin on the wrong side. The expert review does.
- Colour is compared in the same four views as shape, so painting detail that is hidden from those views is not scored.

## Practice animal
The `penguin/` folder holds the whole practice set. Our own textured penguin models score 0.93 on shape and 0.90 to 0.92 on colour against it.
