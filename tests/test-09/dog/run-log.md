# Run log

## Pipeline run 2026-10-30 21:04:14

Why this run: dog round 4 blockout, full build, back view skipped (pose differs)

- Command: `build.py refs/dog out/dog --parts out/dog/work/parts.fitted.json --skip-view back --note dog round 4 blockout, full build, back view skipped (pose differs)`
- Shape: blockout (27 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (3.78 mm voxels), smoothed; kept 1 of 1 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.069, 'back': 0.041, 'side': 0.248, 'side_mirror': 0.248, 'top': 0.103, 'unseen_filled': 0.29, 'duplicate_features_removed': 10, 'uv_islands': 44, 'texel_mm': np.float64(1.0), 'palette_colours': 4}
- Self-check (own masks, kit v0.2 scorer): shape 0.926 (textured 0.926), gross errors none, colour 0.897
- Warnings: front and mirrored back outlines overlap only 0.88, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): thigh: top; hind lower leg: top; hind paw: top; hind toe 4: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): front toe 4, hind toe 3, hind toe 4
- Time: 217.3 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: low
- Animal: golden retriever (long fur), four-legged. Parts: loft torso (7 stations), neck, chest ruff, skull, snout, nose, lower jaw, dark mouth part, tongue (open mouth), hanging paddle ears, front upper and lower legs, front feathering, thighs and hind lower legs, trousers, paws with 4 toe lobes each, and a feathered tail chain.
- Blockout rounds: 4. Round 1: first fit (front 0.94 / side 0.96), but the leg chains zig-zagged, the thighs drifted to the centre line and the skull grew 20%. Round 2: legs, skull and fur roots pinned. Round 3: belly station put back where the fitter had dropped it between the front legs; thigh root moved deeper. Round 4: trousers root moved deeper. Build runs: 1 (full, --skip-view back).
- The back view was skipped (measure.py view check: front and mirrored back overlap only 0.88, pose differs). The nose and snout ignore the front view, which draws the nose about 3 cm lower than the side view.
- Final self-check: shape 0.926, gross errors none, colour 0.897. IoU/colour: front 0.928/0.857, side 0.924/0.902, top 0.908/0.891.
- Image-generation calls: none (no AI image tool was used to repair or generate views)
- What failed or looks weak: the hind legs sit wider than in the top view, so the build ignored the top view for them. A few toe lobes were kept untrimmed (slightly off their drawn place). Some pale patches on the hind paws, and the front feathering reads a little like a separate strip.
