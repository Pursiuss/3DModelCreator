# Run log

## Pipeline run 2026-10-30 22:50:50

Why this run: legs joined

- Command: `build.py ../penguin-skill-test/refs/giraffe C:/Users/paris/AppData/Local/Temp/claude/C--Users-paris-Documents-School-Algoma-CS-Sem-3-Software-Engineering-GIT-Project-FIles-course-registration-api/fca9c8c9-d50f-4c81-acf8-d98ef4f8c62c/scratchpad/glegs/out --parts C:/Users/paris/AppData/Local/Temp/claude/C--Users-paris-Documents-School-Algoma-CS-Sem-3-Software-Engineering-GIT-Project-FIles-course-registration-api/fca9c8c9-d50f-4c81-acf8-d98ef4f8c62c/scratchpad/glegs/parts.json --skip-view top back --note legs joined`
- Shape: blockout (26 parts from parts.json) grown 0.0 mm, trimmed to the outlines (17.86 mm voxels), smoothed; kept 1 of 5 mesh pieces; built on a finer grid and joined on: ossicone, ossicone tip, front lower leg fwd, front lower leg back, hind lower leg fwd, hind lower leg back, tail, tail switch
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.121, 'back': 0.132, 'side': 0.284, 'side_mirror': 0.27, 'top': 0.038, 'unseen_filled': 0.156, 'duplicate_features_removed': 5, 'uv_islands': 29, 'texel_mm': np.float64(3.52), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.867 (textured 0.867), gross errors top, colour 0.893
- Warnings: front width 0.908 m vs top width 0.718 m disagree by more than 8% (pose or framing differs); side length 3.221 m vs top length 3.896 m disagree by more than 8% (pose or framing differs); front and mirrored back outlines overlap only 0.76, even lined up as well as they can be: pose differs between views; a loose piece (0.5% of the model) came off and was dropped: a part (often a tail, ear or horn) joins the body only where trimming cuts it; start it inside the part it grows from, and build a thin tail, strand or leg as a chain (thin chains are built on a finer grid, with whatever hangs from them); kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): hoof fwd fl inner, hoof back fl inner
- Time: 311.4 s

