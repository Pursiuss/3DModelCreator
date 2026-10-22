# Run log

## Pipeline run 2026-10-20 14:22:07

- Command: `build.py tests/animals/bat C:\Users\paris\Documents\School\Algoma CS\Sem 3\Software Engineering\penguin-challenge-kit\tests\results\bat --round 2.0 --res 280 --blur 1.5 --smooth 12 --tol 3`
- Steps: silhouettes (front: alpha channel, back: alpha channel, side: alpha channel, top: alpha channel) -> visual hull (1.36 mm voxels) -> rounded slices (p = 2.0) -> marching cubes + Taubin smoothing (91384 triangles) -> projection texture from the reference views
- Self-check (own masks): shape 0.932, textured shape 0.932, colour match 0.329
- Texture source share: {'front': 0.425, 'back': 0.428, 'side': 0.061, 'side_mirror': 0.058, 'top': 0.028, 'unseen': 0.0}
- Warnings: none
- Time: 8.2 s

