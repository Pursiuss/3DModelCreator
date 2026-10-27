# Run log

## Pipeline run 2026-10-26 20:19:12

Why this run: stag, round 3 blockout

- Command: `build.py tests/animals/stag tests/work/stag/out --parts tests/work/stag/work/parts.fitted.json --note stag, round 3 blockout`
- Shape: blockout (23 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (7.50 mm voxels), smoothed; kept 1 of 9 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.059, 'back': 0.102, 'side': 0.227, 'side_mirror': 0.231, 'top': 0.128, 'unseen_filled': 0.252, 'duplicate_features_removed': 12, 'uv_islands': 18, 'texel_mm': np.float64(1.38), 'palette_colours': 2}
- Self-check (own masks, kit v0.2 scorer): shape 0.649 (textured 0.649), gross errors front, side, top, colour 0.857
- Warnings: front width 0.803 m vs top width 0.969 m disagree by more than 8% (pose or framing differs); side length 1.821 m vs top length 1.446 m disagree by more than 8% (pose or framing differs); front and mirrored back outlines overlap only 0.81: pose differs between views
- Time: 390.9 s

## Pipeline run 2026-10-26 20:25:30

Why this run: top view drawn at other proportions: not used for trimming

- Command: `build.py tests/animals/stag tests/work/stag/out --parts tests/work/stag/work/parts.fitted.json --skip-view top --note top view drawn at other proportions: not used for trimming`
- Shape: blockout (23 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (7.50 mm voxels), smoothed; kept 3 of 10 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.054, 'back': 0.088, 'side': 0.233, 'side_mirror': 0.237, 'top': 0.138, 'unseen_filled': 0.249, 'duplicate_features_removed': 14, 'uv_islands': 24, 'texel_mm': np.float64(1.47), 'palette_colours': 2}
- Self-check (own masks, kit v0.2 scorer): shape 0.666 (textured 0.666), gross errors front, side, top, colour 0.901
- Warnings: front width 0.803 m vs top width 0.969 m disagree by more than 8% (pose or framing differs); side length 1.821 m vs top length 1.446 m disagree by more than 8% (pose or framing differs); front and mirrored back outlines overlap only 0.81: pose differs between views
- Time: 341.8 s

## Pipeline run 2026-10-26 20:37:16

Why this run: top and back views drawn in other proportions/pose: not used for trimming

- Command: `build.py tests/animals/stag tests/work/stag/out --parts tests/work/stag/work/parts.fitted.json --skip-view top back --note top and back views drawn in other proportions/pose: not used for trimming`
- Shape: blockout (23 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (7.50 mm voxels), smoothed; kept 3 of 5 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.058, 'back': 0.087, 'side': 0.231, 'side_mirror': 0.234, 'top': 0.132, 'unseen_filled': 0.258, 'duplicate_features_removed': 14, 'uv_islands': 32, 'texel_mm': np.float64(1.48), 'palette_colours': 2}
- Self-check (own masks, kit v0.2 scorer): shape 0.766 (textured 0.766), gross errors front, side, top, colour 0.921
- Warnings: front width 0.803 m vs top width 0.969 m disagree by more than 8% (pose or framing differs); side length 1.821 m vs top length 1.446 m disagree by more than 8% (pose or framing differs); front and mirrored back outlines overlap only 0.81: pose differs between views
- Time: 451.7 s

## Pipeline run 2026-10-26 20:42:08

Why this run: torso smoothing fixed; top and back not used for trimming

- Command: `build.py tests/animals/stag tests/work/stag/out --parts tests/work/stag/work/parts.fitted.json --skip-view top back --note torso smoothing fixed; top and back not used for trimming`
- Shape: blockout (23 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (7.50 mm voxels), smoothed; kept 1 of 3 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.055, 'back': 0.092, 'side': 0.229, 'side_mirror': 0.23, 'top': 0.129, 'unseen_filled': 0.265, 'duplicate_features_removed': 13, 'uv_islands': 32, 'texel_mm': np.float64(1.48), 'palette_colours': 2}
- Self-check (own masks, kit v0.2 scorer): shape 0.778 (textured 0.778), gross errors front, side, top, colour 0.923
- Warnings: front width 0.803 m vs top width 0.969 m disagree by more than 8% (pose or framing differs); side length 1.821 m vs top length 1.446 m disagree by more than 8% (pose or framing differs); front and mirrored back outlines overlap only 0.81: pose differs between views
- Time: 214.9 s

