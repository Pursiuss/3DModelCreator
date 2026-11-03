# Run log

## Pipeline run 2026-10-30 02:50:03

Why this run: thigh root sunk

- Command: `build.py tests/animals/dog tests/work/dog-roots/out --parts tests/work/dog-roots/parts.json --skip-view back --note thigh root sunk`
- Shape: blockout (24 parts from parts.json) grown 0.0 mm, trimmed to the outlines (3.78 mm voxels), smoothed; kept 1 of 1 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.07, 'back': 0.052, 'side': 0.242, 'side_mirror': 0.241, 'top': 0.116, 'unseen_filled': 0.279, 'duplicate_features_removed': 8, 'uv_islands': 39, 'texel_mm': np.float64(0.98), 'palette_colours': 4}
- Self-check (own masks, kit v0.2 scorer): shape 0.909 (textured 0.909), gross errors none, colour 0.904
- Warnings: front and mirrored back outlines overlap only 0.88, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): thigh: top; hind lower leg: top; hind paw: top; hind toe 4: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): front toe 2, front toe 3, hind toe 2, hind toe 3, hind toe 4
- Time: 242.1 s

## Pipeline run 2026-10-30 03:04:41

Why this run: thigh and tail roots sunk

- Command: `build.py tests/animals/dog tests/work/dog-roots/out --parts tests/work/dog-roots/parts.json --skip-view back --note thigh and tail roots sunk`
- Shape: blockout (24 parts from parts.json) grown 0.0 mm, trimmed to the outlines (3.78 mm voxels), smoothed; kept 1 of 1 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.07, 'back': 0.052, 'side': 0.242, 'side_mirror': 0.241, 'top': 0.115, 'unseen_filled': 0.279, 'duplicate_features_removed': 8, 'uv_islands': 39, 'texel_mm': np.float64(0.98), 'palette_colours': 4}
- Self-check (own masks, kit v0.2 scorer): shape 0.909 (textured 0.909), gross errors none, colour 0.905
- Warnings: front and mirrored back outlines overlap only 0.88, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): thigh: top; hind lower leg: top; hind paw: top; hind toe 4: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): front toe 2, front toe 3, hind toe 2, hind toe 3, hind toe 4
- Time: 193.8 s

