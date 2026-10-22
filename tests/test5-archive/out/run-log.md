# Run log

## Pipeline run 2026-10-21 00:35:11

Why this run: round-4 blockout; legs/feet/toes/claws ignore back (user: feet drawn wrong way) and top (toe spread disagrees with front)

- Command: `build.py refs/penguin out --parts out/work/parts.fitted.json --note round-4 blockout; legs/feet/toes/claws ignore back (user: feet drawn wrong way) and top (toe spread disagrees with front)`
- Shape: blockout (15 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (2.49 mm voxels), smoothed; kept 1 of 1 mesh pieces
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.249, 'back': 0.265, 'side': 0.205, 'side_mirror': 0.204, 'top': 0.02, 'unseen_filled': 0.057, 'duplicate_features_removed': 10}
- Self-check (own masks): shape 0.899, textured shape 0.899, colour match 0.217
- Warnings: none
- Time: 258.5 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: low (reasoning effort 15)
- Animal: Adélie penguin. Upright ovoid body plan. Parts modelled: body, lower body, neck, head, beak, two flippers, flat wedge tail, two short legs (mostly inside the belly feathers), and per foot a small pad, three toes and three claws. Eyes and markings come from the texture only.
- User instruction: back.png draws the feet facing the wrong way, so `back` is in `ignore_views` for every leg, foot pad, toe and claw part.
- View disagreement: the front view spreads the toes from x≈0.01 to 0.11 m, the top view only from 0.06 to 0.10 m. I laid the toes and claws out from the front view (zoomed on the ruler) and the side view, and also put `top` in `ignore_views` for the foot pads, toes and claws. Legs ignore only `back` (the top view does not show them).
- Blockout rounds: 4.
  - Round 1: first blockout. The fitter widened the body until it swallowed the flippers, and stretched the beak.
  - Round 2: locked the body width and the flipper (tilted and yawed so it stands off the body). Set the beak by hand.
  - Round 3: re-measured the beak (its tip is at y≈-0.148, so the side and top views agree on length). Put the toes and claws on the drawn ones and set `fit: false` on them. Lengthened the tail.
  - Round 4: the fitter had grown the neck up into the head. Locked the head and neck to their measured sizes.
- Build runs: 1, with options `--parts out/work/parts.fitted.json` (default tol, grow 0).
- Final self-check: shape 0.899. Per-view IoU: front 0.914, back 0.914, side 0.922, top 0.846. Colour match 0.217. No warnings.
- What failed or looks weak:
  - The top view's outline match is the lowest (0.846), because the feet seen from above are laid out differently and ignored there.
  - The flippers sit close to the body in the side view, with only a slight groove.
  - The foot undersides are filled with the foot's main colour, since no view sees them.
  - The tail is a single flat wedge, not separate feathers.
