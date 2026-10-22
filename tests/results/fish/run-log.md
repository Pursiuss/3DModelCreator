# Run log

## Pipeline run 2026-10-20 14:22:55

- Command: `build.py tests/animals/fish C:\Users\paris\Documents\School\Algoma CS\Sem 3\Software Engineering\penguin-challenge-kit\tests\results\fish --round 2.0 --res 280 --blur 1.5 --smooth 12 --tol 3`
- Steps: silhouettes (front: alpha channel, back: alpha channel, side: alpha channel, top: alpha channel) -> visual hull (1.46 mm voxels) -> rounded slices (p = 2.0) -> marching cubes + Taubin smoothing (161518 triangles) -> projection texture from the reference views
- Self-check (own masks): shape 0.976, textured shape 0.976, colour match 0.34
- Texture source share: {'front': 0.063, 'back': 0.025, 'side': 0.414, 'side_mirror': 0.419, 'top': 0.078, 'unseen': 0.021}
- Warnings: none
- Time: 16.4 s

