# Run log

## Pipeline run 2026-11-10 17:44:02

Why this run: first quick build after 4 blockout rounds

- Command: `build.py refs/penguin out --parts out/work/parts.fitted.json --quick --note first quick build after 4 blockout rounds`
- Shape: blockout (15 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (3.87 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: inner claw, middle claw, outer claw
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.171, 'back': 0.183, 'side': 0.201, 'side_mirror': 0.201, 'top': 0.021, 'unseen_filled': 0.224, 'duplicate_features_removed': 12, 'uv_islands': 24, 'texel_mm': np.float64(0.99), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.911 (textured 0.911), gross errors none, colour 0.888
- Warnings: none
- Time: 92.1 s

## Pipeline run 2026-11-10 17:49:09

Why this run: final full build: lower beak lowered to show below upper beak

- Command: `build.py refs/penguin out --parts out/work/parts.fitted.json --note final full build: lower beak lowered to show below upper beak`
- Shape: blockout (15 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (2.49 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: inner claw, middle claw, outer claw
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.169, 'back': 0.183, 'side': 0.2, 'side_mirror': 0.2, 'top': 0.021, 'unseen_filled': 0.226, 'duplicate_features_removed': 12, 'uv_islands': 24, 'texel_mm': np.float64(0.48), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.917 (textured 0.917), gross errors none, colour 0.884
- Warnings: none
- Time: 269.5 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: low
- Animal: Adélie-type penguin. Upright egg body (tilted ellipsoid plus a lower-belly ellipsoid), head ellipsoid, upper and lower beak capsules, mirrored paddle flippers, short legs mostly inside the belly feathers, webbed feet (web paddle plus three toe capsules and three claw chains each), and a wedge tail. Eyes and the white eye-ring are left to the texture (flat on the face).
- Blockout rounds: 5. (1) First fit: the fitter dragged the flipper root forward onto the white chest, so the flipper was placed by hand from the side-view colour table with `fit: false`, and the outer toe and claw were pulled in. (2) Toes thickened to the drawn depth; "top" added to `ignore_views` for toes, claws and web: the top view draws the feet splayed outward and the inner toes hidden under the chest, while the front view shows all three claws clearly. (3) Tried narrowing the body to free the flippers: front overlap fell from 0.93 to 0.90 and the flipper stuck out at the shoulder, so this was reverted. (4) Flipper root moved slightly outward with more curl. (5) Lower beak lowered so it shows under the upper beak.
- Build runs: 2. One `--quick`, then the final full build with default options (no `--skip-view`, `--tol` or `--grow`).
- Final self-check: shape 0.917, gross errors none, colour 0.884. Per view IoU / colour: front 0.910 / 0.827, side 0.925 / 0.941, top 0.832 / 0.782, back 0.911 / 0.881 (not scored). Warnings: none.
- Image-generation calls: none (no AI image tool was used to repair or generate views).
- What failed or looks weak: the flipper's upper third lies against the body (fit report: 33% sunk past the root). The body cannot narrow at the shoulders without losing the front outline, so only the lower two-thirds stands clear and the shoulder end is mostly texture. In the top view, the foot layout follows the front view, not the top view's splayed toes. The front view draws the beak lower than the side view does, and the beak is placed from the side view. Front colour (0.83) is the weakest score, mostly at the flipper edges and the feet.
