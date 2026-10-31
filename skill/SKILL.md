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
| `front.png`, `side.png`, `back.png`, `top.png` | orthographic reference views of the animal, usually with a transparent background. A view may be missing (a turnaround sheet with no top view): the scripts then skip it everywhere on their own (not fitted, trimmed, painted or scored); model from the others and say so in the log |
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
   body (a loft, unless it really is an egg), head, neck, snout or beak, ears, horns, limbs and tails (a chain
   each, one joint at every bend), feet,
   paws or toes, tail tufts, fins, flippers, wings, shell, antennae, eye stalks. Note which are thin.
2. Run `PY SKILL_DIR/scripts/measure.py REFS out/work`. Open `out/work/ruler-front.png`, `ruler-side.png` and
   `ruler-top.png`: the references with a metric grid in model coordinates. Read `out/work/profiles.txt`: for
   each height (and, from the top view, each position along the body) it lists the solid stretches of the outline in
   metres. Two stretches at one height usually mean two parts (two legs, a flipper beside the body). A second
   side-view table goes along the body instead: at each y, the stretches up and down, which give a loft's stations
   (the torso's top and bottom at that y; where a leg joins, the belly is where the leg's stretch widens). Its last
   line, and `out/work/palette.png`, list the few colours the animal is painted in, as `#rrggbb` codes.
   Its **view check** (near the top) says whether the four views agree on the animal's size and pose. The pictures
   are AI-made and may not: a top view drawn at other proportions, a back view in another pose. A back view whose
   framing is only thrown off by something drawn in it alone (a tail hanging below the paws) is lined up with the
   front first and kept; the check says so, and the scripts use it lined up. If it names views
   to skip, pass `--skip-view` with them to every `blockout.py` and `build.py` run, so they neither pull parts out
   of place nor trim the model; model from the other views, and say so in the log. A skipped top view is still
   scored: the shape score takes the best two of the front, side and top views, but a gross error in any of them
   (the top included) fails the run. A top view drawn at other proportions (much longer than the side view) usually
   gives a gross error that no model true to the front and side views can avoid; say so in the log and in the final
   summary, and do not distort the model to chase it.
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
 {"name": "body", "type": "loft", "stations": [[0, -0.25, 0.45, 0.08, 0.10], [0, -0.12, 0.47, 0.11, 0.15], [0, 0.08, 0.46, 0.12, 0.13], [0, 0.25, 0.47, 0.10, 0.11]], "caps": [0.05, 0.06]},
 {"name": "neck", "type": "capsule", "a": [0, -0.18, 0.50], "b": [0, -0.30, 0.62], "ra": 0.08, "rb": 0.06, "blend": 0.05},
 {"name": "head", "type": "ellipsoid", "center": [0, -0.36, 0.66], "radii": [0.07, 0.10, 0.07], "rotate": [-15, 0, 0], "blend": 0.03},
 {"name": "ear", "type": "ellipsoid", "center": [0.04, -0.33, 0.74], "radii": [0.012, 0.03, 0.05], "rotate": [0, 15, 0], "mirror": true, "blend": 0.01},
 {"name": "front leg", "type": "chain", "joints": [[0.07, -0.18, 0.40, 0.035], [0.07, -0.16, 0.20, 0.025], [0.07, -0.17, 0.03, 0.02]], "mirror": true, "blend": 0.03},
 {"name": "paw", "type": "ellipsoid", "center": [0.07, -0.19, 0.02], "radii": [0.03, 0.04, 0.02], "mirror": true, "blend": 0.01},
 {"name": "tail", "type": "chain", "joints": [[0, 0.30, 0.50, 0.03], [0, 0.42, 0.46, 0.02], [0, 0.50, 0.35, 0.012]], "blend": 0.02}
]}
```
(An example dog-like animal, not the one you are modelling.)

Part types (all sizes in metres):
- `loft`: a torso built slice by slice. `stations`: [x, y, z, half_width, half_height] from the front end to the
  back end (y increasing); each is an upright slice across the body at that y, an ellipse `half_width` wide and
  `half_height` tall around (x, z), and a smooth surface runs through them. `caps`: [front, back] metres the ends
  round off past the first and last station (0: as far as the end slice is thin). For the torso of any animal
  that is not simply an egg: the back can slope from high withers, the belly tuck up, the chest be deep and narrow,
  the rump round off, all in one part. Not for necks or anything running steeply up or down.
- `ellipsoid`: `center`, `radii` [x, y, z], optional `rotate` [degrees about x, then y, then z]. Round bodies, heads,
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
- `chain`: a limb, tail or neck grown joint by joint, the way a modeller extrudes one. `joints`: a list of
  [x, y, z, radius] from the root (inside the part it grows from) to the tip, one joint at every bend (hip, knee,
  hock, fetlock; the base, middle and end of a tail). Neighbouring joints are joined by round cones, so the
  segments always meet; the fitter moves a joint and both segments that share it. Optional `aspect` as for a
  capsule. A chain thinner than about three build voxels anywhere (a tail strand, a giraffe's lower leg) is built
  on its own grid three times finer and joined on, together with whatever hangs from it alone (the tuft at the
  end of the tail, the hoof under the leg), so it cannot break off; `"fine": true` forces that on any part.
- `box`: `center`, `half` [x, y, z] (half-sizes), `round` (edge radius), optional `rotate`. Shells, flat or
  blocky parts.
- On any part: `"mirror": true` adds the matching part at -x (write the +x one); `"blend"`: size in metres of the
  rounded fillet where it meets the parts listed before it (0 = sharp; where two surfaces meet at a shallow angle
  the build automatically spreads the join out instead of adding a bulge); `"fit": false` stops the fitter from
  changing it; `"root_blend"` (capsules, paddles, chains): a larger blend used only near the root, so the part flows
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
- Muzzles (dogs, cats, horses, cattle, bears: any furred snout) are not beaks. The upper jaw is the snout itself: one
  broad capsule from inside the head to the nose, as wide as the front view draws it (`aspect` above 1), its top
  following the drawn bridge and its underside the drawn upper lip; no `droop`. The nose is its own small ellipsoid
  at the tip, coloured with the palette's darkest code, and the snout must end inside it (the nose is the tip):
  a snout reaching past the nose shows its own pale end around it. A closed mouth: the lower jaw tucked right under the snout, touching it all
  along. An open mouth: the lower jaw as drawn, touching the snout at the mouth corner and opening towards the
  front only as far as drawn; then a mouth part between the two jaws, a capsule from the corner to just behind the
  lips, a centimetre narrower than the jaws on each side, coloured with the palette's darkest code: without it the
  gap between the jaws is a hole you can see straight through. A wide open grin (most dogs drawn panting) is as wide
  as the front view draws it between the mouth corners: give the lower jaw the drawn chin's width (`aspect` about
  1.5-2; a narrow jaw tapering to a point leaves a round "O" of a mouth from the front), the snout an `aspect` of
  about 1.6 so its underside covers the mouth part, and the mouth part `aspect` about 2. A mouth part wider than
  the jaws at its height sticks out of the lips as a dark flange. A tongue on top of it if drawn (`"colour":
  "drawn"`), as wide as drawn (`aspect` about 2.5), reaching out over the lower lip as far as the side view draws it. If the front view draws the nose higher or lower than the
  side view (by more than about half the nose's height), place it from the side view and put "front" in the nose's
  and snout's `ignore_views`, or the front picture paints its nose across the upper lip.
- Long faces (cattle, horses, deer, sheep, goats, camels): there is no step between forehead and nose, and the
  head tapers from the skull to the muzzle. Build skull and snout as one `capsule` "head": `a` at the poll (between
  the ear or horn roots, inside the top of the neck), `b` just behind the nose, `ra` and `rb` half the head's
  drawn depth there, so its top runs along the drawn forehead line and its underside along the cheek; `aspect`
  = the front view's head width at the eyes / the side view's depth there (about 1.1-1.2, never so wide that it
  reaches where the ears are drawn). A round skull ellipsoid with a snout capsule on it gives a dished, dog-like
  face with a dip where they meet, and the fitter widens the round skull into the space the ears are drawn in.
  Under it, a lower jaw capsule from the jaw angle to the chin, as wide as the front view draws the chin (`aspect`
  1.3-1.6): it must not taper to a point. The nose pad is an ellipsoid on the front of the head's tip, as wide as
  drawn and standing 1-2 cm proud of it, in the drawn nose colour (`"drawn"` for a pink or pale nose). Give the
  head, jaw and nose `"fit": false`.
- Ears are paddles, mirrored, with `root_blend`, sized and turned as drawn (`--zoom` the front and side views):
  - Ears that stick out (cattle, horses, deer, cats, foxes): leaf-shaped, narrow at the root and widest
    two-thirds out, so `ra` small at the root and `rb` the drawn half-width, with `b` that far in from the tip;
    the flat side faces the camera that sees the ear's full shape (`normal` mostly [0, 1, 0] when the front view
    shows it broad).
  - Hanging ears (most dogs, lop rabbits): the root high on the side of the skull, `b` low beside the cheek where
    the front view draws the ear's bottom (the rounded tip reaches `rb` below `b`), the flat side facing outward
    (`normal` mostly [1, 0, 0], tilted up a little as the ear leans out), lying against the head with a little
    `curl`. Turned towards the front it stands off the head like a horn from above.
  - Size the head without them: if the head ends up covering where the ears are drawn, it is too wide.
- When the front and side views disagree about where a small part sits (the front view draws the beak lower than
  the side view does), place it from the side view: a part pointing at the front camera is seen end-on there,
  squashed into its own base. The build never takes a part's colours from a camera its tip points at, nor the
  colours just around its base in that picture, so the disagreement does not paint the face.
- Place the head so nothing sticks out past the drawn throat and chin in the side view. Red under the beak or
  snout in `blockout-overlay.png` is the head sticking out; trimming flattens it into a dent in the chin. Move the
  head up and back, or tilt it, until the side overlay is clean there.
- Keep thin things thin: give a flipper, fin, wing or ear its thickness from the view where it looks thinnest.
  But nothing thinner than the fit report's minimum (about 1.5 build voxels, 3-4 mm on a 70 cm animal): thinner
  parts melt into blobs. For claws that small, use that minimum radius at the root. Round parts that are long and
  thin (tails, tail strands, slim legs, antennae, whiskers) are chains: those are built on a finer grid, so they can
  be as thin as drawn (down to a third of that minimum).
- Tails: one chain from inside the rump to the tip, as thick as drawn all the way. A tuft or switch at the end is
  a second chain (or an ellipsoid) that starts inside the tail's last joint, with its own `"colour"`; it is built
  together with the tail. Give a hairy tuft `"strands"` (6-10) so it ends in a ragged brush, and put "top" in its
  `ignore_views` when it hangs under the tail: from above it is hidden under the tail, and the top view would trim
  it to the tail's width, a flat blade. Do not exempt a tail from a view's trimming to keep it: if it breaks off, it is not a
  chain, or does not start inside the rump.
- Feet and hands with separate toes or fingers (birds, lizards, frogs, hands): build them the way they are drawn:
  one capsule per toe or finger, all starting together at the ankle or wrist, with at most a small flat pad where
  they join. No big rounded foot blob under the toes: it reads as a slipper, and its large underside is seen by no
  picture, so it gets no real colour. Claws, nails and talons as long and as thick as drawn (measure them on the
  rulers), at each toe tip, pointing the way drawn (for example, curving down to the ground).
  Webbed feet (penguins, ducks, geese, frogs) are the exception: where the drawing shows skin joining the toes,
  add one flat `paddle` per foot under them, `normal` [0, 0, 1], `a` at the ankle (`ra` about the ankle's
  half-width), `b` a little short of the toe tips (`rb` about half the spread between the outer toes there),
  `thick` about half the toes' thickness, with the toes' `"colour"`. The toes then stand on it as ridges; without
  it the foot reads as three bare sticks.
- Long fur (retrievers, setters, collies, long-haired cats, manes): the outline the drawings show is the fur, not
  the body under it, so size the body, neck and limbs to the fur's outer edge, and add the fur that hangs off them
  as its own parts, measured on `--zoom` close-ups of the side and front views: feathering behind the front legs
  and trousers on the back of the thighs as `paddle`s with `normal` [1, 0, 0] (flat sides facing sideways,
  `thick` 1.5-3 cm), from inside the leg out to the drawn fringe; a chest ruff as a small ellipsoid under the
  throat; a mane as a chain along the top of the neck with `aspect` below 1 (taller than wide). Compare the
  build's outline with the drawing: wherever the drawing is wider than the model in the side view behind a leg,
  under the chest or along the neck, fur is missing there. A fatter tail or leg is not the fix if its other
  views are narrower: trimming then cuts it into flat facets.
- Hooves are wedges, not balls: in the side view the front wall slopes from the coronet down to the toe, the sole is
  flat on the ground and the heel is lower than the coronet. Build each claw as a `paddle` with `normal` [1, 0, 0]
  (flat sides facing sideways): `a` at the heel's centre, `b` near the toe on the ground (the rounded tip reaches
  `rb` beyond it), `ra` half the heel's height, `rb` small, `thick` half the claw's width from the front view,
  with the hoof's `"colour"`. Cloven hooves (cattle, deer, sheep, goats, pigs, giraffes): two such claws per foot,
  side by side either side of the leg's centre with a small cleft between them; horses: one, as wide as the hoof.
  Start them inside the leg chain's last joint; trimming to the side view flattens the sole.
- Furred paws (dogs, cats, bears, rabbits) are the opposite: the toes are packed together into one compact foot.
  Build the paw as one ellipsoid as long, wide and tall as drawn (`--zoom` the front and side views; its width is
  the span of the toes in the front view, not the fur above them), the leg running down into its back half; then
  one small ellipsoid per drawn toe across its front edge in an arc (the middle two furthest forward), each about
  a quarter of the paw's width, with its front third standing out of the paw's front edge, so the toes show from
  the front as lobes with grooves between them. Toes buried in a paw wider than they are show only as bumps on its
  sides, and the paw reads as a boot. Where the drawing shows dark claw tips at the front of the toes (most dogs
  do), add each as a short chain from inside its toe's front, a few millimetres out and down to the ground, with
  the claw colour; claws reaching forward read as pegs. Toe capsules sticking out of a paw read as sausages.
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
  animal; then make the parent reach further instead. A neck joining a four-legged body needs more: a blend about
  as big as its root radius, and its root as wide as the front view draws the neck where it meets the shoulders
  (`aspect` about 0.9-1.1; a neck much narrower than tall sits on the chest as an oval patch with a groove round it).
- The torso is one `loft` (an ellipsoid only when the body really is an egg, as a penguin's is). Put a station
  wherever the outline changes: the front of the chest, behind the front legs, the withers or shoulders, mid
  barrel, the flank in front of the hind legs, the hips, the back end of the rump; 5 to 8 stations. Read each one's
  top and bottom from profiles.txt's side table at its y (half_height = half the gap, z = the middle) and its width
  from the top view (from the front view if the top is skipped: the widest stretch at the torso's heights, narrower
  towards the chest and rump). Shoulders, withers and hump belong in the loft, not in extra parts. A neck or head
  then grows out of it as usual. Several thick parts stacked along the body are worse than one loft: the build
  smooths them together, but where one is clearly wider than the next it still reads as a bulge or a ring.
- Show only what the references show. A bird's upper legs are inside the body feathers: keep leg capsules short
  and mostly inside the body, and if the body stops too high, add a broad lower-body ellipsoid so the belly comes
  down to where the feet appear. Visible stilts under a body look wrong.
- Four-legged animals: a leg is not a thin tube hanging from the belly. The upper leg (thigh, shoulder) is a big
  mass that flows out of the body: in the back view a hoofed animal's hind thighs fill the whole width of the rump
  down to the hocks, and in the side view they run from the hip down to the hock. Build each upper leg as a wide
  tapered capsule from inside the body at the hip or shoulder down to the hock or knee (radius about half the
  rump's half-width at the top; `aspect` about 0.7 when it is longer front-to-back than it is wide, which it
  usually is), with `blend` about 0.1 of the animal's height, then the lower leg as one chain from inside the
  upper leg's lower end through the knee or hock and the fetlock down to the hoof or paw (an ellipsoid with its
  own `"colour"`, starting inside the chain's last joint). Read the widths off the back and front views (`profiles.txt` lists the front; a `--zoom` of the
  back view shows where the thighs end).
  Give the lower-leg chain a joint at every bend and bulge the side view draws: for a front leg the elbow
  (inside the body or upper leg), mid-forearm, knee, mid-cannon, fetlock and the top of the hoof; for a hind leg
  the stifle (inside the thigh), hock, mid-cannon, fetlock and the top of the hoof. The hock is the hind leg's
  backmost point, so its joint sits behind the ones above and below it, and the pastern slopes forward from the
  fetlock to the hoof. Read each joint's radius from the widths in `profiles.txt`'s side table at its height
  (half the leg's stretch): the knee, hock and fetlock come out a little thicker than the cannon between them.
  Three or four evenly spaced joints make a straight, smooth stick.
  The two pieces must meet: the upper leg's tip end (`b`) on the lower-leg chain's first joint, its `rb` about
  that joint's radius. Whenever you move one (pinning a lower leg to measured joints, say), move the other with it.
  An upper leg that runs on past the lower leg's start, or stops short of it, sits beside the leg as a lump and
  sticks out sideways at the hip or shoulder; the fit report names such legs ("starts ... from the end of").
  Start every upper leg deep: its root (`a`, or a chain's first joint) at least its root radius in from the body's
  surface, towards the middle of the body rather than just under its side. A root just under the surface shows the
  back of its rounded end as a lump at the shoulder or hip, with a crease round it; the fit report names such
  roots ("bulges ... out of the body"). The same goes for the neck and the tail.
- Chest, brisket, dewlap: no separate ball on the chest. If the front view shows a chest or brisket in front of
  the shoulders, make it no wider than the front view draws it (usually about half the body's width) and give
  it, the neck and the body generous blends (from 0.2 up to half the neck's radius); otherwise let
  the body and neck form the chest. A ball as wide as the body reads as a goitre from the front.
- Legs drawn mid-stride: if `profiles.txt` shows a pair of legs as two separate stretches at the same height in the
  side view (one leg forward, one back), do not mirror that pair; a mirrored pair at the average position matches
  neither drawn leg. Write the two legs as separate parts, each at its own drawn position, with the forward one on
  whichever side the front or back view shows it (if they cannot tell, put it on the +x side). A lifted hoof or paw
  is drawn off the ground: keep it there.
- Antlers, horns and branching parts: the main beam as a chain (a joint wherever it bends) and one capsule or
  chain per tine, each starting inside the beam, measured on `--zoom` close-ups of the front and side views. Thin
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
and run the fit again. Aim for the front and side overlaps at 0.90 or more with no large blue or red areas, but do
not add parts that are not in the references just to cover an area.

The shape and colour scores use the best two of front, side and top. Get front and side right first. The top view
only needs to stay clear of gross errors: do not move parts away from the front and side drawings to fit a top
view that draws them differently (flippers swept back, feet splayed, a wider head).

## 5. Build (about 1 minute)

```
PY SKILL_DIR/scripts/build.py REFS out --parts out/work/parts.fitted.json [--skip-view VIEW ...] --note "why this run"
```
What it does:
- Shape: smooths the thick parts (body, belly, neck, head) together as one form, leaving thin parts exactly as
  written; builds thin chains, and what hangs from them, on a three times finer grid and joins them on with their
  blend (the method line in `report.json` names them); trims the blockout where it sticks out of the outlines (by more than 1% of the animal's size on thick
  parts, closer on thin ones; notches and feather or fur wobble in the outlines are ironed out first), but never
  deletes most of a part: a part trimming would mostly remove is kept as written and reported. Where the top or
  back view alone would cut deep into a part the front and side draw whole (a top view drawn with the rump 15 cm
  short), that view is ignored for that part, and the build lists it under warnings. Then it smooths the model and
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
  back), so it stays consistent with the figure. Only the fine strokes of the drawing (fur, feathers, scales) are
  borrowed on top, from a patch of the same colour region that a picture sees squarely, so a filled belly does not
  look like plastic beside drawn fur.
- Texture: each part is unrolled along its own shape (tubes like sleeves, egg shapes like a world map) into one
  texture image, with the cuts on the back or underneath. Where a picture sees a spot squarely and away from other
  parts, the drawing is kept as drawn (eyes, faces, emblems, spots); elsewhere (slanted views, part edges,
  handovers between pictures) a colour plan takes over: the animal's few colours as
  smooth regions on each part, with the drawing's fine detail on top. Parts with a `"colour"` are painted in it.
  One picture's area fades into the next's over about a centimetre.

It writes `out/untextured.glb`, `out/textured.glb`, `out/preview-untextured.png`, `out/preview-textured.png`
(rendered pixel by pixel from the texture, as a model viewer shows it), `out/report.json` and a section of
`out/run-log.md`. For troubleshooting the shape it also writes `out/parts-coloured.glb` and
`out/preview-parts.png`: the same mesh with every part in its own flat colour (the body grey, the key under the
preview), each triangle coloured by the part it lies nearest to. They are not scored, and `textured.glb` keeps
its real texture.

## 6. Review like a person would

Open the two previews next to the references, and `preview-parts.png` to see which part made which bit of the
surface: the texture can hide a shape fault that the part colours show at once (a part swallowed by its
neighbour, a part spreading over where another is drawn, a joint in the wrong place). The model passes when:
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
| in `preview-parts.png` a part hardly shows (swallowed by the body or a neighbour), or spreads over where another part is drawn | the swallowed part is too small or too deep inside, or the other too big: resize or move them so each covers its own drawn place |
| a lump at the shoulder, hip, chest or tail root, or the fit report says a root "bulges out of the body" | start that part deeper inside the body (its root at least its root radius in) and give it `root_blend`; if the drawing really is wider there, widen the loft's stations instead |
| the neck sits on the chest as an oval patch, or a ring or groove runs round its base | widen the neck's root to the drawn width and raise its blend to about its root radius |
| a crease where two parts join | raise that part's `blend` (about half the smaller radius) |
| a ring or band around the body | a part that continues another bulges out of it: make it narrower where it starts, or let the parent reach further; `"fit": false` on it if the fitter widened it. If several stacked parts make the trunk, replace them with one `loft` |
| the body looks like an egg or a barrel: no sloping back, no tucked belly, widest in the middle from every side | make the torso a `loft`, with stations read off the side table where the outline changes |
| a free-hanging part looks glued on, or like a panel with a groove round it | make it a `paddle` with its root inside the body, `root_blend`, the rest just outside the body, `curl` so it wraps round |
| a part drawn twice (a second flipper shape on the body), or its colour smeared onto a neighbour | in `parts-on-refs.png` the part misses its drawn shape: move or resize it to cover that shape |
| a part textured or shaped from a view that draws it wrongly | add that view to that part's `ignore_views` (that part only) |
| the beak or snout looks like a cone stuck on, or its colour is smeared onto the face | build it as an upper and a lower jaw measured on a `--zoom` of the side view, placed from the side view |
| an open mouth looks like a round "O" from the front, or a dark flange sticks out of the lips | widen the lower jaw and snout to the drawn mouth width and keep the mouth part just inside them (see the muzzle rule) |
| you can see through an open mouth, or the nose colour is smeared over the muzzle | a furred muzzle: add the dark mouth part between the jaws and a nose part; if the front view draws the nose elsewhere, ignore the front view for the nose and snout (see the muzzle rule) |
| a cow's, horse's or deer's face looks dished, pointed or dog-like, or the head is wider than drawn | build the head as one long tapered capsule with a broad lower jaw and a nose pad (see the long-face rule) |
| ears too small, hidden in the head, or sticking out like horns from above | resize and turn them as in the ear rule; if the fit report says the head grew by 20% or more, put it back and give it `"fit": false` |
| legs look like straight sticks: no knees, hocks or fetlocks | a joint at every drawn bend and bulge, radii read off the side table (see the four-legged rule) |
| a leg has a lump or kink partway down, or the rump or shoulders look fat with a lobe sticking out sideways; fit report: a lower leg "starts ... from the end of" an upper leg | the two pieces do not meet: put the upper leg's `b` on the lower chain's first joint, `rb` about that joint's radius |
| a webbed foot (penguin, duck, frog) looks like bare separate toes | add the web paddle under the toes (see the feet rule) |
| long-haired animal looks shaved: smooth legs, no feathering, no ruff, slimmer than drawn behind the legs | add the fur parts (see the long-fur rule) |
| hooves look like round knobs | build them as wedge-shaped claws (see the hoof rule) |
| paws look like boots with sausage toes, or toes show only as bumps on the paw's sides | a furred paw: one paw ellipsoid as wide as the drawn toes, with toe lobes in an arc standing out of its front edge, and short claws where drawn (see the paw rule) |
| a dent in the chin or throat under the beak or snout | the head sticks out past the drawn throat (red there in the side overlay): move the head up and back, or tilt it |
| a one-colour part (toe, claw, boot) is the wrong shade, or a neighbour's colour is on it | give it `"colour"` with the palette code; avoid `"drawn"` for parts the pictures barely see |
| a coloured part paints over something drawn on top of it (pink leg over white feathers) | end the part where the colour changes, or take its `"colour"` off |
| feet, hands or paws splotchy, or dark claw marks across the toes | in `parts-on-refs-detail.png` the toes and claws miss the drawn ones in some view: move them onto the drawing, or if two views disagree, follow the clearer one and ignore the other for those parts; drop any big foot-pad blob |
| outline match low in one view | look for blue in `blockout-overlay.png`; add or enlarge the part there |
| texture from the wrong view on a surface (e.g. back colours on the belly) | `--tol 2`; if hidden areas look wrong, `--tol 5` |
| warning: two views disagree on a size, or front and mirrored back differ | use `--skip-view` with the views measure.py's view check names, for the fit and the build |
| the model is shorter or smaller than the drawings, or parts are cut off | a view that disagrees was used for trimming: see the row above |
| warning: a loose piece came off and was dropped, or fit report: parts "not joined to the body" | a part (tail, tuft, ear, horn) hangs on only where trimming cuts it: start it inside the part it grows from; make a thin tail, strand or leg a chain, with its tuft or hoof starting inside its last joint |
| fit report: a part "grew by 20% or more" | it is filling in for another part (ears beside the head, a neck too thin under it): fix that part, put this one's size back and give it `"fit": false`. Refitting the fitted file lets it grow 25% again every round |
| warning: parts "kept untrimmed" | trimming would have removed most of them, so they are off their drawn place: move them onto the drawing (`parts-on-refs.png`, a `--zoom`) and build again |
| the blockout cannot be made to work after 3 rounds | fallback: `build.py REFS out --hull-only` (outline carving only; boxier, can invent stubs between legs), and say so in the log |

Builds while you are still changing the blockout can add `--quick` (coarser mesh, smaller texture, about a fifth
of the time, nearly the same scores); the final build must be without it. Thin chains are built fine in quick
builds too, but a thin part that is not a chain can break off in a quick build; judge those on the full build.
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
then at the overlay, `parts-on-refs.png`, `parts-on-refs-detail.png`, the parts preview and the three build
previews; do not read `.glb` files into context. Expect 15 to 30 minutes in all, well inside the 2-hour,
2.5-million-token limit.
