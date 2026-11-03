# Run log

## Pipeline run 2026-10-30 23:03:59

Why this run: mouth and paws v2

- Command: `build.py ../penguin-skill-test/refs/dog C:/Users/paris/AppData/Local/Temp/claude/C--Users-paris-Documents-School-Algoma-CS-Sem-3-Software-Engineering-GIT-Project-FIles-course-registration-api/fca9c8c9-d50f-4c81-acf8-d98ef4f8c62c/scratchpad/dfix2/out --parts C:/Users/paris/AppData/Local/Temp/claude/C--Users-paris-Documents-School-Algoma-CS-Sem-3-Software-Engineering-GIT-Project-FIles-course-registration-api/fca9c8c9-d50f-4c81-acf8-d98ef4f8c62c/scratchpad/dfix2/parts.json --skip-view back --note mouth and paws v2`
- Shape: blockout (35 parts from parts.json) grown 0.0 mm, trimmed to the outlines (3.78 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: front claw 1, front claw 2, front claw 3, front claw 4, hind claw 1, hind claw 2, hind claw 3, hind claw 4
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.075, 'back': 0.04, 'side': 0.239, 'side_mirror': 0.24, 'top': 0.1, 'unseen_filled': 0.306, 'duplicate_features_removed': 14, 'uv_islands': 59, 'texel_mm': np.float64(1.0), 'palette_colours': 4}
- Self-check (own masks, kit v0.2 scorer): shape 0.921 (textured 0.921), gross errors none, colour 0.897
- Warnings: front and mirrored back outlines overlap only 0.88, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): thigh: top; hind lower leg: top; hind toe 4: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): hind toe 2, hind toe 3, hind toe 4, front claw 1, front claw 2, front claw 3, front claw 4, hind claw 1, hind claw 2, hind claw 3, hind claw 4
- Time: 353.7 s

