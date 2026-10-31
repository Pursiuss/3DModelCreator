# Run log

## Pipeline run 2026-10-20 14:21:16

- Command: `build.py penguin C:\Users\paris\Documents\School\Algoma CS\Sem 3\Software Engineering\penguin-challenge-kit\tests\results\penguin --round 2.0 --res 280 --blur 1.5 --smooth 12 --tol 3`
- Steps: silhouettes (front: alpha channel, back: alpha channel, side: alpha channel, top: alpha channel) -> visual hull (2.49 mm voxels) -> rounded slices (p = 2.0) -> marching cubes + Taubin smoothing (222970 triangles) -> projection texture from the reference views
- Self-check (own masks): shape 0.979, textured shape 0.979, colour match 0.215
- Texture source share: {'front': 0.261, 'back': 0.274, 'side': 0.215, 'side_mirror': 0.218, 'top': 0.031, 'unseen': 0.065}
- Warnings: none
- Time: 17.9 s

