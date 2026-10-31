# Final v2 texture runner acceptance

2026-10-31 18:35 UTC. Final runner `1ca81455b9ef0605a01b7dbfff15454a3294c16bfe335e5f964919ba251b7cef`, unchanged model `cea6af8ac132485f7492ee60ab1019daaf9f690257bafc62d989fcfdc5697544`. Previous offset-only17fe run remains separately in deep-qa/texture-runner-v2 and texture-runner-negative-v2, not current final-source evidence.

Read final diff: numeric blocks_x/y now checked against expected logical dimensions rounded independently, in addition to literal sizes, cumulative offsets, and pre-optional-import cleanup. No material remaining issue in finite tested scope.

Actual commands (both exit0):
```
python3 research-drafts/deep-qa/texture-runner-v2-final/fixture/run.py > research-drafts/deep-qa/texture-runner-v2-final/run-output.txt 2> research-drafts/deep-qa/texture-runner-v2-final/run-stderr.txt
python3 research-drafts/deep-qa/texture-block-budget/check_raw.py research-drafts/deep-qa/texture-runner-v2-final/fixture/results > research-drafts/deep-qa/texture-runner-v2-final/independent-output.json
```
Full14 numeric cases/6invalid guards/6actual wrapped decodes/one truncated-length refusal pass; independent original byte/pixel/prefix oracle also passes, adding6 actual same-decoder calls. Original getdata warning preserved. This is twelve positive CPU decode calls combined, not additional formats or GPU tests. Artifact bytes/hash unchanged.

Negative harness final copy adds explicit early -O rejection and separate blocks_x/y mutants; historical harnesses untouched:
```
python3 research-drafts/texture-runner-negative-v2-final/check.py research-drafts/texture-runner-v2 research-drafts/deep-qa/texture-block-budget/check_raw.py > research-drafts/texture-runner-negative-v2-final/output.txt
```
Harness exit0 means observations captured. Independently asserted all12 child exits are1: seven runner cases (-O, PIL import, model import, numeric-size, offset, blocks_x, blocks_y) and four direct checker failures plus terminal checker after rejected offset mutant. All seven runners leave no old/new summary. Terminal checker now rejects missing summary, not an offset assertion; original v1 independently rejected the wrong-offset PASS and preserves that distinct evidence. No final negative reaches actual decode. Read-only checker retains input files intentionally.

`python3 -O research-drafts/texture-runner-negative-v2-final/check.py` exits1 before argument parsing/child dispatch with exact Refusing optimized negative harness message. Captured optimized-stdout.txt (empty) and optimized-stderr.txt. This invocation leaves prior normal-run observation receipt unchanged; it is not labeled a new completed negative run. Startup/import/permission/OS failure universality is not claimed.

No original/main/remote edits; source and all evidence retained in separate directories. Archive checker dependency must be supplied with correct relative location by integrator; commands above are historical actual execution paths.
