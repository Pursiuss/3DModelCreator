# Run log

## Pipeline run 2026-10-27 13:52:30

Why this run: trim keeps parts

- Command: `build.py tests/animals/giraffe tests/work/giraffe/out --parts tests/work/giraffe/parts.fitted.json --note trim keeps parts`
- Shape: blockout (7 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (16.25 mm voxels), smoothed; kept 1 of 1 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.132, 'back': 0.131, 'side': 0.212, 'side_mirror': 0.211, 'top': 0.077, 'unseen_filled': 0.237, 'duplicate_features_removed': 7, 'uv_islands': 10, 'texel_mm': np.float64(2.02), 'palette_colours': 2}
- Self-check (own masks, kit v0.2 scorer): shape 0.976 (textured 0.976), gross errors none, colour 0.913
- Warnings: none
- Time: 46.9 s

