# Run log

## Pipeline run 2026-10-30 03:55:02

Why this run: tail switch strands

- Command: `build.py ../penguin-skill-test/refs/cow tests/work/cow-tuft/out --parts tests/work/cow-tuft/parts.json --skip-view back --note tail switch strands`
- Shape: blockout (28 parts from parts.json) grown 0.0 mm, trimmed to the outlines (7.66 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: horn, tail, tail switch
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.082, 'back': 0.111, 'side': 0.23, 'side_mirror': 0.231, 'top': 0.119, 'unseen_filled': 0.227, 'duplicate_features_removed': 9, 'uv_islands': 32, 'texel_mm': np.float64(1.83), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.895 (textured 0.895), gross errors none, colour 0.853
- Warnings: front and mirrored back outlines overlap only 0.82, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): body: top; ear: top; hind thigh R: top; hind thigh L: top; hind lower leg R: top; hind hoof R inner: top; hind hoof R outer: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): hind hoof L inner, hind hoof L outer, teat front
- Time: 275.4 s

