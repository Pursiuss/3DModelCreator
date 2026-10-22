# Run log

## Pipeline run 2026-10-20 14:22:30

- Command: `build.py tests/animals/crab C:\Users\paris\Documents\School\Algoma CS\Sem 3\Software Engineering\penguin-challenge-kit\tests\results\crab --round 2.0 --res 280 --blur 1.5 --smooth 12 --tol 3`
- Steps: silhouettes (front: alpha channel, back: alpha channel, side: alpha channel, top: alpha channel) -> visual hull (1.04 mm voxels) -> rounded slices (p = 2.0) -> marching cubes + Taubin smoothing (231984 triangles) -> projection texture from the reference views
- Self-check (own masks): shape 0.947, textured shape 0.947, colour match 0.57
- Texture source share: {'front': 0.239, 'back': 0.168, 'side': 0.121, 'side_mirror': 0.123, 'top': 0.349, 'unseen': 0.193}
- Warnings: none
- Time: 19.0 s

