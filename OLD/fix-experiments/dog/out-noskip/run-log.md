# Run log

## Pipeline run 2026-10-29 23:41:50

- Command: `build.py tests/animals/dog tests/work/dog/out-noskip --parts tests/work/dog/work/parts.fitted.json --quick`
- Shape: blockout (32 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (5.88 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: front claw 1, front claw 2, front claw 3, front claw 4, hind claw 1, hind claw 2, hind claw 3, hind claw 4
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.07, 'back': 0.06, 'side': 0.235, 'side_mirror': 0.233, 'top': 0.114, 'unseen_filled': 0.288, 'duplicate_features_removed': 6, 'uv_islands': 55, 'texel_mm': np.float64(2.11), 'palette_colours': 4}
- Self-check (own masks, kit v0.2 scorer): shape 0.909 (textured 0.909), gross errors none, colour 0.901
- Warnings: back view lined up with the front (scaled x0.88 and moved; outline overlap 0.77 -> 0.88): a part drawn only in the back view, such as a tail hanging below the paws, had thrown its framing off; it is used as lined up; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): thigh: top; hind lower leg: top; hind paw: top; hind toe 4: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): front toe 2, front toe 3, front toe 4, hind toe 2, hind toe 3, hind toe 4, front claw 1, front claw 2, front claw 3, front claw 4, hind claw 1, hind claw 2, hind claw 3, hind claw 4
- Time: 73.3 s

