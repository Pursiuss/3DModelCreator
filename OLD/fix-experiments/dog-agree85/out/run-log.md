# Run log

## Pipeline run 2026-10-30 02:30:33

- Command: `build.py tests/animals/dog tests/work/dog-agree85/out --parts tests/work/dog/work/parts.fitted.json --skip-view back --quick`
- Shape: blockout (24 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (5.88 mm voxels), smoothed; kept 1 of 1 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.066, 'back': 0.061, 'side': 0.239, 'side_mirror': 0.239, 'top': 0.117, 'unseen_filled': 0.277, 'duplicate_features_removed': 7, 'uv_islands': 39, 'texel_mm': np.float64(2.11), 'palette_colours': 4}
- Self-check (own masks, kit v0.2 scorer): shape 0.919 (textured 0.919), gross errors none, colour 0.905
- Warnings: back view lined up with the front (scaled x0.88 and moved; outline overlap 0.77 -> 0.88): a part drawn only in the back view, such as a tail hanging below the paws, had thrown its framing off; it is used as lined up; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): thigh: top; hind lower leg: top; hind paw: top; hind toe 4: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): front toe 2, front toe 3, hind toe 2, hind toe 3, hind toe 4
- Time: 85.5 s

