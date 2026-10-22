To: randy.lin@algomau.ca
Subject: Penguin challenge: remaining questions after kit v0.2

Hello,

Thank you for kit v0.2. It answers my earlier questions about the colour score (now compared with the reference
views), the nose direction (-y) and the reference style (cut-outs on a transparent background, orthographic views
that may disagree with each other). A few questions remain:

1. How the shape is made. The allowed model (Claude) looks at the references and writes a blockout: a short list
   of simple solids (ellipsoids, tapered capsules, flat tapered plates, boxes) with positions and sizes in metres,
   much like a modeller blocking out in Blender. Ordinary geometry code then fits those solids to the reference
   outlines, trims them where they stick out, smooths the result, and textures it from the reference pictures. No
   image-to-3D or text-to-3D generator is used. Is this allowed under "AI 3D generation is not allowed (anything
   that produces a 3D shape from text or images)"?

2. Run environment. In what environment do staff run the skill (which agent harness, OS, Python version)? Can the
   skill `pip install` numpy, Pillow, scipy and scikit-image into its own virtual environment, or will they already
   be installed? Is there network access during the run?

3. Output location. Should `out/` be created in the working directory the skill is started in, or next to the refs
   folder?

4. Image tools. v0.2 allows AI image tools to repair or generate views, with every call logged. Which image tools
   are allowed, and will they be available to the skill during the unattended judged run, or only while developing?

5. Submission format. What should a submission contain (the skill folder only, or a zip with a README), and how is
   it sent?

Thank you,
<name, student ID>
