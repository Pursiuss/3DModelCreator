# Run log

## Pipeline run 2026-11-03 15:20:16

Why this run: round 3 blockout, quick check

- Command: `build.py refs/giraffe out --parts out/work/parts.fitted.json --skip-view back --quick --note round 3 blockout, quick check`
- Shape: blockout (24 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (27.78 mm voxels), smoothed; kept 1 of 3 mesh pieces; built on a finer grid and joined on: front lower leg R, front lower leg L, hind lower leg R, hind lower leg L, front hoof R outer, front hoof R inner, front hoof L outer, front hoof L inner, hind hoof R outer, hind hoof R inner, hind hoof L outer, hind hoof L inner, tail, tail tuft
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.112, 'back': 0.16, 'side': 0.206, 'side_mirror': 0.199, 'top': 0.019, 'unseen_filled': 0.304, 'duplicate_features_removed': 3, 'uv_islands': 28, 'texel_mm': np.float64(6.26), 'palette_colours': 4}
- Self-check (own masks, kit v0.2 scorer): shape 0.905 (textured 0.905), gross errors none, colour 0.908
- Warnings: front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views
- Time: 97.4 s

## Pipeline run 2026-11-03 15:23:24

Why this run: final: round-3 blockout, ossicones as chains, ears on fine grid

- Command: `build.py refs/giraffe out --parts out/work/parts.fitted.json --skip-view back --note final: round-3 blockout, ossicones as chains, ears on fine grid`
- Shape: blockout (24 parts from parts.fitted.json) grown 0.0 mm, trimmed to the outlines (17.86 mm voxels), smoothed; kept 1 of 1 mesh pieces; built on a finer grid and joined on: tail, tail tuft, ear, ossicone, ossicone knob
- Texture: projected from the reference views (share per view, and share filled from neighbours): {'front': 0.085, 'back': 0.223, 'side': 0.209, 'side_mirror': 0.207, 'top': 0.045, 'unseen_filled': 0.231, 'duplicate_features_removed': 3, 'uv_islands': 30, 'texel_mm': np.float64(3.11), 'palette_colours': 4}
- Self-check (own masks, kit v0.2 scorer): shape 0.898 (textured 0.898), gross errors none, colour 0.906
- Warnings: front and mirrored back outlines overlap only 0.78, even lined up as well as they can be: pose differs between views
- Time: 170.2 s


## Agent summary
- Models used: Claude Opus 5.5 (claude-opus-5-5), effort: low (reasoning effort setting for this session)
- Animal: reticulated-style giraffe (5.0 m tall), standing quadruped in a slight walking stance. Parts: loft torso (7 stations), 6-joint neck chain, long-face head capsule + lower jaw, two ossicones (chains, fine grid) with dark knobs, two ear paddles (fine grid), eyes, front and hind upper legs (mirrored capsules), four separate lower-leg chains (knee/hock, cannon, fetlock, hoof top), eight wedge hoof claws (cloven, two per foot), tail chain and an 8-strand dark tail tuft. Left out: the short neck mane (inside the neck outline; left to the texture) and a separate nose pad (fully inside the head tip, so it was dropped).
- Note: this session picked up a giraffe blockout from an earlier unfinished run in out/work (parts.json, fit and zooms from 2026-11-02); measure.py was re-run on the same refs before building on it.
- View check: front and mirrored back outlines overlap only 0.78 (pose differs), so `--skip-view back` was used for every fit and build. The front view does not draw the tail/tuft hanging between the legs (the back and side views do), so "front" is in the tail's and tuft's ignore_views; "top" is also ignored for the tuft (hidden under the tail), ears, ossicones and knobs.
- Legs drawn mid-stride (side view shows the +x legs forward), so all four lower legs are separate parts at their drawn positions rather than mirrored.
- Blockout rounds: 4 fits.
  1. Measured lower legs and wedge hooves pinned (`fit: false`), tail tuft re-attached inside the tail tip, eye moved onto the drawn eye, nose shrunk.
  2. Let the fitter move the lower legs again: it pulled fetlocks and hooves sideways and detached upper from lower legs, so this was reverted.
  3. Re-measured the front legs on a front-view zoom (knee at z 1.22, fetlock at 0.30, claw widths); all leg pieces pinned with upper legs ending exactly on the lower-leg chains; hoof claws widened to the drawn width; nose dropped.
  4. Hind gaskin made deeper front-to-back (aspect 0.55) to fill the side view while staying hidden behind the front legs from the front.
- Build runs: 2 (one `--quick` check, then the final full build). The quick build lost the ears and ossicones, so for the final build the ossicones became chains and the ears were set to `fine: true`; both survive. Final build options: `--parts out/work/parts.fitted.json --skip-view back`.
- Final self-check: shape 0.898, gross errors none, colour 0.906. Per view IoU / colour: front 0.861 / 0.897, side 0.895 / 0.915, top 0.901 / 0.810 (back 0.735 / 0.882, not scored: skipped view).
- Image-generation calls: none (no AI image tool was used to repair or generate views).
- What failed or looks weak: the ears come out as thin pale blades rather than leaf-shaped cups; the head is slightly small and the muzzle simple (no gape line modelled); the short mane is not a separate part; the tail tuft can be seen hanging between the legs from the front, which the front drawing does not show; front-view IoU (0.86) is limited by the thin legs, where a few cm of offset cost a lot; top-view colour is the weakest (0.81).
