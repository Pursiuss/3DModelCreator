# Run log

## Pipeline run 2026-11-09 22:13:42

Why this run: round 3: first full build

- Command: `build.py refs/penguin out/penguin --parts out/penguin/work/parts.fitted.json --note round 3: first full build`
- Shape: blockout (20 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (2.49 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: tail feather centre, tail feather mid, tail feather outer, inner claw, middle claw, outer claw
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.153, 'back': 0.211, 'side': 0.191, 'side_mirror': 0.191, 'top': 0.02, 'unseen_filled': 0.233, 'duplicate_features_removed': 14, 'uv_islands': 32, 'texel_mm': np.float64(0.51), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.925 (textured 0.925), gross errors none, colour 0.879
- Warnings: none
- Time: 251.0 s

## Pipeline run 2026-11-09 22:19:07

Why this run: round 4: added lower belly so feathers reach the ankles

- Command: `build.py refs/penguin out/penguin --parts out/penguin/work/parts.fitted.json --note round 4: added lower belly so feathers reach the ankles`
- Shape: blockout (21 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (2.49 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: tail feather centre, tail feather mid, tail feather outer, inner claw, middle claw, outer claw
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.164, 'back': 0.206, 'side': 0.185, 'side_mirror': 0.185, 'top': 0.02, 'unseen_filled': 0.241, 'duplicate_features_removed': 14, 'uv_islands': 38, 'texel_mm': np.float64(0.51), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.93 (textured 0.93), gross errors none, colour 0.879
- Warnings: none
- Time: 279.1 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: reasoning effort 30
- Animal: Adelie-style penguin; upright bird, egg body with a broad lower belly
- Parts modelled: body, rump, lower belly, neck, head, upper and lower beak, flippers, tail paddle plus 5 tail feathers, ankles, heels, web paddles, 3 toes and 3 claws per foot. Eyes are texture only.
- Blockout rounds: 4 blockout rounds: 1 first fit; 2 added the mirror flag I had missed on flippers and ankles and locked the body width; 3 moved flippers outward and tightened the body bottom; 4 added the lower belly so the feathers reach the ankles.
- Build runs: 2 full builds, no --quick; final options: defaults (all four views used).
- Final self-check: shape 0.93, gross errors [], colour 0.879; front IoU 0.925 colour 0.83, back IoU 0.924 colour 0.905, side IoU 0.935 colour 0.929, top IoU 0.872 colour 0.819
- Image-generation calls: none (no AI image tool was used to repair or generate views)
- What failed or looks weak: Feather-tip ragged edges are painted, not modelled. Toes follow the front view; the top view spreads them differently, so it is ignored for the toes and claws.
- Remaining warnings from the build: []
