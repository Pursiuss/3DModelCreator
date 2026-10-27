# Run log

## Pipeline run 2026-10-27 15:50:05

Why this run: round 2, quick

- Command: `build.py tests/animals/giraffe tests/work/giraffe/out --parts tests/work/giraffe/work/parts.fitted.json --skip-view top back --quick --note round 2, quick`
- Shape: blockout (22 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (27.78 mm voxels), smoothed; kept 2 of 2 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.076, 'back': 0.103, 'side': 0.312, 'side_mirror': 0.314, 'top': 0.021, 'unseen_filled': 0.174, 'duplicate_features_removed': 5, 'uv_islands': 23, 'texel_mm': np.float64(5.66), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.744 (textured 0.744), gross errors top, colour 0.881
- Warnings: front width 0.908 m vs top width 0.718 m disagree by more than 8% (pose or framing differs); side length 3.221 m vs top length 3.896 m disagree by more than 8% (pose or framing differs); front and mirrored back outlines overlap only 0.82: pose differs between views; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): lower jaw
- Time: 41.6 s

## Pipeline run 2026-10-27 15:53:07

Why this run: round 3, quick

- Command: `build.py tests/animals/giraffe tests/work/giraffe/out --parts tests/work/giraffe/work/parts.fitted.json --skip-view top back --quick --note round 3, quick`
- Shape: blockout (22 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (27.78 mm voxels), smoothed; kept 1 of 2 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.102, 'back': 0.109, 'side': 0.304, 'side_mirror': 0.301, 'top': 0.022, 'unseen_filled': 0.161, 'duplicate_features_removed': 5, 'uv_islands': 24, 'texel_mm': np.float64(5.72), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.8 (textured 0.8), gross errors top, colour 0.889
- Warnings: front width 0.908 m vs top width 0.718 m disagree by more than 8% (pose or framing differs); side length 3.221 m vs top length 3.896 m disagree by more than 8% (pose or framing differs); front and mirrored back outlines overlap only 0.82: pose differs between views; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): lower jaw, hind hoof fwd, hind hoof back
- Time: 42.5 s

## Pipeline run 2026-10-27 15:55:50

Why this run: round 4, quick

- Command: `build.py tests/animals/giraffe tests/work/giraffe/out --parts tests/work/giraffe/work/parts.fitted.json --skip-view top back --quick --note round 4, quick`
- Shape: blockout (22 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (27.78 mm voxels), smoothed; kept 1 of 2 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.104, 'back': 0.111, 'side': 0.297, 'side_mirror': 0.3, 'top': 0.023, 'unseen_filled': 0.164, 'duplicate_features_removed': 5, 'uv_islands': 24, 'texel_mm': np.float64(5.72), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.803 (textured 0.803), gross errors top, colour 0.89
- Warnings: front width 0.908 m vs top width 0.718 m disagree by more than 8% (pose or framing differs); side length 3.221 m vs top length 3.896 m disagree by more than 8% (pose or framing differs); front and mirrored back outlines overlap only 0.82: pose differs between views; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): lower jaw, hind hoof fwd, hind hoof back
- Time: 41.7 s

## Pipeline run 2026-10-27 16:01:26

Why this run: round 4b: tail starts inside the rump

- Command: `build.py tests/animals/giraffe tests/work/giraffe/out --parts tests/work/giraffe/work/parts.fitted.json --skip-view top back --quick --note round 4b: tail starts inside the rump`
- Shape: blockout (22 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (27.78 mm voxels), smoothed; kept 1 of 2 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.104, 'back': 0.113, 'side': 0.297, 'side_mirror': 0.301, 'top': 0.022, 'unseen_filled': 0.164, 'duplicate_features_removed': 5, 'uv_islands': 24, 'texel_mm': np.float64(5.72), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.802 (textured 0.802), gross errors top, colour 0.889
- Warnings: front width 0.908 m vs top width 0.718 m disagree by more than 8% (pose or framing differs); side length 3.221 m vs top length 3.896 m disagree by more than 8% (pose or framing differs); front and mirrored back outlines overlap only 0.82: pose differs between views; a loose piece (1.8% of the model) came off and was dropped: a part (often a tail, ear or horn) joins the body only where trimming cuts it; start it inside the part it grows from; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): lower jaw, hind hoof fwd, hind hoof back
- Time: 41.8 s

## Pipeline run 2026-10-27 16:03:12

Why this run: round 4c: tail runs into its tuft

- Command: `build.py tests/animals/giraffe tests/work/giraffe/out --parts tests/work/giraffe/work/parts.fitted.json --skip-view top back --quick --note round 4c: tail runs into its tuft`
- Shape: blockout (22 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (27.78 mm voxels), smoothed; kept 1 of 2 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.103, 'back': 0.113, 'side': 0.299, 'side_mirror': 0.3, 'top': 0.022, 'unseen_filled': 0.163, 'duplicate_features_removed': 5, 'uv_islands': 24, 'texel_mm': np.float64(5.72), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.802 (textured 0.802), gross errors top, colour 0.889
- Warnings: front width 0.908 m vs top width 0.718 m disagree by more than 8% (pose or framing differs); side length 3.221 m vs top length 3.896 m disagree by more than 8% (pose or framing differs); front and mirrored back outlines overlap only 0.82: pose differs between views; a loose piece (1.8% of the model) came off and was dropped: a part (often a tail, ear or horn) joins the body only where trimming cuts it; start it inside the part it grows from; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): lower jaw, hind hoof fwd, hind hoof back
- Time: 42.8 s

## Pipeline run 2026-10-27 16:05:37

Why this run: final build

- Command: `build.py tests/animals/giraffe tests/work/giraffe/out --parts tests/work/giraffe/work/parts.fitted.json --skip-view top back --note final build`
- Shape: blockout (22 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (17.86 mm voxels), smoothed; kept 2 of 2 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.099, 'back': 0.109, 'side': 0.302, 'side_mirror': 0.301, 'top': 0.021, 'unseen_filled': 0.168, 'duplicate_features_removed': 4, 'uv_islands': 25, 'texel_mm': np.float64(2.82), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.828 (textured 0.828), gross errors top, colour 0.877
- Warnings: front width 0.908 m vs top width 0.718 m disagree by more than 8% (pose or framing differs); side length 3.221 m vs top length 3.896 m disagree by more than 8% (pose or framing differs); front and mirrored back outlines overlap only 0.82: pose differs between views; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): lower jaw, hind hoof fwd, hind hoof back
- Time: 116.5 s

