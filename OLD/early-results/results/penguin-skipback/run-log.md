# Run log

## Pipeline run 2026-10-20 14:20:11

Why this run: skip-view test

- Command: `build.py penguin tests/results/penguin-skipback --round 2.0 --res 280 --blur 1.5 --smooth 12 --tol 3 --skip-view back`
- Steps: silhouettes (front: alpha channel, back: alpha channel, side: alpha channel, top: alpha channel) -> visual hull (2.49 mm voxels) -> rounded slices (p = 2.0) -> marching cubes + Taubin smoothing (223628 triangles) -> projection texture from the reference views
- Self-check (own masks): shape 0.979, textured shape 0.979, colour match 0.215
- Texture source share: {'front': 0.262, 'back': 0.275, 'side': 0.214, 'side_mirror': 0.217, 'top': 0.032, 'unseen': 0.064}
- Warnings: none
- Time: 17.1 s

