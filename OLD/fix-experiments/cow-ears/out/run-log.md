# Run log

## Pipeline run 2026-10-30 02:15:21

Why this run: leaf ears

- Command: `build.py ../penguin-skill-test/refs/cow tests/work/cow-ears/out --parts tests/work/cow-ears/parts.json --skip-view back --note leaf ears`
- Shape: blockout (24 parts from parts.json) grown 0.0 mm, trimmed to the outlines (7.66 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: horn, tail, tail switch
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.079, 'back': 0.116, 'side': 0.236, 'side_mirror': 0.238, 'top': 0.114, 'unseen_filled': 0.217, 'duplicate_features_removed': 8, 'uv_islands': 28, 'texel_mm': np.float64(1.79), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.895 (textured 0.895), gross errors none, colour 0.854
- Warnings: front and mirrored back outlines overlap only 0.82, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): body: top; ear: top; hind thigh R: top; hind thigh L: top; hind lower leg R: top; hind hoof R: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): hind hoof L, teat front
- Time: 441.9 s

