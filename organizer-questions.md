To: randy.lin@algomau.ca
Subject: Penguin challenge: questions about the rules and the scoring script (kit v0.1)

Hello,

I'm working on the "Can you ask AI to make a penguin?" challenge and have some questions about the kit v0.1.

1. How the shape is made. The allowed model (Claude) looks at the references and writes a blockout: a short list
   of simple solids (ellipsoids, tapered capsules, boxes) with positions and sizes in metres, much like a modeller
   blocking out in Blender. Ordinary geometry code then fits those solids to the reference outlines, trims them where
   they stick out, smooths and textures the result. No image-to-3D or text-to-3D generator is used. Is this allowed
   under "AI 3D generation is not allowed (anything that produces a 3D shape from text or images)"?

2. Colour match and backdrop. `colour_match` compares the texture image with all of `final.png`. The practice
   `final.png` is mostly sunset sky and ice, and `subject.json` has no `backdrop` key, so the backdrop decides the
   score. A strip of only sky from `final.png` scores 0.68 against `final.png`, while every penguin reference view
   scores at most 0.21. A penguin texture coloured faithfully therefore cannot reach the 0.80 bar. Will the hidden
   animals' `final.png` have a plain backdrop declared in `subject.json`, or will the colour bar or the script
   change? If neither, is filling unused texture space with backdrop colours acceptable, or would that count as
   gaming the metric? (My skill does not do this.)

3. Nose direction. The header of `score_glb.py` says the nose points towards +y. All four practice masks put the
   beak at -y (the front camera looks along +y and sees the face). I build the model to match the masks. Which one
   will the expert reviewers check?

4. Run environment. In what environment do staff run the skill (which agent harness, OS, Python version)? Can the
   skill `pip install` numpy, Pillow, scipy and scikit-image, or will they already be installed? Is there network
   access?

5. Output location. Should `out/` be created in the working directory the skill is started in, or next to the refs
   folder?

6. Reference style. Will the hidden animals' views always have transparent backgrounds, as the practice set does,
   and always be orthographic, in the same pose in every view?

7. Submission format. What should a submission contain (the skill folder only, or a zip with a README), and how is
   it sent?

Thank you,
<name, student ID>
