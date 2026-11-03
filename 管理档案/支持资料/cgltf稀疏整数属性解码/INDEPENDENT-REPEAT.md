# cgltf unsigned-byte sparse accessor: independent same-input repeat

Date: 2026-11-03. Result: accepted for the three frozen generic accessor configurations only.

## Actual execution and input binding

Following static v2 acceptance and explicit execution authorization, this reviewer verified the original manifest and its exact eleven-file input set, then created the new `independent-package-2/` without overwriting an existing directory. Every copied input and manifest matched before execution. The sole runner invocation was `python3 -B independent-package-2/run.py run-2` (paths relative to this research unit). It performed **one compilation and one native invocation containing three configurations**. No retry, installation, network operation, extra scenario, or source modification was performed.

Frozen manifest SHA256: `774e45d5e4f32ea14ac109dd1b0d881ecea4d23abf7538a30a2a9369cb8e5a95`.
Runner SHA256: `a7f98208f2e6456506ac05094cf1c28ac32a38d15c41a6c6d9449cd41e7e5eec`.
Protocol SHA256: `02f4e43799238237ab602d02e7e3236e5518bd76c01c64a531df541135d6cc94`.
Upstream commit: `360db1a95480fe102ae9c69b27c5d101167ff5ba`.
Header SHA256: `e378a21c084bf1f288bb799de827bb26906efb024255f1ecf1705ea13f11c6ec`.

The complete eleven input hashes are recorded in the frozen manifest and the safe result receipt. After execution, this reviewer independently checked all eleven hashes in the original package, independent package, and runner work copy, plus both package manifests: all matched. The frozen protocol's preparation-time “NOT EXECUTED” statement remains a historical input, not the present result.

## Observed stages

Compilation used the unchanged `-std=c99 -O0 -Wall -Wextra -pedantic` options with the protocol's 30-second limit. It exited zero with empty stdout and stderr. The single native process, with the 5-second limit, exited zero with empty stderr and exactly three JSON rows. Both stage receipts record leader exit, process-group absence confirmation, and successful cleanup. These are the runner's limited group checks, not proof of sandboxing or control of descendants that leave the group. No timeout or cleanup failure was observed in this invocation; timeout handling was not experimentally challenged.

The finalized receipt says `PASS_three_configurations`, `identity_after: MATCH`, and eleven validated runtime directories. Private working files and execution diagnostics remain under `run-2/private-raw/`; this report contains no host paths, process identifiers, environment values, or installed/compiled binary fingerprints.

## Independent numerical reading

The oracle was re-derived from the frozen sixteen bytes, not from the main operator's output: base elements are `[255,0,0,0]` and `[0,255,0,0]`; sparse index 1 replaces the second element with `[64,191,0,0]`. Normalization divides each unsigned byte by 255. An absent base contributes zeros before replacement.

| Configuration | Observed eight values |
| --- | --- |
| Dense, normalized | `[1,0,0,0,0.250980407,0.749019623,0,0]` |
| Absent base, normalized | `[0,0,0,0,0.250980407,0.749019623,0,0]` |
| Dense, not normalized | `[255,0,0,0,64,191,0,0]` |

Independent rational comparisons of all 24 printed values agree with the pre-execution oracle. The printed fractional values differ from exact `64/255` and `191/255` by `757/51000000000` and `773/51000000000`, respectively, both below the frozen absolute tolerance `1e-7`. All other values match exactly. This checks the reported decimal observations against the oracle, not exact internal floating-point bit patterns.

Each actual row reports parse/load/validate status zero, query count 8, full unpack count 8, and `read_float: false`. The false sparse single-element read is the expected API boundary; no contents of its unsuccessful output buffer are used. Full unpack replaces the sparse element rather than adding to the dense base.

## Output identities and limits

- Raw numeric stdout SHA256: `f0a89e2722597c044759c9127fd36efa4ba2202fc56e6827aa6fb0192087d4d6`.
- Safe `values.json` SHA256: `5703a37ca9d36e24f053871413377aeaade518cc670c110da8896590385a318d`.
- Safe `result.json` SHA256: `e1656f6cc7c595af2cec454efdc69a16f79ce6a00691cdef970c3124926f6343`.

This is a different operator's repeat on the same host using the same program and frozen inputs. The reviewer knew the main run had succeeded but did not read its numeric output to construct this oracle. It is not an independent implementation, blind reproduction, cross-platform result, skin/weight validation, whole-format conformance claim, or engine/GPU observation. Across the two authorized operators there are repeated observations of the same three configurations, not six distinct configurations. This report does not itself authorize publication of private raw files.
