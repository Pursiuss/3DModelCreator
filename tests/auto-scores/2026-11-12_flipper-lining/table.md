# Auto-score 2026-11-12_flipper-lining

| animal | from | shape | front / side / top IoU | gross errors | colour | pass |
|---|---|---|---|---|---|---|
| cow | tests/test-15/cow | 0.912 (new test) | 0.888 / 0.936 / 0.885 | none | 0.857 (new test) | yes |
| dog | tests/test-15/dog | 0.934 (new test) | 0.925 / 0.944 / 0.908 | none | 0.891 (new test) | yes |
| giraffe | tests/test-15/giraffe | 0.899 (new test) | 0.852 / 0.912 / 0.886 | none | 0.905 (new test) | yes |
| penguin | tests/test-17/penguin | 0.915 (new test) | 0.935 / 0.896 / 0.845 | none | 0.894 (new test) | yes |
| sheep | tests/test-15/sheep | 0.930 (new test) | 0.931 / 0.928 / 0.929 | none | 0.878 (new test) | yes |
| stag | tests/test-15/stag | 0.855 (new test) | 0.840 / 0.871 / 0.719 | none | 0.891 (new test) | yes |

Scored with the kit's score_glb.py; pass = shape >= 0.8, no gross errors, colour >= 0.8; changes in brackets are against run '2026-11-04_dropped-parts' ("new test": that animal is now rebuilt from a newer saved test, so its scores are not comparable).
