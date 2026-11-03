# Run log

## Pipeline run 2026-10-30 21:41:57

Why this run: cow round 4 blockout, full build, back view skipped (pose differs)

- Command: `build.py refs/cow out/cow --parts out/cow/work/parts.fitted.json --skip-view back --note cow round 4 blockout, full build, back view skipped (pose differs)`
- Shape: blockout (24 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (7.66 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: horn, tail, tail switch
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.07, 'back': 0.101, 'side': 0.237, 'side_mirror': 0.234, 'top': 0.122, 'unseen_filled': 0.237, 'duplicate_features_removed': 9, 'uv_islands': 31, 'texel_mm': np.float64(1.8), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.917 (textured 0.917), gross errors none, colour 0.854
- Warnings: front and mirrored back outlines overlap only 0.82, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): thigh back: top; hind lower leg back: top; hind hoof back outer: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): front teat, hind hoof fwd inner
- Time: 286.5 s

## Pipeline run 2026-10-30 21:52:41

Why this run: cow round 5: hind legs and tail switch locked to measured joints; back view skipped

- Command: `build.py refs/cow out/cow --parts out/cow/work/parts.fitted.json --skip-view back --note cow round 5: hind legs and tail switch locked to measured joints; back view skipped`
- Shape: blockout (24 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (7.66 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: horn, tail, tail switch
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.072, 'back': 0.097, 'side': 0.235, 'side_mirror': 0.237, 'top': 0.126, 'unseen_filled': 0.234, 'duplicate_features_removed': 6, 'uv_islands': 31, 'texel_mm': np.float64(1.83), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.906 (textured 0.906), gross errors none, colour 0.837
- Warnings: front and mirrored back outlines overlap only 0.82, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): thigh back: top; hind lower leg back: top; hind hoof back outer: top; hind hoof back inner: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): front teat, hind hoof fwd outer, hind hoof fwd inner
- Time: 246.3 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: low
- Animal: dairy cow (Simmental-type colouring), four-legged with the hind legs mid-stride. Parts: loft torso (8 stations), neck, long-face head capsule, broad lower jaw, nose pad, paddle ears, horn chains, udder with four teats, front upper and lower legs (mirrored), two separately placed hind legs (thigh plus lower chain each), cloven hooves (two paddle claws per foot), tail chain and an 8-strand switch.
- Blockout rounds: 5. Round 1: first fit (front 0.93 / side 0.93), but the fitter dropped the belly, kinked the front leg and the tail, and moved the udder forward. Round 2: udder moved back, front legs and tail pinned. Round 3: belly line put back and the loft pinned; thigh roots deepened. Rounds 4–5: hind legs and tail switch pinned to the measured joints. Build runs: 2 (full, --skip-view back); the final one is round 5.
- The back view was skipped (view check: front and mirrored back overlap only 0.82). The nose pad ignores the front view, which draws the nose lower.
- Final self-check: shape 0.906, gross errors none, colour 0.837. IoU/colour: front 0.907/0.795, side 0.894/0.856, top 0.905/0.818.
- Image-generation calls: none (no AI image tool was used to repair or generate views)
- What failed or looks weak: colour 0.837 is under the skill's 0.85 target but above the judges' 0.80. The round-4 build scored 0.854 but its hind legs were bent wrongly, so round 5 was kept. The tail switch is shorter than drawn. A front teat and the forward hind hooves were kept untrimmed (slightly off their drawn place).
