# Run log

## Pipeline run 2026-11-09 23:09:43

Why this run: round 2: quick build

- Command: `build.py refs/giraffe out/giraffe --parts out/giraffe/work/parts.fitted.json --skip-view back --quick --note round 2: quick build`
- Shape: blockout (27 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (27.78 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: mane, ossicone, ossicone knob, tail, tail switch, near front lower leg, near front hoof in, near front hoof out, far front lower leg, far front hoof in, far front hoof out, near hind lower leg, near hind hoof in, near hind hoof out, far hind lower leg, far hind hoof in, far hind hoof out
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.101, 'back': 0.198, 'side': 0.211, 'side_mirror': 0.193, 'top': 0.048, 'unseen_filled': 0.248, 'duplicate_features_removed': 3, 'uv_islands': 30, 'texel_mm': np.float64(6.96), 'palette_colours': 4}
- Self-check (own masks, kit v0.2 scorer): shape 0.909 (textured 0.909), gross errors none, colour 0.905
- Warnings: front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): ear
- Time: 206.0 s

## Pipeline run 2026-11-09 23:14:16

Why this run: final build: thicker ears on a fine grid

- Command: `build.py refs/giraffe out/giraffe --parts out/giraffe/work/parts.final.json --skip-view back --note final build: thicker ears on a fine grid`
- Shape: blockout (27 parts from parts.final.json) grown 0.0 mm, trimmed to the outlines (17.86 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: mane, ossicone, ossicone knob, ear, tail, tail switch
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.086, 'back': 0.219, 'side': 0.232, 'side_mirror': 0.227, 'top': 0.07, 'unseen_filled': 0.166, 'duplicate_features_removed': 3, 'uv_islands': 30, 'texel_mm': np.float64(3.46), 'palette_colours': 4}
- Self-check (own masks, kit v0.2 scorer): shape 0.899 (textured 0.899), gross errors none, colour 0.905
- Warnings: front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views
- Time: 245.0 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: reasoning effort 30
- Animal: Giraffe; long-necked quadruped
- Parts modelled: loft body, neck chain, long-face head capsule, brow, lower jaw, mane, ossicones with dark knobs, ears, tail, tail switch, four separately placed legs each with upper leg, lower leg and 2 hoof claws. Eyes and nostrils are texture only.
- Blockout rounds: 2 blockout rounds: 1 first fit; 2 moved the far foreleg forward onto its drawn position and the ears onto the top view's line.
- Build runs: 1 quick and 1 full build; final options: --skip-view back (measure.py's view check named it). Ears thickened and built on the fine grid for the final build, after they melted away in the quick build.
- Final self-check: shape 0.899, gross errors [], colour 0.905; front IoU 0.852 colour 0.891, back IoU 0.737 colour 0.88, side IoU 0.912 colour 0.919, top IoU 0.886 colour 0.82
- Image-generation calls: none (no AI image tool was used to repair or generate views)
- What failed or looks weak: Back view skipped (pose differs). The front picture does not draw the tail between the legs although the side and back do, so the switch ignores the front view and shows there. The drawing's neck and head sit about 2 cm off-centre in the front view and the model stays symmetric. Far hooves ignore the side view, which draws them higher only through perspective.
- Remaining warnings from the build: ['front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views']
