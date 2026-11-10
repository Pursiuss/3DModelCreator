# Run log

## Pipeline run 2026-11-09 22:35:22

Why this run: round 2: quick build

- Command: `build.py refs/cow out/cow --parts out/cow/work/parts.fitted.json --skip-view back --quick --note round 2: quick build`
- Shape: blockout (36 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (11.91 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: horn, tail, tail switch
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.057, 'back': 0.11, 'side': 0.26, 'side_mirror': 0.26, 'top': 0.103, 'unseen_filled': 0.21, 'duplicate_features_removed': 10, 'uv_islands': 38, 'texel_mm': np.float64(3.76), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.911 (textured 0.911), gross errors none, colour 0.855
- Warnings: front and mirrored back outlines overlap only 0.82, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): ear: top; near hind upper leg: top; near hind lower leg: top; near hind hoof out: top; far hind upper leg: top; far hind lower leg: top
- Time: 174.3 s

## Pipeline run 2026-11-09 22:43:53

Why this run: final build: fuller tail switch

- Command: `build.py refs/cow out/cow --parts out/cow/work/parts.final.json --skip-view back --note final build: fuller tail switch`
- Shape: blockout (36 parts from parts.final.json) grown 0.0 mm, trimmed to the outlines (7.66 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: horn, tail, tail switch
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.064, 'back': 0.099, 'side': 0.252, 'side_mirror': 0.249, 'top': 0.106, 'unseen_filled': 0.23, 'duplicate_features_removed': 7, 'uv_islands': 38, 'texel_mm': np.float64(1.81), 'palette_colours': 3}
- Self-check (own masks, kit v0.2 scorer): shape 0.912 (textured 0.912), gross errors none, colour 0.857
- Warnings: front and mirrored back outlines overlap only 0.82, even lined up as well as they can be: pose differs between views; views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): ear: top; near hind upper leg: top; near hind lower leg: top; near hind hoof out: top; near hind dewclaw out: top; far hind upper leg: top; far hind lower leg: top
- Time: 487.8 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: reasoning effort 30
- Animal: Red-and-white dairy cow; horned quadruped, legs drawn mid-stride
- Parts modelled: loft body, neck, long-face head capsule, lower jaw, nose pad, ears, horns, udder, 4 teats, tail, tail switch, four separately placed legs each with upper leg, lower leg, 2 hoof claws and 2 dewclaws.
- Blockout rounds: 2 blockout rounds: 1 first fit; 2 reattached floating dewclaws, shrank and deepened the hind upper legs, kept far hooves on the ground.
- Build runs: 1 quick and 1 full build; final options: --skip-view back (measure.py's view check named it).
- Final self-check: shape 0.912, gross errors [], colour 0.857; front IoU 0.888 colour 0.774, back IoU 0.832 colour 0.782, side IoU 0.936 colour 0.889, top IoU 0.885 colour 0.825
- Image-generation calls: none (no AI image tool was used to repair or generate views)
- What failed or looks weak: Back view skipped (pose differs). The front view does not draw the tail between the legs although the back and side do, so the switch ignores the front view and shows there. Far hooves ignore the side view, which draws them higher only through perspective.
- Remaining warnings from the build: ['front and mirrored back outlines overlap only 0.82, even lined up as well as they can be: pose differs between views', 'views ignored for parts they disagree with (one view would have cut deep into a part the others draw whole): ear: top; near hind upper leg: top; near hind lower leg: top; near hind hoof out: top; near hind dewclaw out: top; far hind upper leg: top; far hind lower leg: top']
