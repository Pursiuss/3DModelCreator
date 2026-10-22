"""Sanity check: a plain box of the animal's real size. Should score about 0.5 on shape.

usage: python make_box.py REFS_DIR OUT.glb
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skill", "scripts"))
from glb_io import write_glb

refs, out = sys.argv[1], sys.argv[2]
s = json.load(open(os.path.join(refs, "subject.json")))
w, l, h = s["width"], s["length"], s["height"]
V = np.array([[x, y, z] for z in (0, h) for y in (-l / 2, l / 2) for x in (-w / 2, w / 2)])
F = np.array([[0, 2, 1], [1, 2, 3], [4, 5, 6], [5, 7, 6], [0, 1, 4], [1, 5, 4],
              [2, 6, 3], [3, 6, 7], [0, 4, 2], [2, 4, 6], [1, 3, 5], [3, 7, 5]])
write_glb(out, V, F)
print("wrote", out)
