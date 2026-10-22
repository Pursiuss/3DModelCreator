# Run log

## Pipeline run 2026-10-21 01:13:05

Why this run: Astro Boy sheet; hair follows the front view

- Command: `build.py tests/work/astro/refs tests/work/astro/out --parts tests/work/astro/work/parts.fitted.json --note Astro Boy sheet; hair follows the front view`
- Shape: blockout (15 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (4.82 mm voxels), smoothed; kept 1 of 4 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.308, 'back': 0.215, 'side': 0.136, 'side_mirror': 0.137, 'unseen_filled': 0.204, 'duplicate_features_removed': 7}
- Self-check (own masks): shape 0.59, textured shape 0.59, colour match 0.314
- Warnings: front and mirrored back outlines overlap only 0.64: pose differs between views
- Time: 78.0 s

## Pipeline run 2026-10-21 01:17:23

Why this run: Astro Boy sheet; hair follows the front view; arms from the front view only

- Command: `build.py tests/work/astro/refs tests/work/astro/out --parts tests/work/astro/work/parts.fitted.json --note Astro Boy sheet; hair follows the front view; arms from the front view only`
- Shape: blockout (15 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (4.82 mm voxels), smoothed; kept 1 of 4 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.315, 'back': 0.21, 'side': 0.122, 'side_mirror': 0.123, 'unseen_filled': 0.23, 'duplicate_features_removed': 7}
- Self-check (own masks): shape 0.594, textured shape 0.594, colour match 0.314
- Warnings: front and mirrored back outlines overlap only 0.64: pose differs between views
- Time: 80.7 s

## Pipeline run 2026-10-21 02:14:21

Why this run: colour plan

- Command: `build.py tests/work/astro/refs tests/work/astro/out --parts tests/work/astro/work/parts.fitted.json --note colour plan`
- Shape: blockout (15 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (4.82 mm voxels), smoothed; kept 1 of 4 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.315, 'back': 0.21, 'side': 0.122, 'side_mirror': 0.123, 'top': 0.0, 'unseen_filled': 0.23, 'duplicate_features_removed': 7, 'uv_islands': 20, 'texel_mm': np.float64(0.85), 'palette_colours': 4}
- Self-check (own masks): shape 0.594, textured shape 0.594, colour match 0.714
- Warnings: front and mirrored back outlines overlap only 0.64: pose differs between views
- Time: 87.6 s

## Pipeline run 2026-10-21 02:21:07

Why this run: colour plan

- Command: `build.py tests/work/astro/refs tests/work/astro/out --parts tests/work/astro/work/parts.fitted.json --note colour plan`
- Shape: blockout (15 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (4.82 mm voxels), smoothed; kept 1 of 4 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.315, 'back': 0.21, 'side': 0.122, 'side_mirror': 0.123, 'top': 0.0, 'unseen_filled': 0.23, 'duplicate_features_removed': 7, 'uv_islands': 20, 'texel_mm': np.float64(0.85), 'palette_colours': 9}
- Self-check (own masks): shape 0.594, textured shape 0.594, colour match 0.743
- Warnings: front and mirrored back outlines overlap only 0.64: pose differs between views
- Time: 87.6 s

## Pipeline run 2026-10-22 13:52:30

Why this run: underside fill

- Command: `build.py tests/work/astro/refs tests/work/astro/out --parts tests/work/astro/work/parts.fitted.json --note underside fill`
- Shape: blockout (15 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (4.82 mm voxels), smoothed; kept 1 of 4 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.273, 'back': 0.189, 'side': 0.075, 'side_mirror': 0.106, 'top': 0.0, 'unseen_filled': 0.357, 'duplicate_features_removed': 7, 'uv_islands': 20, 'texel_mm': np.float64(0.85), 'palette_colours': 9}
- Self-check (own masks): shape 0.594, textured shape 0.594, colour match 0.709
- Warnings: front and mirrored back outlines overlap only 0.64: pose differs between views
- Time: 98.1 s

## Pipeline run 2026-10-22 14:52:37

Why this run: speck clean-up

- Command: `build.py tests/work/astro/refs tests/work/astro/out --parts tests/work/astro/work/parts.fitted.json --note speck clean-up`
- Shape: blockout (15 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (4.82 mm voxels), smoothed; kept 1 of 4 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.273, 'back': 0.189, 'side': 0.075, 'side_mirror': 0.106, 'top': 0.0, 'unseen_filled': 0.357, 'duplicate_features_removed': 7, 'uv_islands': 20, 'texel_mm': np.float64(0.85), 'palette_colours': 9}
- Self-check (own masks, kit v0.2 scorer): shape 0.687 (textured 0.687), gross errors side, top, colour 0.812
- Warnings: front and mirrored back outlines overlap only 0.64: pose differs between views
- Time: 94.1 s

