# Observation-end instrumentation correction review

2026-10-31 23:47 UTC. Accepted corrected main.gd SHA256 `4a6006f6ef378cf1c8801e1b77cc2cd5de354b25ade331682a112690233102ff` for a separately authorized fresh attempt. Exact diff adds only the `finished` early return to record(); seven other frozen source files are unchanged.

Read failed UUID fb2313fd-98a4-44b1-9527-12547d3925af receipt and both behavior streams. Both native processes returned zero, but two SCRIPT ERROR null get_instance_id diagnostics caused the runner to fail, correctly. Diagnostic parsing of its serialized 20-row result satisfies the prior trace oracle; this does not convert the invocation to PASS. Separate stdout/stderr do not establish temporal order. The multiline dictionary error location does not identify the exact null expression. Teardown is a source-consistent hypothesis, not a demonstrated engine defect or authenticated source match.

Verified the historical eight-source hashes against the failed receipt and all five receipt/raw files byte-for-byte against original evidence. The added guard closes observation only after final snapshot and postcall gate, or explicit failure termination. It does not suppress diagnostics occurring within the measured sequence, alter the successful 20-row oracle, or relax the runner's empty-stderr requirement. CORRECTION.md states these boundaries accurately.

No engine/version invocation or independent retry by this reviewer. Main authorization is still required for any fresh attempt. Original failed evidence must remain failed and preserved regardless of later results.
