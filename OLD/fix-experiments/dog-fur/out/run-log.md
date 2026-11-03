# Run log

## Pipeline run 2026-10-30 04:13:27

Why this run: fur parts

- Command: `build.py tests/animals/dog tests/work/dog-fur/out --parts tests/work/dog-fur/parts.json --skip-view back --note fur parts`
- Shape: blockout (27 parts from parts.json) grown 0.0 mm, trimmed to the outlines (3.78 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: tail
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.061, 'back': 0.051, 'side': 0.239, 'side_mirror': 0.238, 'top': 0.11, 'unseen_filled': 0.301, 'duplicate_features_removed': 8, 'uv_islands': 44, 'texel_mm': np.float64(0.99), 'palette_colours': 4}
- Self-check (own masks, kit v0.2 scorer): shape 0.93 (textured 0.93), gross errors none, colour 0.907
- Warnings: front and mirrored back outlines overlap only 0.88, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): thigh: top; hind lower leg: top; hind paw: top; hind toe 4: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): hind toe 2, hind toe 4
- Time: 224.8 s

