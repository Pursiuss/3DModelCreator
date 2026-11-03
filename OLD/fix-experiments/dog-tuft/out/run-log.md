# Run log

## Pipeline run 2026-10-30 03:54:11

Why this run: bushy tail strands

- Command: `build.py tests/animals/dog tests/work/dog-tuft/out --parts tests/work/dog-tuft/parts.json --skip-view back --note bushy tail strands`
- Shape: blockout (24 parts from parts.json) grown 0.0 mm, trimmed to the outlines (3.78 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: tail
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.064, 'back': 0.069, 'side': 0.241, 'side_mirror': 0.239, 'top': 0.119, 'unseen_filled': 0.268, 'duplicate_features_removed': 7, 'uv_islands': 39, 'texel_mm': np.float64(0.99), 'palette_colours': 4}
- Self-check (own masks, kit v0.2 scorer): shape 0.916 (textured 0.916), gross errors none, colour 0.911
- Warnings: front and mirrored back outlines overlap only 0.88, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): thigh: top; hind lower leg: top; hind paw: top; hind toe 4: top; a loose piece (0.8% of the model) came off and was dropped: a part (often a tail, ear or horn) joins the body only where trimming cuts it; start it inside the part it grows from, and build a thin tail, strand or leg as a chain (thin chains are built on a finer grid, with whatever hangs from them); kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): front toe 2, front toe 3, hind toe 2, hind toe 3, hind toe 4
- Time: 225.1 s

