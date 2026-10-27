# Run log

## Pipeline run 2026-10-27 13:53:36

Why this run: trim keeps parts

- Command: `build.py tests/animals/crab tests/work/crab/out --parts tests/work/crab/parts.fitted.json --note trim keeps parts`
- Shape: blockout (8 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (1.04 mm voxels), smoothed; kept 1 of 1 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.056, 'back': 0.046, 'side': 0.025, 'side_mirror': 0.024, 'top': 0.373, 'unseen_filled': 0.476, 'duplicate_features_removed': 2, 'uv_islands': 15, 'texel_mm': np.float64(0.19), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.946 (textured 0.946), gross errors none, colour 0.924
- Warnings: none
- Time: 63.6 s

