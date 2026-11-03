# Run log

## Pipeline run 2026-10-30 02:28:45

Why this run: baseline, current code

- Command: `build.py tests/animals/dog tests/work/dog-base/out --parts tests/work/dog/work/parts.fitted.json --skip-view back --note baseline, current code`
- Shape: blockout (24 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (3.78 mm voxels), smoothed; kept 1 of 1 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.065, 'back': 0.06, 'side': 0.238, 'side_mirror': 0.238, 'top': 0.117, 'unseen_filled': 0.282, 'duplicate_features_removed': 7, 'uv_islands': 39, 'texel_mm': np.float64(1.02), 'palette_colours': 4}
- Self-check (own masks, kit v0.2 scorer): shape 0.913 (textured 0.913), gross errors none, colour 0.904
- Warnings: front and mirrored back outlines overlap only 0.88, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): thigh: top; hind lower leg: top; hind paw: top; hind toe 4: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): front toe 2, front toe 3, hind toe 2, hind toe 3, hind toe 4
- Time: 274.2 s

