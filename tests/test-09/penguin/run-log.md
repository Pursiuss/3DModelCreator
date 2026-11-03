# Run log

## Pipeline run 2026-10-30 20:42:36

Why this run: penguin round 3 blockout, full build

- Command: `build.py refs/penguin out/penguin --parts out/penguin/work/parts.fitted.json --note penguin round 3 blockout, full build`
- Shape: blockout (13 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (2.49 mm voxels), smoothed; kept 1 of 1 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.203, 'back': 0.218, 'side': 0.204, 'side_mirror': 0.204, 'top': 0.025, 'unseen_filled': 0.146, 'duplicate_features_removed': 6, 'uv_islands': 21, 'texel_mm': np.float64(0.51), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.903 (textured 0.903), gross errors none, colour 0.873
- Warnings: views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): outer toe: top; outer claw: top
- Time: 106.0 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: low
- Animal: Adélie-type penguin, upright egg body. Parts: body (tilted ellipsoid), head, upper and lower beak, two paddle flippers, flattened tail wedge, two short legs, three toes and three claws per foot. Eyes left to the texture.
- Blockout rounds: 4. Round 1: first fit (front 0.94 / side 0.93), but the flippers came out too short and pulled off the body. Round 2: longer flippers with fixed size, toes and claws pinned. The fitter then widened the body and swallowed the flippers. Round 3: body width fixed at 0.097 m; flippers sat inside the outline. Round 4: body 0.104 m and flippers moved out to the drawn edge, with no part-check problems left. Build runs: 1 (full, no --quick, no skipped views).
- Final self-check: shape 0.903, gross errors none, colour 0.873. IoU/colour: front 0.903/0.826, side 0.904/0.919, top 0.842/0.768, back 0.905/0.881.
- Image-generation calls: none (no AI image tool was used to repair or generate views)
- What failed or looks weak: the top view draws the claws closer together than the front view. Toes and claws were laid out from the front view with "top" in their ignore_views. The beak is slightly thin from the front.
