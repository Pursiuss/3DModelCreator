# Run log

## Pipeline run 2026-10-31 00:46:23

Why this run: quick test: sheep round 1 blockout

- Command: `build.py refs/sheep out/sheep --parts out/sheep/work/parts.fitted.json --skip-view back --quick --note quick test: sheep round 1 blockout`
- Shape: blockout (13 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (6.29 mm voxels), smoothed; kept 1 of 1 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.03, 'back': 0.086, 'side': 0.216, 'side_mirror': 0.215, 'top': 0.17, 'unseen_filled': 0.283, 'duplicate_features_removed': 13, 'uv_islands': 19, 'texel_mm': np.float64(2.14), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.936 (textured 0.936), gross errors none, colour 0.899
- Warnings: front and mirrored back outlines overlap only 0.84, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): ear: top
- Time: 70.1 s

