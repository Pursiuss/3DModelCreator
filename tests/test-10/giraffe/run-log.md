# Run log

## Pipeline run 2026-10-31 00:14:02

Why this run: round-3 blockout, legs pinned to measured joints; top and back skipped per view check

- Command: `build.py refs/giraffe out --parts out/work/parts.fitted.json --skip-view top back --note round-3 blockout, legs pinned to measured joints; top and back skipped per view check`
- Shape: blockout (27 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (17.86 mm voxels), smoothed; kept 1 of 5 mesh pieces; built on a finer grid and joined on: mane, front leg A, front leg B, hind leg C, hind leg D, tail, tail tuft
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.129, 'back': 0.149, 'side': 0.269, 'side_mirror': 0.277, 'top': 0.022, 'unseen_filled': 0.154, 'duplicate_features_removed': 4, 'uv_islands': 30, 'texel_mm': np.float64(3.32), 'palette_colours': 5}
- Self-check (own masks, kit v0.2 scorer): shape 0.909 (textured 0.909), gross errors top, colour 0.888
- Warnings: front width 0.908 m vs top width 0.718 m disagree by more than 8% (pose or framing differs); side length 3.221 m vs top length 3.896 m disagree by more than 8% (pose or framing differs); front and mirrored back outlines overlap only 0.76, even lined up as well as they can be: pose differs between views; a loose piece (0.8% of the model) came off and was dropped: a part (often a tail, ear or horn) joins the body only where trimming cuts it; start it inside the part it grows from, and build a thin tail, strand or leg as a chain (thin chains are built on a finer grid, with whatever hangs from them); kept untrimmed, because trimming to the outlines would have removed most of them (they are off their drawn place; move them onto it in parts-on-refs.png): hoof C inner, hoof D inner
- Time: 323.1 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: low (reasoning effort setting 15)
- Animal: reticulated-pattern giraffe, quadruped standing mid-stride. Parts modelled (27): torso loft (8 stations), neck chain (flat-sided, aspect 0.55), long-face head capsule, lower jaw, nose/muzzle tip, 2 ossicones with dark knobs, 2 ear paddles, mane chain (#5b3314), 2 front shoulder capsules + 2 hind thigh capsules, 4 separate lower-leg chains (legs drawn mid-stride, so not mirrored; forward legs on +x), 8 hoof claw paddles (cloven, #2c2520), tail chain and black tail-tuft chain with strands. Eyes left to the texture.
- View disagreement: measure.py's view check found the top view drawn at other proportions (length 3.90 m vs side 3.22 m, width 0.72 m vs front 0.91 m) and the back view in another pose (front/mirrored-back overlap 0.76). Both were passed as `--skip-view top back` to every fit and build; modelled from front and side.
- Blockout rounds: 3.
  - Round 1: fitter reached front 0.95 / side 0.96 overlap but scrambled the legs (joints crossing to the other side, a fetlock below ground) and reported hooves/ears thinner than 1.5 voxels, root bulges on neck, thighs and tail.
  - Round 2: legs, shoulders, thighs, hooves and tail reset to measured values with "fit": false; hooves and ears thickened to 27 mm half-thickness; neck and tail roots moved deeper, neck root_blend 0.3; tail tuft ignores the front view (it draws the tuft at another height). Overlap front 0.84 / side 0.91 (legs too close to the centre line in front view).
  - Round 3: front legs moved out to x ±0.18-0.20 with aspect 1.3, hind legs to x ±0.11-0.13, hooves re-centred, hind leg C gaskin/stifle and front leg B forearm moved back. Overlap front 0.92 / side 0.92, no part-check problems.
- Build runs: 1, final options: `--parts out/work/parts.fitted.json --skip-view top back` (full build, no --quick).
- Final self-check: shape 0.909, gross errors [top], colour 0.888. Per view IoU / colour: front 0.907 / 0.862, side 0.910 / 0.914, top 0.632 / 0.857, back (not scored) 0.737 / 0.839.
- Image-generation calls: none (no AI image tool was used to repair or generate views)
- What failed or looks weak:
  - Gross error in the top view: the top reference is drawn ~21% longer and ~21% narrower than the side and front views, so no model true to the front and side can match it; the model was not distorted to chase it.
  - Hooves come out small: after trimming they read as small dark tips rather than the drawn wedges; hoof C inner and hoof D inner were kept untrimmed (off their drawn place in the front view).
  - A loose piece (0.8% of the model) was dropped by the build.
  - A few pale filled patches on the back/rump where no picture sees the surface squarely (filled from neighbours, 15% of the surface).
  - Tail tuft reads flatter than the drawn brush.
