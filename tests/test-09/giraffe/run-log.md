# Run log

## Pipeline run 2026-10-30 21:41:50

Why this run: giraffe round 2 blockout, full build, top and back views skipped (framing/pose differ)

- Command: `build.py refs/giraffe out/giraffe --parts out/giraffe/work/parts.fitted.json --skip-view top back --note giraffe round 2 blockout, full build, top and back views skipped (framing/pose differ)`
- Shape: blockout (26 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (17.86 mm voxels), smoothed; kept 1 of 5 mesh pieces; built on a finer grid and joined on: ossicone, ossicone tip, front lower leg fwd, front lower leg back, hind lower leg fwd, hind lower leg back, tail, tail switch
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.142, 'back': 0.131, 'side': 0.257, 'side_mirror': 0.244, 'top': 0.041, 'unseen_filled': 0.185, 'duplicate_features_removed': 4, 'uv_islands': 29, 'texel_mm': np.float64(3.56), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.885 (textured 0.885), gross errors top, colour 0.893
- Warnings: front width 0.908 m vs top width 0.718 m disagree by more than 8% (pose or framing differs); side length 3.221 m vs top length 3.896 m disagree by more than 8% (pose or framing differs); front and mirrored back outlines overlap only 0.76, even lined up as well as they can be: pose differs between views; a loose piece (0.5% of the model) came off and was dropped: a part (often a tail, ear or horn) joins the body only where trimming cuts it; start it inside the part it grows from, and build a thin tail, strand or leg as a chain (thin chains are built on a finer grid, with whatever hangs from them); kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): hoof fwd fl inner, hoof back fl inner
- Time: 228.2 s

## Pipeline run 2026-10-30 21:50:00

Why this run: giraffe round 3: leg chains locked to measured joints (fitter had scrambled them); top and back views skipped

- Command: `build.py refs/giraffe out/giraffe --parts out/giraffe/work/parts.fitted.json --skip-view top back --note giraffe round 3: leg chains locked to measured joints (fitter had scrambled them); top and back views skipped`
- Shape: blockout (26 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (17.86 mm voxels), smoothed; kept 1 of 5 mesh pieces; built on a finer grid and joined on: ossicone, ossicone tip, front lower leg fwd, front lower leg back, hind lower leg fwd, hind lower leg back, tail, tail switch
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.12, 'back': 0.129, 'side': 0.285, 'side_mirror': 0.257, 'top': 0.037, 'unseen_filled': 0.172, 'duplicate_features_removed': 5, 'uv_islands': 29, 'texel_mm': np.float64(3.61), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.872 (textured 0.872), gross errors top, colour 0.894
- Warnings: front width 0.908 m vs top width 0.718 m disagree by more than 8% (pose or framing differs); side length 3.221 m vs top length 3.896 m disagree by more than 8% (pose or framing differs); front and mirrored back outlines overlap only 0.76, even lined up as well as they can be: pose differs between views; a loose piece (0.5% of the model) came off and was dropped: a part (often a tail, ear or horn) joins the body only where trimming cuts it; start it inside the part it grows from, and build a thin tail, strand or leg as a chain (thin chains are built on a finer grid, with whatever hangs from them); kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): hoof fwd fl inner, hoof back fl inner
- Time: 231.4 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: low
- Animal: giraffe, four-legged with both leg pairs mid-stride. Parts: loft torso (8 stations), neck chain (aspect 0.6), long-face head, lower jaw, nose pad, paddle ears, ossicone chains with dark tips, two separate front legs and two separate hind legs (upper capsule plus lower chain each), cloven hooves, tail chain and an 8-strand switch.
- Blockout rounds: 3. Round 1: first fit (front 0.94 / side 0.94). Round 2: hooves and ears thickened to the build minimum, and leg roots moved deeper. Round 3: the fitter had scrambled the lower-leg chains (joints swapped between legs, so legs crossed and kicked out), so all leg parts were pinned to the measured joints. Build runs: 2 (full, --skip-view top back).
- The top and back views were skipped. View check: the top view draws the animal 3.9 m long against 3.2 m in the side view, and the back view's pose differs (overlap 0.76).
- Final self-check: shape 0.872, colour 0.894. Gross errors: ['top'], because the top reference itself disagrees with the side view's length, so no model matching front and side can match it. IoU/colour: front 0.868/0.877, side 0.876/0.911, top 0.653/0.872.
- Image-generation calls: none (no AI image tool was used to repair or generate views)
- What failed or looks weak: the gross error in the top view is a reference problem, not a modelling one, but it is listed. One small loose piece (0.5%) was dropped by the build. Two front inner hooves were kept untrimmed. The legs are fairly uniform sticks with little knee or hock shape.
