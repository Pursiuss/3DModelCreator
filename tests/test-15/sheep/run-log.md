# Run log

## Pipeline run 2026-11-09 22:41:12

Why this run: round 2: quick build

- Command: `build.py refs/sheep out/sheep --parts out/sheep/work/parts.fitted.json --skip-view back --quick --note round 2: quick build`
- Shape: blockout (16 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (6.29 mm voxels), smoothed; kept 1 of 1 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.075, 'back': 0.089, 'side': 0.205, 'side_mirror': 0.204, 'top': 0.158, 'unseen_filled': 0.27, 'duplicate_features_removed': 13, 'uv_islands': 25, 'texel_mm': np.float64(2.14), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.932 (textured 0.932), gross errors none, colour 0.877
- Warnings: front and mirrored back outlines overlap only 0.84, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): nose pad: top; kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): ear
- Time: 106.8 s

## Pipeline run 2026-11-09 22:47:08

Why this run: final build: ears on the top view's line

- Command: `build.py refs/sheep out/sheep --parts out/sheep/work/parts.final.json --skip-view back --note final build: ears on the top view's line`
- Shape: blockout (16 parts from parts.final.json) grown 0.0 mm, trimmed to the outlines (4.04 mm voxels), smoothed; kept 1 of 1 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.071, 'back': 0.09, 'side': 0.204, 'side_mirror': 0.202, 'top': 0.159, 'unseen_filled': 0.275, 'duplicate_features_removed': 14, 'uv_islands': 25, 'texel_mm': np.float64(1.04), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.93 (textured 0.93), gross errors none, colour 0.878
- Warnings: front and mirrored back outlines overlap only 0.84, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): nose pad: top
- Time: 332.4 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: reasoning effort 30
- Animal: Woolly sheep; rounded quadruped
- Parts modelled: loft body, neck, wool cap, long-face head capsule, lower jaw, nose pad, ears, tail, front and hind legs (mirrored chains), 2 hoof claws and a dewclaw per leg.
- Blockout rounds: 2 blockout rounds: 1 first fit; 2 pinned the hind and front legs to measured positions after the fitter ballooned the hip and moved the hooves.
- Build runs: 1 quick and 1 full build; final options: --skip-view back (measure.py's view check named it).
- Final self-check: shape 0.93, gross errors [], colour 0.878; front IoU 0.931 colour 0.861, back IoU 0.783 colour 0.885, side IoU 0.928 colour 0.882, top IoU 0.929 colour 0.874
- Image-generation calls: none (no AI image tool was used to repair or generate views)
- What failed or looks weak: Back view skipped (pose differs). Wool curls are painted over a smooth body rather than modelled. Far legs are mirrored from the near ones, because the side view's offset is small and mostly perspective.
- Remaining warnings from the build: ['front and mirrored back outlines overlap only 0.84, even lined up as well as they can be: pose differs between views', 'views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): nose pad: top']
