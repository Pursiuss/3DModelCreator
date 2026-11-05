# Run log

## Pipeline run 2026-11-03 16:43:40

Why this run: round 2 blockout + front legs averaged across asymmetric front drawing, quick check

- Command: `build.py refs/stag out --parts out/work/parts.json --skip-view back --quick --note round 2 blockout + front legs averaged across asymmetric front drawing, quick check`
- Shape: blockout (27 parts from parts.json) grown 0.0 mm, trimmed to the outlines (8.76 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: front lower leg, front hoof inner, front hoof outer, front dewclaw, near hind lower leg, near hind hoof inner, near hind hoof outer, far hind lower leg, far hind hoof inner, far hind hoof outer, tail, antler beam, antler tall tine, antler mid tine, antler back tine, antler bez tine, antler brow tine, antler second tine
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.125, 'back': 0.081, 'side': 0.214, 'side_mirror': 0.193, 'top': 0.035, 'unseen_filled': 0.352, 'duplicate_features_removed': 6, 'uv_islands': 38, 'texel_mm': np.float64(2.24), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.875 (textured 0.875), gross errors top, colour 0.897
- Warnings: front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views; a loose piece (11.5% of the model) came off and was dropped: a part (often a tail, ear or horn) joins the body only where trimming cuts it; start it inside the part it grows from, and build a thin tail, strand or leg as a chain (thin chains are built on a finer grid, with whatever hangs from them); kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): ear; top: 2.8% of the picture is off by more than the tolerance (over the 2% gross-error limit); see selfcheck/off-target-top.png (red = model beyond the drawing, blue = drawing missed)
- Time: 145.0 s

## Pipeline run 2026-11-03 16:48:12

Why this run: antlers leaned toward top view (rear sweep, shorter brow tine), ears ignore top; quick

- Command: `build.py refs/stag out --parts out/work/parts.json --skip-view back --quick --note antlers leaned toward top view (rear sweep, shorter brow tine), ears ignore top; quick`
- Shape: blockout (28 parts from parts.json) grown 0.0 mm, trimmed to the outlines (8.76 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: front lower leg, front hoof inner, front hoof outer, front dewclaw, near hind lower leg, near hind hoof inner, near hind hoof outer, far hind lower leg, far hind hoof inner, far hind hoof outer, tail, antler beam, antler tall tine, antler mid tine, antler back tine, antler rear sweep, antler bez tine, antler brow tine, antler second tine
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.125, 'back': 0.079, 'side': 0.213, 'side_mirror': 0.192, 'top': 0.036, 'unseen_filled': 0.355, 'duplicate_features_removed': 6, 'uv_islands': 40, 'texel_mm': np.float64(2.24), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.866 (textured 0.866), gross errors none, colour 0.897
- Warnings: front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views; a loose piece (11.1% of the model) came off and was dropped: a part (often a tail, ear or horn) joins the body only where trimming cuts it; start it inside the part it grows from, and build a thin tail, strand or leg as a chain (thin chains are built on a finer grid, with whatever hangs from them)
- Time: 137.8 s

## Pipeline run 2026-11-03 16:53:24

Why this run: final: antlers reset to measured joints (fit false) so tall tines stay joined to the beam; full quality

- Command: `build.py refs/stag out --parts out/work/parts.json --skip-view back --note final: antlers reset to measured joints (fit false) so tall tines stay joined to the beam; full quality`
- Shape: blockout (28 parts from parts.json) grown 0.0 mm, trimmed to the outlines (5.63 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: front dewclaw, tail, antler beam, antler tall tine, antler mid tine, antler back tine, antler rear sweep, antler bez tine, antler brow tine, antler second tine
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.101, 'back': 0.108, 'side': 0.208, 'side_mirror': 0.209, 'top': 0.095, 'unseen_filled': 0.279, 'duplicate_features_removed': 7, 'uv_islands': 42, 'texel_mm': np.float64(1.07), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.848 (textured 0.848), gross errors none, colour 0.899
- Warnings: front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views
- Time: 279.9 s

## Pipeline run 2026-11-03 16:58:32

Why this run: final: antlers thickened to drawn widths from profiles, larger ears angled as drawn, front lower legs to front-view widths; full quality

- Command: `build.py refs/stag out --parts out/work/parts.json --skip-view back --note final: antlers thickened to drawn widths from profiles, larger ears angled as drawn, front lower legs to front-view widths; full quality`
- Shape: blockout (28 parts from parts.json) grown 0.0 mm, trimmed to the outlines (5.63 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: front dewclaw, tail, antler beam, antler tall tine, antler mid tine, antler back tine, antler rear sweep, antler bez tine, antler brow tine, antler second tine
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.096, 'back': 0.11, 'side': 0.206, 'side_mirror': 0.208, 'top': 0.091, 'unseen_filled': 0.289, 'duplicate_features_removed': 7, 'uv_islands': 42, 'texel_mm': np.float64(1.07), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.864 (textured 0.864), gross errors none, colour 0.897
- Warnings: front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views
- Time: 256.5 s

## Pipeline run 2026-11-03 17:03:37

Why this run: final: neck root widened and blended (0.12) to remove the ring on the chest; full quality

- Command: `build.py refs/stag out --parts out/work/parts.json --skip-view back --note final: neck root widened and blended (0.12) to remove the ring on the chest; full quality`
- Shape: blockout (28 parts from parts.json) grown 0.0 mm, trimmed to the outlines (5.63 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: front dewclaw, tail, antler beam, antler tall tine, antler mid tine, antler back tine, antler rear sweep, antler bez tine, antler brow tine, antler second tine
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.096, 'back': 0.111, 'side': 0.206, 'side_mirror': 0.208, 'top': 0.09, 'unseen_filled': 0.289, 'duplicate_features_removed': 7, 'uv_islands': 42, 'texel_mm': np.float64(1.07), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.863 (textured 0.863), gross errors none, colour 0.897
- Warnings: front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views
- Time: 280.7 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: low (reasoning effort setting 15)
- Animal: spotted stag (fallow/sika-type deer), four-legged hoofed body plan. Parts modelled: loft torso (7 stations), neck chain, long-face head capsule, lower jaw, nose pad (#3c3632), paddle ears (mirrored), front shoulder capsules + front lower-leg chains (mirrored), separate near (+x, back) and far (-x, forward, hoof lifted) hind thighs and lower-leg chains (the side view draws the hind pair mid-stride), cloven hooves as two wedge paddles per foot (#3c3632), front dewclaws (fine chains), short tail chain, and per antler a main beam chain with tall, mid, back, bez, brow and second tines plus a rear sweep. Eyes and spots are left to the texture. Hind dewclaws were dropped: they sat entirely inside the legs.
- View disagreements: measure.py's view check found the back view in a different pose (front/mirrored-back overlap 0.78), so `--skip-view back` was used for every fit and build. The top view draws the antlers swept back to y = +0.25 while the side view ends them at y = +0.09, so all antler parts have "top" in `ignore_views`. To clear the resulting top-view gross error (2.8% off target), a short rear-sweep chain per antler was added (ignoring top and side for trimming) and the brow tines were shortened about 3 cm. The front drawing is about 1.3 cm off-centre, so the mirrored front legs were placed at the average of the two drawn legs.
- Blockout rounds: 2 fitter runs (each about 10 minutes on this machine). Round 1 fixed the shoulder lump (front upper leg rooted deeper, root_blend), crooked front legs (fit false), a neck with two joints bunched together, a tail buried in the rump, ears too far forward and too thin, and the dewclaws (made fine chains). After round 2 the front legs were re-centred, the hind dewclaws dropped and the hind legs set to x = +/-0.072 behind the front legs. Further edits were made directly in parts.json without another fit, since the parts concerned are all "fit": false.
- Build runs: 6 (2 quick, 1 that crashed in my diagnostic wrapper before finishing, 3 full). Builds from the second quick build on were launched through a scratch wrapper that only logged the bounding box of any piece the build dropped; it did not change the geometry or texture. That wrapper showed the dropped piece was both tall tines, whose roots the fitter had moved off the beam, so the antlers were reset to their measured joints with "fit": false. The second full build thickened the antlers to the widths in profiles.txt (tine radii about 14 mm, not 9 mm) and enlarged and re-angled the ears; the third widened the neck root and raised its blend to 0.12. Final build options: `--parts out/work/parts.json --skip-view back` (full quality, tol 3).
- Final self-check: shape 0.863 (untextured and textured), gross errors none, colour 0.897. Per view IoU / colour / off-target: front 0.835 / 0.873 / 0.000, side 0.892 / 0.920 / 0.0035, top 0.733 / 0.868 / 0.0017, back (not scored, skipped) 0.733 / 0.883 / 0.0015. Remaining warning: only the back-view pose disagreement, handled by the skip.
- Image-generation calls: none (no AI image tool was used to repair or generate views, and no AI 3D generation).
- What failed or looks weak: the top-view IoU is low (0.73) because the top drawing shows the antlers swept back and the rump narrower and asymmetric. Being true to the front and side views was the priority, and the top view only has to stay clear of gross errors. A faint seam remains on the chest at the neck base in the untextured front view; widening the neck root did not remove it, so it is probably where the front outline trims the chest. The tail is a small flattened tab on the rump. The ears are somewhat paler and smaller than drawn from the front. The antlers lean partway towards the top view's swept-back drawing, so from the side they run a few centimetres past the drawn tips. The eyes are texture only.
