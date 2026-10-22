# Practice kit (v0.1)

## Input format your skill receives
A folder `refs/` for one animal:

| File | What |
|---|---|
| `front.png`, `side.png`, `back.png`, `top.png` | reference images of the animal |
| `final.png` | the finished look: the texture target |
| `subject.json` | real size in metres: `{"height": .., "length": .., "width": ..}` |

The hidden animals use exactly this layout. Your skill gets the folder path and nothing else.

## Output your skill must write
`out/untextured.glb`, `out/textured.glb`, `out/run-log.md` (models used, effort, steps, what failed).

## Scoring script (`score_glb.py`)
```
python score_glb.py out/untextured.glb penguin/ --out score.json
python score_glb.py out/textured.glb  penguin/ --out score.json --textured
```
Needs Python, numpy and Pillow only. The `penguin/` folder is a complete example: references, `final.png`, `subject.json` and the four masks `front-mask.png`, `side-mask.png`, `back-mask.png`, `top-mask.png` (white = animal). For the hidden animals the staff make the masks.

- **Shape score** = mean overlap (IoU) of the model's silhouette with the reference silhouette in four views. Higher is better, 1.0 is perfect.
- **Colour match** = a coarse colour-histogram similarity to `final.png`. It cannot judge pattern or placement; the experts do that.
- The conventions (axes, scale, what counts as the feet) are in the script's header.

## Read this before you tune to the score
- Overlap is generous: on our test, a model of a *building* scores about **0.5** against the penguin, and the course staff's penguin models score about **0.9**. A big score difference is therefore meaningful; the last few points are not.
- The script only sees outlines. It cannot see a flat foot where a webbed foot should be, or a fin on the wrong side. The expert review does.
- **The pass bar is 0.80 shape score and 0.80 colour match, on each of the three hidden animals.**

## Practice animal
The `penguin/` folder in this kit holds the whole practice set. Two of the course staff's penguin models score 0.90 and 0.93 on shape against it.
