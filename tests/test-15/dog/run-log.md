# Run log

## Pipeline run 2026-11-09 22:30:28

Why this run: round 3: quick build

- Command: `build.py refs/dog out/dog --parts out/dog/work/parts.fitted.json --skip-view back --quick --note round 3: quick build`
- Shape: blockout (32 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (5.88 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: front claw inner, front claw mid inner, front claw mid outer, front claw outer, hind claw mid inner, hind claw mid outer
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.086, 'back': 0.051, 'side': 0.245, 'side_mirror': 0.245, 'top': 0.102, 'unseen_filled': 0.272, 'duplicate_features_removed': 8, 'uv_islands': 48, 'texel_mm': np.float64(2.26), 'palette_colours': 4}
- Self-check (own masks, kit v0.2 scorer): shape 0.932 (textured 0.932), gross errors none, colour 0.895
- Warnings: front and mirrored back outlines overlap only 0.88, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): hind thigh: top; hind toe outer: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): hind toe outer
- Time: 120.7 s

## Pipeline run 2026-11-09 22:38:32

Why this run: final: hind legs/paws in palette gold (only the skipped back view sees them)

- Command: `build.py refs/dog out/dog --parts out/dog/work/parts.final.json --skip-view back --note final: hind legs/paws in palette gold (only the skipped back view sees them)`
- Shape: blockout (32 parts from parts.final.json) grown 0.0 mm, trimmed to the outlines (3.78 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: front claw inner, front claw mid inner, front claw mid outer, front claw outer, hind claw mid inner, hind claw mid outer
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.084, 'back': 0.05, 'side': 0.246, 'side_mirror': 0.244, 'top': 0.104, 'unseen_filled': 0.272, 'duplicate_features_removed': 8, 'uv_islands': 48, 'texel_mm': np.float64(1.11), 'palette_colours': 4}
- Self-check (own masks, kit v0.2 scorer): shape 0.934 (textured 0.934), gross errors none, colour 0.891
- Warnings: front and mirrored back outlines overlap only 0.88, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): hind thigh: top; hind toe outer: top
- Time: 422.1 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: reasoning effort 30
- Animal: Golden retriever; long-haired quadruped with an open mouth and tongue
- Parts modelled: loft body, neck, chest ruff, skull, snout, nose, lower jaw, mouth, tongue, hanging ears, front lower legs, front feathering, hind thighs, hind lower legs, trousers, paws with 4 toes, claws on the front paws and two per hind paw, tail. The front upper legs were removed because they sat entirely inside the body.
- Blockout rounds: 3 blockout rounds: 1 first fit; 2 fixed an overgrown neck that swallowed the head, turned the ears, joined thighs to lower legs; 3 ended the snout inside the nose, pulled the hind paws in, rooted limbs deeper.
- Build runs: 1 quick and 1 full build; final options: --skip-view back (measure.py's view check named it).
- Final self-check: shape 0.934, gross errors [], colour 0.891; front IoU 0.925 colour 0.871, back IoU 0.771 colour 0.866, side IoU 0.944 colour 0.895, top IoU 0.908 colour 0.887
- Image-generation calls: none (no AI image tool was used to repair or generate views)
- What failed or looks weak: Back view skipped (different pose: the tail hangs to the ground there). Hind legs and paws are flat palette gold because only the skipped back view would colour them. Fur tufts along the legs are painted, with only the paddles for shape. Hind paws: the top view does not draw them, so it is ignored for those parts. Far paws are mirrored from the near ones, because the side view's offset is mostly perspective.
- Remaining warnings from the build: ['front and mirrored back outlines overlap only 0.88, even lined up as well as they can be: pose differs between views', 'views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): hind thigh: top; hind toe outer: top']
