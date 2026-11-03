# Run log

## Pipeline run 2026-10-29 14:12:48

Why this run: chains + fine grid

- Command: `build.py tests/animals/giraffe tests/work/giraffe-chain/out --parts tests/work/giraffe-chain/work/parts.fitted.json --skip-view top back --note chains + fine grid`
- Shape: blockout (21 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (17.86 mm voxels), smoothed; kept 1 of 1 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.126, 'back': 0.11, 'side': 0.269, 'side_mirror': 0.267, 'top': 0.043, 'unseen_filled': 0.186, 'duplicate_features_removed': 3, 'uv_islands': 26, 'texel_mm': np.float64(3.01), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.883 (textured 0.883), gross errors top, colour 0.889
- Warnings: front width 0.908 m vs top width 0.718 m disagree by more than 8% (pose or framing differs); side length 3.221 m vs top length 3.896 m disagree by more than 8% (pose or framing differs); front and mirrored back outlines overlap only 0.82: pose differs between views
- Time: 122.9 s

