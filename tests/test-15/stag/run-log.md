# Run log

## Pipeline run 2026-11-09 22:50:36

Why this run: round 2: quick build

- Command: `build.py refs/stag out/stag --parts out/stag/work/parts.fitted.json --skip-view back --quick --note round 2: quick build`
- Shape: blockout (32 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (8.76 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: antler beam, brow tine, bez tine, small tine, trez tine, upper fork, rear tine upper, rear tine lower, tail, front leg, front +x hoof in, front +x hoof out, front +x dewclaw, front -x hoof in, front -x hoof out, front -x dewclaw, near hind leg, far hind leg, near hind hoof in, near hind hoof out, near hind dewclaw, far hind hoof in, far hind hoof out, far hind dewclaw
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.101, 'back': 0.131, 'side': 0.21, 'side_mirror': 0.204, 'top': 0.038, 'unseen_filled': 0.316, 'duplicate_features_removed': 4, 'uv_islands': 42, 'texel_mm': np.float64(2.35), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.798 (textured 0.798), gross errors top, colour 0.885
- Warnings: front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): far hind dewclaw, near hind dewclaw, near hind hoof in, rear tine upper, small tine, upper fork; front: 1.5% of the picture is off by more than the tolerance (close to the 2% gross-error limit); see selfcheck/off-target-front.png (red = model beyond the drawing, blue = drawing missed); top: 4.3% of the picture is off by more than the tolerance (over the 2% gross-error limit); see selfcheck/off-target-top.png (red = model beyond the drawing, blue = drawing missed)
- Time: 226.4 s

## Pipeline run 2026-11-09 22:56:32

Why this run: round 3: ears kept, rump to drawn length, antler tips leaned to the top view

- Command: `build.py refs/stag out/stag --parts out/stag/work/parts.fitted.json --skip-view back --quick --note round 3: ears kept, rump to drawn length, antler tips leaned to the top view`
- Shape: blockout (32 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (8.76 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: ear, antler beam, brow tine, bez tine, small tine, trez tine, upper fork, rear tine upper, rear tine lower, tail, front leg, front +x hoof in, front +x hoof out, front +x dewclaw, front -x hoof in, front -x hoof out, front -x dewclaw, near hind leg, far hind leg, near hind hoof in, near hind hoof out, near hind dewclaw, far hind hoof in, far hind hoof out, far hind dewclaw
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.109, 'back': 0.136, 'side': 0.202, 'side_mirror': 0.197, 'top': 0.042, 'unseen_filled': 0.314, 'duplicate_features_removed': 5, 'uv_islands': 42, 'texel_mm': np.float64(2.38), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.821 (textured 0.821), gross errors none, colour 0.883
- Warnings: front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): brow tine, far hind dewclaw, near hind dewclaw, near hind hoof in, small tine, upper fork
- Time: 187.1 s

## Pipeline run 2026-11-09 23:01:09

Why this run: round 4: head and nose moved onto the drawn nose position

- Command: `build.py refs/stag out/stag --parts out/stag/work/parts.fitted.json --skip-view back --quick --note round 4: head and nose moved onto the drawn nose position`
- Shape: blockout (32 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (8.76 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: ear, antler beam, brow tine, bez tine, small tine, trez tine, upper fork, rear tine upper, rear tine lower, tail, front leg, front +x hoof in, front +x hoof out, front +x dewclaw, front -x hoof in, front -x hoof out, front -x dewclaw, near hind leg, far hind leg, near hind hoof in, near hind hoof out, near hind dewclaw, far hind hoof in, far hind hoof out, far hind dewclaw
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.104, 'back': 0.135, 'side': 0.203, 'side_mirror': 0.199, 'top': 0.042, 'unseen_filled': 0.317, 'duplicate_features_removed': 6, 'uv_islands': 42, 'texel_mm': np.float64(2.38), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.847 (textured 0.847), gross errors none, colour 0.891
- Warnings: front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): brow tine, far hind dewclaw, near hind dewclaw, near hind hoof in, small tine, upper fork
- Time: 189.2 s

## Pipeline run 2026-11-09 23:10:04

Why this run: final build

- Command: `build.py refs/stag out/stag --parts out/stag/work/parts.fitted.json --skip-view back --note final build`
- Shape: blockout (32 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (5.63 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: ear, antler beam, brow tine, bez tine, small tine, trez tine, upper fork, rear tine upper, rear tine lower, tail
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.091, 'back': 0.213, 'side': 0.179, 'side_mirror': 0.188, 'top': 0.085, 'unseen_filled': 0.243, 'duplicate_features_removed': 6, 'uv_islands': 42, 'texel_mm': np.float64(1.15), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.855 (textured 0.855), gross errors none, colour 0.89
- Warnings: front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): near hind leg: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): near hind hoof in, far hind dewclaw, brow tine, small tine, upper fork
- Time: 504.1 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: reasoning effort 30
- Animal: Spotted fallow-type stag; quadruped with branching antlers, hind legs drawn mid-stride
- Parts modelled: loft body, neck chain, long-face head capsule, lower jaw, nose pad, ears, main antler beam and 7 tines per side, tail, front legs, two separately placed hind legs with thighs, 2 hoof claws and a dewclaw per leg.
- Blockout rounds: 4 blockout rounds: 1 first fit; 2 antlers re-measured on a close-up and hind legs brought in; 3 ears thickened to survive the build, rump extended to the drawn length, antler tips leaned toward the top view; 4 head and nose moved to the true drawn nose position, after a misread grid had shifted the whole model.
- Build runs: 3 quick builds and 1 full build; final options: --skip-view back (measure.py's view check named it).
- Final self-check: shape 0.855, gross errors [], colour 0.89; front IoU 0.84 colour 0.871, back IoU 0.731 colour 0.872, side IoU 0.871 colour 0.909, top IoU 0.719 colour 0.843
- Image-generation calls: none (no AI image tool was used to repair or generate views)
- What failed or looks weak: Back view skipped (pose differs). The top view sweeps the antlers much further back than the side view does: antlers ignore the top view, and only the rear tines are leaned towards it (so those tines also ignore the side view), which removes the gross error but leaves the top IoU low. Fine antler branches are thin, so small misplacements cost shape score. The drawing's body is about 1 cm off-centre in the front view and the model stays symmetric.
- Remaining warnings from the build: ['front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views', 'views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): near hind leg: top', 'kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): near hind hoof in, far hind dewclaw, brow tine, small tine, upper fork']
