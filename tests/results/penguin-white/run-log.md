# Run log

## Pipeline run 2026-10-20 14:23:26

- Command: `build.py tests/variants/penguin-white C:\Users\paris\Documents\School\Algoma CS\Sem 3\Software Engineering\penguin-challenge-kit\tests\results\penguin-white --round 2.0 --res 280 --blur 1.5 --smooth 12 --tol 3`
- Steps: silhouettes (front: background-colour segmentation (no alpha), back: background-colour segmentation (no alpha), side: background-colour segmentation (no alpha), top: background-colour segmentation (no alpha)) -> visual hull (2.48 mm voxels) -> rounded slices (p = 2.0) -> marching cubes + Taubin smoothing (224970 triangles) -> projection texture from the reference views
- Self-check (own masks): shape 0.979, textured shape 0.979, colour match 0.231
- Texture source share: {'front': 0.263, 'back': 0.274, 'side': 0.215, 'side_mirror': 0.216, 'top': 0.032, 'unseen': 0.064}
- Warnings: front: silhouette from background-colour segmentation (no alpha) - check the preview for background left on; back: silhouette from background-colour segmentation (no alpha) - check the preview for background left on; side: silhouette from background-colour segmentation (no alpha) - check the preview for background left on; top: silhouette from background-colour segmentation (no alpha) - check the preview for background left on
- Time: 24.6 s

