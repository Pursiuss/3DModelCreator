# Run log

## Pipeline run 2026-10-30 04:00:46

Why this run: udder and teats as drawn

- Command: `build.py ../penguin-skill-test/refs/cow tests/work/cow-udder/out --parts tests/work/cow-udder/parts.json --skip-view back --note udder and teats as drawn`
- Shape: blockout (28 parts from parts.json) grown 0.0 mm, trimmed to the outlines (7.66 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: horn, tail, tail switch
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.082, 'back': 0.112, 'side': 0.23, 'side_mirror': 0.231, 'top': 0.12, 'unseen_filled': 0.225, 'duplicate_features_removed': 9, 'uv_islands': 32, 'texel_mm': np.float64(1.78), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.893 (textured 0.893), gross errors none, colour 0.853
- Warnings: front and mirrored back outlines overlap only 0.82, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): body: top; ear: top; hind thigh R: top; hind thigh L: top; hind lower leg R: top; hind hoof R inner: top; hind hoof R outer: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): hind hoof L inner, hind hoof L outer
- Time: 263.2 s

