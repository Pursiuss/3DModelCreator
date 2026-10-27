To: randy.lin@algomau.ca
Subject: Penguin challenge: remaining questions after kit v0.2

Hello,

Thank you for kit v0.2 and for confirming that the blockout method is allowed, that the run has network access, and
that `out/` in the working directory is right. A few questions remain:

1. Image tools. v0.2 allows AI image tools to repair or generate views, with every call logged. Which image tools
   are allowed, and will they be available to the skill during the unattended judged run, or only while developing?

2. Gross errors on an inconsistent view. On four-view sheets I tested, the top view was drawn about 20% wider and
   20% shorter than the front and side views imply. A model that matches the front and side cannot also match
   such a top view, so the top view reports a gross error and the shape test fails, although the score itself
   uses only the best two views. Does the gross-error check apply to all three scored views, or only to the two
   that count for the score? Will the hidden animals' views be consistent enough that this cannot happen?

3. Submission format. What should a submission contain (the skill folder only, or a zip with a README), and how is
   it sent?

Thank you,
<name, student ID>
