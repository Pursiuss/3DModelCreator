---
name: animal-model-from-views
description: Build an untextured and a textured 3D model (.glb) of an animal from a folder of reference views (front.png, side.png, back.png, top.png, final.png, subject.json). Use when asked to make a 3D model of an animal from reference images, or when given a refs folder in this layout. Runs unattended; writes out/untextured.glb, out/textured.glb and out/run-log.md.
---

# Animal model from reference views

You model the animal the way a person would: block it out in simple shapes, fit them to the references, then let
the scripts trim, smooth and texture it. You are the modeller (you decide what the parts are and where they go);
the scripts do the measuring, fitting and mesh work.

You get one folder path, `REFS`, holding:

| File | What |
|---|---|
| `front.png`, `side.png`, `back.png`, `top.png` | orthographic reference views of the animal, usually with a transparent background |
| `final.png` | the finished look, in a scene: what the expert reviewers compare the texture with (the scoring script compares it with the four views instead) |
| `subject.json` | real size in metres: `{"height": .., "length": .., "width": ..}` |

You must write, in `out/` under the current working directory unless the task names another place:
`out/untextured.glb`, `out/textured.glb`, `out/run-log.md` (models used, effort, steps, what failed, and every
image-generation call; this skill makes none, and the log must say so).
Working files go in `out/work/`.

Rules: **never edit an output file by hand**, and never edit, flip or replace the reference images. Every change goes
through `parts.json` or a script option, and every build is logged. No AI 3D generation is used: the shape is your
blockout of simple solids, trimmed to the reference outlines by ordinary geometry code.

Paths below: `SKILL_DIR` is the folder this file is in (the base directory shown when the skill loads). `PY` is the
Python interpreter chosen in step 1; use it for every script.

## 1. Set up (about 1 minute)

1. If `python -c "import numpy, PIL, scipy, skimage"` succeeds, `PY` is `python`. Go to step 2.
2. Otherwise do not install into the system Python. Make a private environment in the working directory:
   ```
   python -m venv .venv-skill
   ```
   `PY` is then `.venv-skill/Scripts/python.exe` on Windows or `.venv-skill/bin/python` elsewhere. Run
   `PY -m pip install -r SKILL_DIR/requirements.txt` and check the import again with `PY`.
3. If this fails (no network, no pip), write that in `out/run-log.md` under "What failed" and stop.

## 2. Look and measure

1. Look at the four views and `final.png`. Decide what the animal is and list its parts as a modeller would:
   body, head, neck, snout or beak, ears, horns, limbs (one capsule per straight segment; a bent leg is two),
   feet, paws or toes, tail, fins, flippers, wings, shell, antennae, eye stalks. Note which are thin.
2. Run `PY SKILL_DIR/scripts/measure.py REFS out/work`. Open `out/work/ruler-front.png`, `ruler-side.png` and
   `ruler-top.png`: the references with a metric grid in model coordinates. Read `out/work/profiles.txt`: for
   each height (and, from the top view, each position along the body) it lists the solid stretches of the outline in
   metres. Two stretches at one height usually mean two parts (two legs, a flipper beside the body). Its last
   line, and `out/work/palette.png`, list the few colours the animal is painted in, as `#rrggbb` codes.
   Its **view check** (near the top) says whether the four views agree on the animal's size and pose. The pictures
   are AI-made and may not: a top view drawn at other proportions, a back view in another pose. If it names views
   to skip, pass `--skip-view` with them to every `blockout.py` and `build.py` run, so they neither pull parts out
   of place nor trim the model; model from the other views, and say so in the log. (The judges score the best two
   of the front, side and top views, so a skipped top view costs little.)
3. For small parts (beak, snout, mouth, toes, claws, eyes, ears, antler tines), make a close-up with a fine grid:
   `PY SKILL_DIR/scripts/measure.py REFS out/work --zoom side Y0 Z0 Y1 Z1` (front or back: X0 Z0 X1 Z1; top:
   X0 Y0 X1 Y1), which writes `out/work/zoom-side.png` (rename it before the next zoom of that view). The grid is
   every centimetre for a box up to 25 cm across, coarser for bigger boxes; keep boxes small to place small parts.
   The full rulers are too coarse to place a 2 cm part.

Model coordinates: metres; **z** up from the ground (feet at 0); **y** along the animal with the **nose at -y**;
**x** across, where image-right in the front view is +x. The animal is centred on x = 0 and on the middle of its
length. Read x and z from the front ruler, y and z from the side ruler, and check x and y on the top ruler.

## 3. Block out: write `out/work/parts.json`

```json
{"parts": [
 {"name": "body", "type": "ellipsoid", "center": [0, 0.05, 0.45], "radii": [0.12, 0.30, 0.14]},
 {"name": "neck", "type": "capsule", "a": [0, -0.18, 0.50], "b": [0, -0.30, 0.62], "ra": 0.08, "rb": 0.06, "blend": 0.05},
 {"name": "head", "type": "ellipsoid", "center": [0, -0.36, 0.66], "radii": [0.07, 0.10, 0.07], "rotate": [-15, 0, 0], "blend": 0.03},
 {"name": "ear", "type": "ellipsoid", "center": [0.04, -0.33, 0.74], "radii": [0.012, 0.03, 0.05], "rotate": [0, 15, 0], "mirror": true, "blend": 0.01},
 {"name": "front leg", "type": "capsule", "a": [0.07, -0.18, 0.40], "b": [0.07, -0.17, 0.03], "ra": 0.035, "rb": 0.025, "mirror": true, "blend": 0.03},
 {"name": "paw", "type": "ellipsoid", "center": [0.07, -0.19, 0.02], "radii": [0.03, 0.04, 0.02], "mirror": true, "blend": 0.01},
 {"name": "tail", "type": "capsule", "a": [0, 0.33, 0.50], "b": [0, 0.50, 0.35], "ra": 0.03, "rb": 0.015, "blend": 0.02}
]}
```
(An example dog-like animal, not the one you are modelling.)

Part types (all sizes in metres):
- `ellipsoid`: `center`, `radii` [x, y, z], optional `rotate` [degrees about x, then y, then z]. Bodies, heads,
  paws, eyes, and short flat wedges such as a bird's tail.
- `capsule`: a cone from `a` to `b`: a ball of radius `ra` at `a`, a ball of `rb` at `b`, joined smoothly. Round
  in cross-section, so for limbs, necks, toes, claws, horns, antennae, round tails; optional `aspect` (width /
  height of the cross-section, default 1: above 1 wider than tall, below 1 narrower) and `droop` (metres the tip
  hooks down) make it a jaw: an upper or lower beak, a snout, a muzzle.
- `paddle`: a flat tapered plate from its root `a` to its tip `b`: half-width `ra` at the root narrowing to `rb`
  at the tip, half-thickness `thick`, flat faces turned towards `normal` (default `[1, 0, 0]`, facing sideways),
  optional `bend` (metres the middle bows within the plate: a crescent flipper; negative bows towards the nose for
  a part on the +x side) and `curl` (metres the long edges curl back towards the body, so it wraps round it). For
  flippers, wings, fins, ears, flat fan tails: anything flat that grows out of the body at one end.
- `box`: `center`, `half` [x, y, z] (half-sizes), `round` (edge radius), optional `rotate`. Shells, flat or
  blocky parts.
- On any part: `"mirror": true` adds the matching part at -x (write the +x one); `"blend"`: size in metres of the
  rounded fillet where it meets the parts listed before it (0 = sharp; where two surfaces meet at a shallow angle
  the build automatically spreads the join out instead of adding a bulge); `"fit": false` stops the fitter from
  changing it; `"root_blend"` (capsules and paddles): a larger blend used only near the root `a`, so the part flows
  out of the body there and stays a separate shape everywhere else; `"colour"`: the part is one colour, either a
  `#rrggbb` code from the palette or `"drawn"` (see the colour rule below); `"ignore_views": ["back"]` (any of
  front, back, side, top) tells every script to ignore that reference view for this part, for a view that draws
  the part wrongly (see the last rule below).

Modelling rules that matter for how the result looks:
- One part per feature you can see. Visible toes, claws, nails, ears, horns, beaks and tails are their own parts
  (claws: a small tapered capsule at each toe tip); a smooth blob where the reference shows toes looks wrong.
- Parts on the centre line (head, beak, snout, neck, tail, a centre fin) must be written with x exactly 0 and not
  mirrored. The fitter then keeps them centred and straight; anything else can come out crooked.
- Size every part from the views that show it, in each direction: a beak's width from the front view, its depth
  and length from the side view. Too fat and it reads as a cone on a button; too thin and the fitter grows the head
  to cover the gap and the beak ends up a spike. The texture is projected from the pictures, so a part bigger or
  smaller than its drawn shape also gets the wrong colours (face black on the beak, beak red on the face).
- Mouths are two parts: an upper and a lower jaw. Build every beak, and any snout or muzzle where the pictures
  show a gape line, an open mouth or jaws of different shapes, as an upper jaw part and a lower jaw part, meeting
  along the gape line drawn in the side view. For a beak: an upper capsule from just inside the face to the tip,
  as deep at its base as drawn, with `droop` if the tip hooks; below it a shallower, slightly shorter, narrower
  lower capsule (`aspect` about 1, so it does not poke out sideways). Measure both on a `--zoom` of the side view;
  take their width from the front view. Put both on the centre line, with `"fit": false`. A closed mouth drawn as
  a line on a flat face (a cartoon face) is not modelled: leave it to the texture.
- When the front and side views disagree about where a small part sits (the front view draws the beak lower than
  the side view does), place it from the side view: a part pointing at the front camera is seen end-on there,
  squashed into its own base. The build never takes a part's colours from a camera its tip points at, nor the
  colours just around its base in that picture, so the disagreement does not paint the face.
- Place the head so nothing sticks out past the drawn throat and chin in the side view. Red under the beak or
  snout in `blockout-overlay.png` is the head sticking out; trimming flattens it into a dent in the chin. Move the
  head up and back, or tilt it, until the side overlay is clean there.
- Keep thin things thin: give a flipper, fin, wing or ear its thickness from the view where it looks thinnest.
  But nothing thinner than the fit report's minimum (about 1.5 build voxels, 3-4 mm on a 70 cm animal): thinner
  parts melt into blobs. For claws that small, use that minimum radius at the root.
- Feet, hands and paws: build them the way they are drawn: one capsule per toe or finger, all starting together at
  the ankle or wrist, with at most a small flat pad where they join. No big rounded foot blob under the toes: it
  reads as a slipper, and its large underside is seen by no picture, so it gets no real colour. Claws, nails and
  talons as long and as thick as drawn (measure them on the rulers), at each toe tip, pointing the way drawn
  (for example, curving down to the ground).
- Give one colour to parts that are one colour: claws, nails, toes, hooves, boots, belts, a shell, a single-coloured
  limb. Set `"colour"` to the palette code from `profiles.txt` (`"#2e2932"`); such a part keeps only the drawing's
  fine detail and cannot pick up a neighbour's colour from a drawing that sits a few millimetres off. Use
  `"drawn"` (the colour the pictures mostly show on it) only for a part the pictures see clearly and squarely; a
  part hidden or small in every picture (an inner toe behind the outer one) gets its shadow colour. Only give a
  part one colour if its edge is where the colour changes: a bird's leg capsule that runs up under the belly
  feathers would paint pink over the white feathers drawn hanging over it; leave such a part uncoloured, or make
  it end where the feathers begin.
- When two views disagree about how small parts are laid out (the claws spread twice as wide in the front view as
  in the top view), do not place them halfway: then they match neither picture, and both paint their claws onto
  the wrong spots. Lay them out from the view that shows them largest and least overlapped, and put the other view
  in those parts' `ignore_views`, so its differently placed toes and claws are neither fitted nor painted on. Say
  so in the log.
- Match the part's cross-section: capsules are round. Flippers, wings, fins and ears are flat and taper from a
  wide root to a narrow tip: use a `paddle`, not an ellipsoid. A flat ellipsoid is rounded at both ends and widest
  in the middle, so its top end stands out of the body as a lip and the whole thing reads as a panel set into a
  groove. A short flat tail is a flattened ellipsoid angled as the side view shows; a capsule there comes out as a
  stiff spike.
- A part that hangs free (flipper, wing, ear, tail fin, a limb held away from the body) grows out of the body only
  at its root. Put the paddle's root `a` just inside the body at the shoulder, give it `root_blend` of about
  0.04 of the animal's size and a small `blend` (about 0.005), and place the rest just outside the body: where the
  front view shows a gap, the same gap; where the drawing shows it lying against the body, touching but not sunk
  in. Use `curl` (about the plate's thickness) so a flipper lying against a round body wraps round it, and `bend`
  to follow a crescent outline. Check its outline in `parts-on-refs.png` against the side drawing: a few
  millimetres too far forward and the side picture paints the chest white onto it. Sunk half into the body along
  its length, it looks glued on (the fit report warns about this).
- A part that continues another (neck out of a body, head out of a neck, a fuller lower belly) must start inside
  it, narrower than the parent's cross-section where it starts, and get a generous blend: about half the smaller
  part's radius. If it is as wide as the parent there, its rounded end bulges out and prints a ring around the
  animal; then make the parent reach further instead.
- Build the trunk from as few thick parts as the outline needs: one body ellipsoid shaped (radii, tilt) to the whole
  torso is better than a stack. The build smooths the thick parts together as one form, which irons out small
  waists where they meet, but a lower part that is clearly wider than the one above it still reads as a hip
  bulge. Add a lower-body or neck part only where one ellipsoid cannot follow the outline.
- Show only what the references show. A bird's upper legs are inside the body feathers: keep leg capsules short
  and mostly inside the body, and if the body stops too high, add a broad lower-body ellipsoid so the belly comes
  down to where the feet appear. Visible stilts under a body look wrong.
- Legs drawn mid-stride: if `profiles.txt` shows a pair of legs as two separate stretches at the same height in the
  side view (one leg forward, one back), do not mirror that pair; a mirrored pair at the average position matches
  neither drawn leg. Write the two legs as separate parts, each at its own drawn position, with the forward one on
  whichever side the front or back view shows it (if they cannot tell, put it on the +x side). A lifted hoof or paw
  is drawn off the ground: keep it there.
- Antlers, horns and branching parts: one capsule per straight segment of the main beam and one per tine, each
  starting inside the segment it grows from, measured on `--zoom` close-ups of the front and side views. Thin
  branches that sit a little off their drawn place are kept by the build, but they paint and score better on it.
- Order: biggest first. Parts listed later blend into the ones before them.
- Check each part against every view it appears in. If one view clearly draws a part differently from the others
  (feet or toes pointing the other way, a limb in another pose), add that view to the part's `ignore_views` and say
  so in the log. Do not use it to get rid of a view that merely disagrees with your blockout, and do not put it on
  a big part (the body, the neck) to hide colour flecks: that throws away the view's colours for the whole part.
  Flecks mean a neighbouring part is in the wrong place; fix that part.

## 4. Fit and check the blockout (about 1-2 minutes per round, up to 3 rounds)

```
PY SKILL_DIR/scripts/blockout.py REFS out/work/parts.json out/work [--skip-view VIEW ...]
```
It nudges every part (within limits around what you wrote) to match the outlines and writes
`out/work/parts.fitted.json`, `fit-report.txt`, `blockout-overlay.png`, `blockout-parts.png`,
`parts-on-refs.png` and `parts-on-refs-detail.png`.

Open the four images and the report:
- `blockout-overlay.png`, per view: green = match, **blue = reference not covered** (a part is missing, too small or
  misplaced), **red = blockout sticks out** (a part too big, or one that should not be there), grey = ignored there
  (`ignore_views`).
- `parts-on-refs.png`: each reference picture with the outline of every part drawn on it, as that camera sees the
  parts. This is the only check for parts that lie inside the body's outline (a flipper or wing seen from the
  side, a beak or eyes seen from the front, toes in front of the belly, the tail seen from behind): the outlines
  cannot see them, so the fitter cannot place them. Each part's outline should sit on the shape drawn for it. Where
  it does not, move or resize the part (and usually give it `"fit": false`): the texture comes from these pictures,
  so a flipper drawn longer than the modelled one gets painted twice, once on the flipper and once on the body.
- `parts-on-refs-detail.png`: the same, zoomed in on each group of small parts (a foot with its toes and claws,
  the head and beak, the tail) in every view. Small parts are only a few pixels in the full sheet; check them
  here, part by part: every toe on a drawn toe and every claw on a drawn claw, in each view that is not ignored
  for them. A claw outline beside the drawn claw means that picture will paint its claw onto the toe instead.
- `blockout-parts.png`: the blockout in 3D, one colour per part. Check each part is doing its job: the beak is a
  beak (not a disc swelling out of the face), the legs are separate and straight down, nothing is floating.
- `fit-report.txt`: what the fitter changed, then **part checks**: parts too thin to survive the build, free parts
  lying glued along a bigger part, and parts sticking out of an outline. Deal with each one, or say in the log why
  it is fine. The fitter keeps each part within limits around what you wrote, but if it has turned a part into
  something else (a beak swollen to fill the head, a neck widened until it bulges out of the chest, a flipper
  shrunk into the body), set that part's size right in `parts.json` and add `"fit": false` to it.

To change the blockout: copy `parts.fitted.json` over `parts.json`, edit it (add, remove, move or resize parts)
and run the fit again. Aim for every view's overlap at 0.90 or more with no large blue or red areas, but do not
add parts that are not in the references just to cover an area.

## 5. Build (about 1 minute)

```
PY SKILL_DIR/scripts/build.py REFS out --parts out/work/parts.fitted.json [--skip-view VIEW ...] --note "why this run"
```
What it does:
- Shape: smooths the thick parts (body, belly, neck, head) together as one form, leaving thin parts exactly as
  written; trims the blockout where it sticks out of the outlines (by more than 1% of the animal's size on thick
  parts, closer on thin ones; notches and feather or fur wobble in the outlines are ironed out first), but never
  deletes most of a part: a part trimming would mostly remove is kept as written and reported; smooths it and
  removes loose fragments.
- Which picture colours each spot: one that sees it squarely (grazing views only where nothing better does), not
  one where the spot sits right next to another part, in large patches with their seams where neighbouring
  pictures agree. A feature two pictures would paint twice (an eye) is painted once. A paddle takes colours only
  from pictures that see its flat faces. A part whose tip points at a camera (a beak seen from the front) takes no
  colours from that camera, and neither does the area just around its base in that picture. A small mirrored
  group (one foot with its toes and claws) is coloured from at most two pictures. No picture colours surfaces facing
  downward (drawings show the shadow under a body there), a paddle's inner face (the side towards the body), or the
  body just beside a paddle away from its root (the drawings show the gap between them there). Tiny specks in a
  picture whose colour is far from every palette colour (a green fringe left in the cut-out) are ignored.
- Spots no picture colours are not guessed: each is flood-filled flat with the average colour of its part, taken
  per colour region from the area's border (white where it meets the white belly, black where it meets the black
  back), so it stays consistent with the figure.
- Texture: each part is unrolled along its own shape (tubes like sleeves, egg shapes like a world map) into one
  texture image, with the cuts on the back or underneath. Where a picture sees a spot squarely and away from other
  parts, the drawing is kept as drawn (eyes, faces, emblems, spots); elsewhere (slanted views, part edges,
  handovers between pictures) a colour plan takes over: the animal's few colours as
  smooth regions on each part, with the drawing's fine detail on top. Parts with a `"colour"` are painted in it.
  One picture's area fades into the next's over about a centimetre.

It writes `out/untextured.glb`, `out/textured.glb`, `out/preview-untextured.png`, `out/preview-textured.png`
(rendered pixel by pixel from the texture, as a model viewer shows it), `out/report.json` and a section of
`out/run-log.md`.

## 6. Review like a person would

Open the two previews next to the references. The model passes when:
- it is complete and recognisable: every part in the references is there, attached, on the correct side;
- centre-line parts are straight: the beak or snout points straight ahead, the tail straight back;
- the surface is smooth where the animal is smooth: no ridges, steps, rings at part joins, flat slabs, spikes or
  loose fragments;
- thin parts are thin; free-hanging parts stand off the body where the references show a gap; the underside is
  closed; nothing shows that the references hide (legs under feathers);
- each eye, marking and colour patch appears once, where the references have it, and no part carries another
  part's colour (black flipper smudges on a white chest, beak red on the face);
- `report.json` (the self-check runs the judges' scoring script, kit v0.2, against masks made from the references):
  `self_check.untextured_shape` is 0.85 or more, `self_check.gross_errors` is empty, `self_check.colour_score` is
  0.85 or more, and `warnings` is empty or dealt with. The judges' bar is 0.80 on shape and colour with their own
  masks; both scores are the mean of the best two of the front, side and top views, and a gross error (more than 2%
  of a view's picture wrong by more than 3% of the animal's size: a missing or misplaced head, foot, tail) fails
  the shape test whatever the score.

If it does not pass, fix the cause:

| What you see | Fix |
|---|---|
| a part missing, misplaced, too fat or too thin | edit `parts.json`, fit again (step 4), build again |
| a crease where two parts join | raise that part's `blend` (about half the smaller radius) |
| a ring or band around the body | a part that continues another bulges out of it: make it narrower where it starts, or let the parent reach further; `"fit": false` on it if the fitter widened it. If several stacked parts make the trunk, try fewer: one body ellipsoid shaped to the whole torso |
| a free-hanging part looks glued on, or like a panel with a groove round it | make it a `paddle` with its root inside the body, `root_blend`, the rest just outside the body, `curl` so it wraps round |
| a part drawn twice (a second flipper shape on the body), or its colour smeared onto a neighbour | in `parts-on-refs.png` the part misses its drawn shape: move or resize it to cover that shape |
| a part textured or shaped from a view that draws it wrongly | add that view to that part's `ignore_views` (that part only) |
| the beak or snout looks like a cone stuck on, or its colour is smeared onto the face | build it as an upper and a lower jaw measured on a `--zoom` of the side view, placed from the side view |
| a dent in the chin or throat under the beak or snout | the head sticks out past the drawn throat (red there in the side overlay): move the head up and back, or tilt it |
| a one-colour part (toe, claw, boot) is the wrong shade, or a neighbour's colour is on it | give it `"colour"` with the palette code; avoid `"drawn"` for parts the pictures barely see |
| a coloured part paints over something drawn on top of it (pink leg over white feathers) | end the part where the colour changes, or take its `"colour"` off |
| feet, hands or paws splotchy, or dark claw marks across the toes | in `parts-on-refs-detail.png` the toes and claws miss the drawn ones in some view: move them onto the drawing, or if two views disagree, follow the clearer one and ignore the other for those parts; drop any big foot-pad blob |
| outline match low in one view | look for blue in `blockout-overlay.png`; add or enlarge the part there |
| texture from the wrong view on a surface (e.g. back colours on the belly) | `--tol 2`; if hidden areas look wrong, `--tol 5` |
| warning: two views disagree on a size, or front and mirrored back differ | use `--skip-view` with the views measure.py's view check names, for the fit and the build |
| the model is shorter or smaller than the drawings, or parts are cut off | a view that disagrees was used for trimming: see the row above |
| warning: parts "kept untrimmed" | trimming would have removed most of them, so they are off their drawn place: move them onto the drawing (`parts-on-refs.png`, a `--zoom`) and build again |
| the blockout cannot be made to work after 3 rounds | fallback: `build.py REFS out --hull-only` (outline carving only; boxier, can invent stubs between legs), and say so in the log |

Do not raise `--grow` above 0: growing the blockout before trimming makes large flat, boxy faces.
Each build overwrites `out/`: finish with a build of the best version.

## 7. Finish the run log

Append to `out/run-log.md` (keep what the scripts wrote):

```
## Agent summary
- Models used: <your exact model name and version>, effort: <your reasoning effort setting>
- Animal: <what it is>, body plan, parts modelled (and any left out, with why)
- Blockout rounds: <n>, what changed each round; build runs: <n>, options of the final build
- Final self-check: shape <..>, gross errors <..>, colour <..>, per view IoU and colour <..>
- Image-generation calls: none (no AI image tool was used to repair or generate views)
- What failed or looks weak: <be specific: missing or simplified parts, texture seams, view disagreements>
```

Confirm `out/untextured.glb`, `out/textured.glb` and `out/run-log.md` exist before you stop.

## Budget

Measuring, each fit and each build take a minute or two and few tokens. Look at the rulers and any zooms once,
then at the overlay, `parts-on-refs.png`, `parts-on-refs-detail.png`, the parts preview and the two build
previews; do not read `.glb` files into context. Expect 15 to 30 minutes in all, well inside the 2-hour,
2.5-million-token limit.
