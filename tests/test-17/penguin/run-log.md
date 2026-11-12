# Run log

## Pipeline run 2026-11-11 20:16:15

Why this run: round 3 blockout: flippers, feet and beak pinned to measurements

- Command: `build.py refs/penguin out --parts out/work/parts.fitted.json --note round 3 blockout: flippers, feet and beak pinned to measurements`
- Shape: blockout (15 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (2.49 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: web, inner claw, middle claw, outer claw
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.129, 'back': 0.153, 'side': 0.172, 'side_mirror': 0.172, 'top': 0.018, 'unseen_filled': 0.357, 'duplicate_features_removed': 10, 'uv_islands': 24, 'texel_mm': np.float64(0.42), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.911 (textured 0.911), gross errors none, colour 0.887
- Warnings: none
- Time: 226.3 s

## Pipeline run 2026-11-11 20:20:34

Why this run: added lower belly so feathers hang down over the legs as drawn

- Command: `build.py refs/penguin out --parts out/work/parts.fitted.json --note added lower belly so feathers hang down over the legs as drawn`
- Shape: blockout (16 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (2.49 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: web, inner claw, middle claw, outer claw
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.134, 'back': 0.152, 'side': 0.172, 'side_mirror': 0.172, 'top': 0.018, 'unseen_filled': 0.352, 'duplicate_features_removed': 10, 'uv_islands': 25, 'texel_mm': np.float64(0.44), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.915 (textured 0.915), gross errors none, colour 0.891
- Warnings: none
- Time: 218.1 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: low (reasoning effort setting for this session)
- Setup: system Python 3.14 lacked numpy etc.; created a private venv `.venv-skill` and installed requirements.txt.
- Animal: Adélie-style penguin, upright bird body plan. Parts modelled: belly, upper body (shoulders between the flippers), lower belly (feathers hanging over the legs), head, upper and lower beak (two jaws, measured on a side zoom), two paddle flippers (tilted ~30 degrees, curl and crescent bend; edges placed from `--colours side/front`), flat tail wedge, short pink legs, webbed foot paddle, three toes and three claws per foot (claws as fine chains). Eyes are left to the texture (drawn on a smooth black head), not modelled as parts.
- View check: the four views agree; no view skipped. The front view spreads the toes much wider (x 0.01-0.11 m) than the top view (x 0.065-0.10 m), so the feet, toes, claws and web are laid out from the front and side views with "top" in their `ignore_views`.
- Blockout rounds: 4 fits. (1) first blockout: overlap front 0.95 / side 0.91, but the fitter shortened the flipper, raised the toes off the drawn ones and lowered the belly past the feet; (2) flipper, feet and belly pinned to measured values with `"fit": false`, claws turned into chains joined to the toe tips: no part warnings; (3) flipper moved out to the drawn outer edge, feet thickened at the ankle; (4) added a lower-belly ellipsoid so the feather line comes down over the legs (front 0.93 -> 0.94).
- Build runs: 2, both full quality (no `--quick`), default options; final build: `build.py refs/penguin out --parts out/work/parts.fitted.json`.
- Final self-check: shape 0.915, gross errors none, colour 0.891, warnings none. Per view IoU / colour: front 0.935 / 0.861, side 0.896 / 0.922, back 0.935 / 0.865 (not scored), top 0.845 / 0.794 (off_target 0.0011).
- Image-generation calls: none (no AI image tool was used to repair or generate views)
- What failed or looks weak: the top view scores lowest (IoU 0.845, colour 0.79), mainly the feet, which are laid out from the front view rather than the top view's narrower toes; about 35% of the surface is filled from neighbouring colours (underside, insides of flippers), so it is flat-shaded rather than drawn; there are faint horizontal ridges on the lower back in the back-3/4 render where the trimming meets the belly; the drawn feather fringe at the bottom of the belly and the separate tail-feather points are smoothed into one tail wedge.
