# Frozen literal checker and independent repeat

2026-11-01 UTC. **Accepted for the two successful configurations and five declared rejection cases.** No changes to expected values, author sources, checker, or tolerance after seeing output.

## Exact source/oracle identity

- Reader: `f4236faccf9de7d57f65d5f4e68f8e900865bac7cd42f480e5cfe81f6d376f91`.
- Runner: `a1364f544309e0e45a0f70c375092eda4976d271b8371595da6ca2e1fcb03065`.
- Protocol: `de8c9bd74299fb409d58859a099de8b5ff2802df6b78ba1308400762b294172d`.
- Pre-implementation literal oracle: `expected.json`, `b936312a481fe04c51d8f61ae965f7a43ba8589246d39138e831245859787623`.
- Pre-output checker: `check.py`, `20901fdd4f66eaaac7d1ddd7c8bc2041ae04215ba899247fa91e23fa650637e9`.

The checker imports no author decoder and derives expected values/addresses from the literal oracle frozen before author code inspection. It is an archive checker, not a second general glTF decoder or execution-authentication system.

## Actual authorized sequence

1. Ran frozen checker against author `results/` plus `author-execution/` streams/exit receipt: exit 0, empty checker stderr, PASS. Exact invocation/output/source hashes retained in `author-static/`.
2. Copied only exact reader/runner/protocol to fresh sibling `../independent-repeat/`; recorded before hashes, command, UTC start/end, stdout/stderr, exit and after hashes. One normal Python runner invocation exited 0 with empty stderr. Before and after three-source hashes are identical. No originals were changed.
3. Ran frozen checker against that repeat and its actual raw receipts: exit 0, empty checker stderr, PASS. Command/output/source hashes retained in `repeat-static/`.

Author plus reviewer therefore ran **two runner processes with the same seven unique semantic cases**, not fourteen unique cases. This reviewer additionally ran **two static checker processes**, not extra decoder cases. No new malformed probes, optimized invocation, native engine, DCC, installation or network fetch occurred in this execution review.

## Observed binding and literal result

Both result documents retain the exact 44-byte input and full expected metadata/data URI. Both successful results include complete values, base addresses, sparse index/value addresses, destination indices and replacement values. Dense output is [10,7,30,9], absent-base output [0,7,0,9]; sparse indices are read at18/20 and values at28/32. Five negative case labels agree with the frozen expected four distinct error categories. Mutated negative inputs are generated in memory by the bound runner source, not separately archived binary inputs; this check does not pretend otherwise.

Both invocations produced identical stdout SHA256 `7ee7f43985cbd93da69bd1d41ee7c3632e57661e6a472ba90fb7b9bf844c5f15` and summary SHA256 `892b9c2e41b8b35eea4b79a780e4bbf5dcd1eef843fdecc849b3f93de853c33e` on this shared environment. This is observed identity of these receipts, not a platform-independent determinism guarantee. All CASE_JSON lines and the single RESULT_JSON are structurally associated with their parsed summary; both input artifact hashes bind the actual files.

## Editorial read before placeholder replacement

Read `gltf-sparse-editorial/section.md` and `source-note.md`. Their finite representation scope, replacement-vs-addition distinction, view-local bounds, five cases versus four error labels, strict-int subset caveat and nontransfer of Godot evidence are accurate. `EXECUTION_PENDING` must be replaced before publication with the actual counts above; no final acceptance of an unfilled publication placeholder is implied. No other substantive editorial correction identified. The prior source/protocol reviewers provide the normative-source review; this record primarily establishes independent predeclared numeric/address expectations and actual archived execution agreement.
