# Run log

## Pipeline run 2026-11-05 14:52:17

Why this run: round 3 blockout, quick build

- Command: `build.py refs/penguin out --parts out/work/parts.fitted.json --quick --note round 3 blockout, quick build`
- Shape: blockout (15 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (3.87 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: inner claw, middle claw, outer claw
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.17, 'back': 0.19, 'side': 0.205, 'side_mirror': 0.205, 'top': 0.022, 'unseen_filled': 0.208, 'duplicate_features_removed': 12, 'uv_islands': 24, 'texel_mm': np.float64(0.92), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.89 (textured 0.89), gross errors none, colour 0.895
- Warnings: none
- Time: 163.7 s

## Pipeline run 2026-11-05 14:57:08

Why this run: final full build of round 3 blockout

- Command: `build.py refs/penguin out --parts out/work/parts.fitted.json --note final full build of round 3 blockout`
- Shape: blockout (15 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (2.49 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: inner claw, middle claw, outer claw
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.168, 'back': 0.186, 'side': 0.202, 'side_mirror': 0.202, 'top': 0.022, 'unseen_filled': 0.221, 'duplicate_features_removed': 10, 'uv_islands': 24, 'texel_mm': np.float64(0.45), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.897 (textured 0.897), gross errors none, colour 0.901
- Warnings: none
- Time: 274.2 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: low (reasoning effort setting 15)
- Animal: Adélie-type penguin, upright egg-shaped body. Parts modelled: body ellipsoid + lower-body ellipsoid, head ellipsoid, upper and lower beak (centre line, fit off), flat tail paddle, two flipper paddles (root_blend, curl, bend), two short pink leg chains, a web paddle under each foot, three toe capsules per foot and a dark claw chain on each toe. Eyes are left to the texture (drawn on the head).
- Blockout rounds: 3.
  - Round 1: first blockout from the rulers and zooms; front/side 0.94. Claw capsules too thin for the grid, flippers started too low, tail too narrow.
  - Round 2: claws made into fine chains placed on the drawn claws, flippers re-placed from a side-view zoom (shoulder z 0.50 to tip z 0.18) with fit off, tail thickened. The fitter widened the body to 0.112 and swallowed the flippers.
  - Round 3: body locked at half-width 0.093 (fit off) so the flippers lie just outside it, leg roots moved deeper with root_blend, flipper root moved inward to clear the "root bulges" check. Part checks were clean after that.
- Build runs: 2 (one --quick, then the final full build with default options, no --skip-view).
- Final self-check: shape 0.897, gross errors none, colour 0.901. Per view IoU / colour: front 0.867 / 0.857, side 0.926 / 0.946, top 0.838 / 0.789, back 0.866 / 0.879 (not scored). Warnings: none.
- Image-generation calls: none (no AI image tool was used to repair or generate views).
- View disagreement: the top view draws the feet short and splayed outward (claws at x 0.06-0.10, y -0.09 to -0.11), unlike the front and side views (toes about 10 cm long, claws at x 0.01-0.11). The feet (leg, web, toes, claws) were laid out from the front and side views and have "top" in their ignore_views.
- What failed or looks weak: the upper third of each flipper merges into the body (it lies against the body at the shoulder in the drawings), so only the lower two thirds stands free. The top view's colour score (0.79) is lower because of the splayed feet it draws. The pink legs show a little higher under the belly feathers than drawn. Eyes are painted only, not modelled.
