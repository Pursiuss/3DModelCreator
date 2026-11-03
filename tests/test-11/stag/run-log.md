# Run log

## Pipeline run 2026-10-31 18:44:37

Why this run: quick check after round-1 fit; far hind hoof moved onto drawing

- Command: `build.py refs/stag out --parts out/work/parts.json --skip-view back --quick --note quick check after round-1 fit; far hind hoof moved onto drawing`
- Shape: blockout (25 parts from parts.json) grown 0.0 mm, trimmed to the outlines (8.76 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: front leg, hind leg R, hind leg L, front hoof outer, front hoof inner, hind hoof R outer, hind hoof R inner, hind hoof L outer, hind hoof L inner, tail, antler beam, brow tine, bez tine, upper tine, back tine, rear tine
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.105, 'back': 0.132, 'side': 0.183, 'side_mirror': 0.183, 'top': 0.035, 'unseen_filled': 0.363, 'duplicate_features_removed': 6, 'uv_islands': 36, 'texel_mm': np.float64(2.33), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.89 (textured 0.89), gross errors top, colour 0.897
- Warnings: front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): ear
- Time: 163.7 s

## Pipeline run 2026-10-31 18:49:56

Why this run: final full build: ears ignore top view (drawn folded back there), restored to drawn size

- Command: `build.py refs/stag out --parts out/work/parts.json --skip-view back --note final full build: ears ignore top view (drawn folded back there), restored to drawn size`
- Shape: blockout (25 parts from parts.json) grown 0.0 mm, trimmed to the outlines (5.63 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: antler beam, brow tine, bez tine, upper tine, back tine, rear tine
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.079, 'back': 0.109, 'side': 0.204, 'side_mirror': 0.203, 'top': 0.076, 'unseen_filled': 0.329, 'duplicate_features_removed': 7, 'uv_islands': 36, 'texel_mm': np.float64(1.12), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.887 (textured 0.887), gross errors top, colour 0.895
- Warnings: front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views
- Time: 295.0 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: low
- Animal: spotted fallow/sika-type stag (four-legged, hoofed, branched antlers). Parts: loft torso (7 stations), neck chain, long-face head capsule, lower jaw, dark nose pad, leaf ears (paddles), shoulders + front-leg chains, two separate hind thighs + hind-leg chains (drawn mid-stride: +x hind leg back, -x hind leg forward with its hoof slightly lifted), cloven hooves (two paddle claws per foot), short tail chain, antlers per side (main beam chain + brow, bez, upper, back and rear tines). Eyes and mouth line left to the texture.
- View check: front and mirrored back overlap only 0.78 (different pose), so the back view was skipped (--skip-view back) for every fit and build.
- Blockout rounds: 1 fit (overlap front 0.92, side 0.93, top 0.90). After it: the far (-x) hind leg's lower joints and hooves moved onto the drawn lifted hoof (fit false); ears given "ignore_views": ["top"] (the top view draws them folded back under the antlers, which trimmed them) and put back to the drawn size. All antler parts ignore the top view (drawn swept back over the shoulders there, upright in front/side).
- Build runs: 2 (one --quick check, one final full build: build.py refs/stag out --parts out/work/parts.json --skip-view back).
- Final self-check: shape 0.887, gross errors ['top'], colour 0.895. Per view IoU / colour: front 0.884 / 0.843, side 0.891 / 0.925, top 0.710 / 0.866 (back 0.738 / 0.872, not scored).
- Image-generation calls: none (no AI image tool was used to repair or generate views).
- What failed or looks weak: the top view's gross error comes from the drawing. It sweeps the antlers back to y = +0.25 over the shoulders and folds the ears back; the side view draws them upright. The model follows the front and side views and was not distorted to chase the top view. The ears read small from the front. The antler tines are simplified (5 per side) where the side view draws the two antlers overlapping. The fit took about 10 minutes per round, so only one fit round was run.
