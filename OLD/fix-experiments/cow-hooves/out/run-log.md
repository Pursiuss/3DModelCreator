# Run log

## Pipeline run 2026-10-30 03:15:14

Why this run: split hooves

- Command: `build.py ../penguin-skill-test/refs/cow tests/work/cow-hooves/out --parts tests/work/cow-hooves/parts.json --skip-view back --note split hooves`
- Shape: blockout (28 parts from parts.json) grown 0.0 mm, trimmed to the outlines (7.66 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: horn, tail, tail switch
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.078, 'back': 0.114, 'side': 0.234, 'side_mirror': 0.236, 'top': 0.112, 'unseen_filled': 0.226, 'duplicate_features_removed': 10, 'uv_islands': 32, 'texel_mm': np.float64(1.83), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.897 (textured 0.897), gross errors none, colour 0.855
- Warnings: front and mirrored back outlines overlap only 0.82, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): body: top; ear: top; hind thigh R: top; hind thigh L: top; hind lower leg R: top; hind hoof R inner: top; hind hoof R outer: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): hind hoof L inner, hind hoof L outer, teat front
- Time: 296.6 s

