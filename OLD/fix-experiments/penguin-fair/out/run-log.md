# Run log

## Pipeline run 2026-10-30 03:46:02

Why this run: fairing capped

- Command: `build.py penguin tests/work/penguin-fair/out --parts C:/Users/paris/AppData/Local/Temp/claude/C--Users-paris-Documents-School-Algoma-CS-Sem-3-Software-Engineering-GIT-Project-FIles-course-registration-api/fca9c8c9-d50f-4c81-acf8-d98ef4f8c62c/scratchpad/test8/parts.fitted.json --note fairing capped`
- Shape: blockout (15 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (2.49 mm voxels), smoothed; kept 1 of 1 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.174, 'back': 0.202, 'side': 0.212, 'side_mirror': 0.212, 'top': 0.023, 'unseen_filled': 0.177, 'duplicate_features_removed': 10, 'uv_islands': 24, 'texel_mm': np.float64(0.5), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.917 (textured 0.917), gross errors none, colour 0.895
- Warnings: views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): outer claw: top
- Time: 147.0 s

