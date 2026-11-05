# Auto-score 2026-11-04_dropped-parts

| animal | from | shape | front / side / top IoU | gross errors | colour | pass |
|---|---|---|---|---|---|---|
| cow | tests/test-09/cow | 0.906 (=) | 0.907 / 0.894 / 0.905 | none | 0.834 (=) | yes |
| dog | tests/test-09/dog | 0.926 (=) | 0.928 / 0.924 / 0.908 | none | 0.903 (=) | yes |
| giraffe | tests/test-12/giraffe | 0.898 (=) | 0.861 / 0.895 / 0.901 | none | 0.906 (=) | yes |
| penguin | tests/test-09/penguin | 0.903 (=) | 0.903 / 0.904 / 0.842 | none | 0.877 (=) | yes |
| sheep | tests/quick-tests/sheep | 0.936 (=) | 0.919 / 0.934 / 0.939 | none | 0.893 (=) | yes |
| stag | tests/test-13/stag | 0.863 (new test) | 0.835 / 0.892 / 0.733 | none | 0.897 (new test) | yes |

Scored with the kit's score_glb.py; pass = shape >= 0.8, no gross errors, colour >= 0.8; changes in brackets are against run '2026-11-03_this-machine' ("new test": that animal is now rebuilt from a newer saved test, so its scores are not comparable).
