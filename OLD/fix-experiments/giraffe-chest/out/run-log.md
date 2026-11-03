# Run log

## Pipeline run 2026-10-30 03:13:29

Why this run: neck blend

- Command: `build.py tests/animals/giraffe tests/work/giraffe-chest/out --parts tests/work/giraffe-chest/parts.json --skip-view top back --note neck blend`
- Shape: blockout (20 parts from parts.json) grown 0.0 mm, trimmed to the outlines (17.86 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: front leg R, hind leg R, front leg L, hind leg L, front hoof R, front hoof L, hind hoof R, hind hoof L, tail, tail tuft
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.121, 'back': 0.116, 'side': 0.281, 'side_mirror': 0.277, 'top': 0.042, 'unseen_filled': 0.163, 'duplicate_features_removed': 4, 'uv_islands': 25, 'texel_mm': np.float64(3.22), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.881 (textured 0.881), gross errors top, colour 0.895
- Warnings: front width 0.908 m vs top width 0.718 m disagree by more than 8% (pose or framing differs); side length 3.221 m vs top length 3.896 m disagree by more than 8% (pose or framing differs); front and mirrored back outlines overlap only 0.76, even lined up as well as they can be: pose differs between views
- Time: 131.7 s

