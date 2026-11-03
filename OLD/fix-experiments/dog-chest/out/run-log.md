# Run log

## Pipeline run 2026-10-30 03:15:30

Why this run: neck blend

- Command: `build.py tests/animals/dog tests/work/dog-chest/out --parts tests/work/dog-chest/parts.json --skip-view back --note neck blend`
- Shape: blockout (24 parts from parts.json) grown 0.0 mm, trimmed to the outlines (3.78 mm voxels), smoothed; kept 1 of 1 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.071, 'back': 0.051, 'side': 0.242, 'side_mirror': 0.241, 'top': 0.116, 'unseen_filled': 0.278, 'duplicate_features_removed': 7, 'uv_islands': 39, 'texel_mm': np.float64(0.98), 'palette_colours': 4}
- Self-check (own masks, kit v0.2 scorer): shape 0.911 (textured 0.911), gross errors none, colour 0.905
- Warnings: front and mirrored back outlines overlap only 0.88, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): thigh: top; hind lower leg: top; hind paw: top; hind toe 4: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): front toe 2, front toe 3, hind toe 2, hind toe 3, hind toe 4
- Time: 253.5 s

