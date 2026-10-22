# Run log

## Pipeline run 2026-10-20 14:21:54

- Command: `build.py tests/animals/giraffe C:\Users\paris\Documents\School\Algoma CS\Sem 3\Software Engineering\penguin-challenge-kit\tests\results\giraffe --round 2.0 --res 280 --blur 1.5 --smooth 12 --tol 3`
- Steps: silhouettes (front: alpha channel, back: alpha channel, side: alpha channel, top: alpha channel) -> visual hull (16.25 mm voxels) -> rounded slices (p = 2.0) -> marching cubes + Taubin smoothing (94476 triangles) -> projection texture from the reference views
- Self-check (own masks): shape 0.953, textured shape 0.953, colour match 0.536
- Texture source share: {'front': 0.169, 'back': 0.158, 'side': 0.297, 'side_mirror': 0.297, 'top': 0.08, 'unseen': 0.073}
- Warnings: none
- Time: 7.2 s

