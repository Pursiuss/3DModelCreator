# Run log

## Pipeline run 2026-10-20 14:21:40

- Command: `build.py tests/animals/turtle C:\Users\paris\Documents\School\Algoma CS\Sem 3\Software Engineering\penguin-challenge-kit\tests\results\turtle --round 2.0 --res 280 --blur 1.5 --smooth 12 --tol 3`
- Steps: silhouettes (front: alpha channel, back: alpha channel, side: alpha channel, top: alpha channel) -> visual hull (1.62 mm voxels) -> rounded slices (p = 2.0) -> marching cubes + Taubin smoothing (238994 triangles) -> projection texture from the reference views
- Self-check (own masks): shape 0.97, textured shape 0.97, colour match 0.755
- Texture source share: {'front': 0.181, 'back': 0.127, 'side': 0.176, 'side_mirror': 0.176, 'top': 0.34, 'unseen': 0.116}
- Warnings: none
- Time: 17.7 s

