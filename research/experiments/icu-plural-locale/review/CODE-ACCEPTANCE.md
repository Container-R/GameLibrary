# Independent pre-native source acceptance

2026-10-31 23:06 UTC. Accepted exact frozen source:

- child.py `e4f879c4b6439266d0a6f16e40be1eabd48e0b124fb8bea2119aae4dbabd8c94`
- run.py `d1013713afcfe0fd1560c572dfa367fa223738b8d371bdd5a477d2bb65af5b26`
- consume.py `a20cbbce599dca620d896ab3d29c3a475a37c322742126f48ec7d5eeb04508c8`
- test_pure.py `6f84074e040b88e129f88f7af8c30b313d9891142657a071027c2ba17f6558f1`

Protocol e44d2d3a and helper bcade741 unchanged. Copies are in `final-source/`, with exact full manifest. No CDLL, ICU/version call, child native process or legacy top-level module import was performed by reviewer. Source imports in pure tests only define the inert new ABI structure and helper functions.

## Source/control review

Explicit Linux ABI checks precede CDLL. Resolved uc/i18n libraries load only after all three pinned file hashes match. Fixed signatures match reviewed declarations, with exactly one variadic c_double. Direct uint16 array initialization avoids an extra ctypes memmove helper and preserves the ASCII UTF-16 pattern. Native calls log before/after, with bounded readbacks; successful-open status and nonnull handle precede all formatting. Format status/length checks precede UTF-16 decode, literal comparison stops at first mismatch, and finally closes every returned nonnull formatter. Before/after library checks preserve identity drift as failure.

Parent serial order, explicit fresh environment, unique receipts, source pin checks, 20-second per-child deadline and bounded group cleanup satisfy the frozen plan. Batch receipt recount distinguishes observed child receipts from unknown interrupted in-flight spawn counts; it does not assert all native attempts from a constant. Only complete accepted configuration advances the batch. Timeout/exception handling remains bounded, not a general sandbox or guaranteed reaping claim.

Consumer uses frozen ABI and exact literal outputs, not current-host native behavior. It rejects incomplete success traces, nonzero process exits, missing cleanup, bad version, non-success status, invalid lengths, wrong identity and source/raw hashes. It checks separate load events followed by the full API sequence then terminal, so filtering cannot hide reordered loading/API phases. This is archive consistency, not authenticated execution.

## Actual pure review findings and closure

Initial source had six passing author methods, but independent malformed records showed three false accepts: report input False instead of0; format attempt input False instead of0; intent accepted numeric0 instead of booleanFalse. Separate load/API filtering also lost cross-stream order. These were pre-native checker defects, not failed ICU executions. Exact initial source and probes are preserved in `initial-source/` and `initial-probe-output.txt`.

Final typed checks reject all three independently reproduced substitutions under normal and optimized Python (`final-probes*.txt`). All eight final author methods pass in both modes (`final-tests*.txt`), including newly added event-order and boolean/integer regressions. These methods use synthetic records and ABI layout inspection only; they are not native coverage of 18 format calls or evidence of installed ICU outputs. No remaining material pre-execution blocker found. Actual execution still requires coordinator authorization; no independent repeat was performed or implied.
