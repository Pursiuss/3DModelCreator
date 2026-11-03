# Run log

## Pipeline run 2026-10-31 00:52:02

Why this run: quick test: stag round 1 blockout

- Command: `build.py refs/stag out/stag --parts out/stag/work/parts.fitted.json --skip-view back --quick --note quick test: stag round 1 blockout`
- Shape: blockout (19 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (8.76 mm voxels), smoothed; kept 1 of 5 mesh pieces; built on a finer grid and joined on: antler beam, brow tine, upper tine, tail, front leg, hind leg fwd, hind leg back
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.095, 'back': 0.116, 'side': 0.211, 'side_mirror': 0.21, 'top': 0.068, 'unseen_filled': 0.3, 'duplicate_features_removed': 7, 'uv_islands': 25, 'texel_mm': np.float64(2.29), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.813 (textured 0.813), gross errors top, colour 0.907
- Warnings: front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): ear: top; a loose piece (0.9% of the model) came off and was dropped: a part (often a tail, ear or horn) joins the body only where trimming cuts it; start it inside the part it grows from, and build a thin tail, strand or leg as a chain (thin chains are built on a finer grid, with whatever hangs from them); kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): hind hoof fwd outer, hind hoof fwd inner, hind hoof back outer, hind hoof back inner, brow tine, upper tine
- Time: 104.3 s

## Pipeline run 2026-10-31 00:54:30

Why this run: quick test: stag round 2, antlers ignore the top view

- Command: `build.py refs/stag out/stag --parts out/stag/work/parts.json --skip-view back --quick --note quick test: stag round 2, antlers ignore the top view`
- Shape: blockout (19 parts from parts.json) grown 0.0 mm, trimmed to the outlines (8.76 mm voxels), smoothed; kept 1 of 5 mesh pieces; built on a finer grid and joined on: antler beam, brow tine, upper tine, tail, front leg, hind leg fwd, hind leg back
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.099, 'back': 0.118, 'side': 0.208, 'side_mirror': 0.207, 'top': 0.044, 'unseen_filled': 0.325, 'duplicate_features_removed': 7, 'uv_islands': 25, 'texel_mm': np.float64(2.29), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.821 (textured 0.821), gross errors top, colour 0.903
- Warnings: front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): ear: top; a loose piece (0.9% of the model) came off and was dropped: a part (often a tail, ear or horn) joins the body only where trimming cuts it; start it inside the part it grows from, and build a thin tail, strand or leg as a chain (thin chains are built on a finer grid, with whatever hangs from them); kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): hind hoof fwd outer, hind hoof fwd inner, hind hoof back outer, hind hoof back inner, brow tine, upper tine
- Time: 112.1 s

