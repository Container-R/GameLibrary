# Main source read — sensor occupancy and swept traversal

2026-11-01. The official tag API confirmed v3.1.1 points directly to the old commit; the newer commit API reports 2026-10-30. Source-only review; no engine execution, event trace, performance result or fixture claim.

Directly read official erincatto/box2d files pinned to v3.1.1 commit `8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3`: simulation.md 922–956 and 1744–1834; world.c 695–793; sensor.c 47–106 and 135–186; solver.c 212–245 and 425–450. Positive world-step control flow invokes the overlap pass after solving, rather than once per solver substep. Current-transform distance tests and both continuous sensor exclusions support the historical limitation, not a statement about all versions.

Directly read main snapshot `dd8bd3fb525f0f33f1079f8ca3c5770783c44a53`: simulation.md 1071–1103; solver.c 138–425, 542–550 and 1935–1964. Candidate sensors can enter the TOI path when event and collision filters permit. The temporary hit array is bounded at eight within this continuous context; the initial comparison is inclusive, but final forwarding requires fraction strictly less than the final solid fraction. The fast shape itself still skips continuous work when it is a sensor. Static tree lookup and additional bullet tree queries do not prove arbitrary moving-sensor reliability.

The newer documentation explicitly qualifies reliable detection to non-moving sensors. This snapshot is not identified as a released version, and website deployment equivalence is not established. A geometric crossing assumption is not a generated trajectory; a proposed cast needs explicit volume, interval, initial-overlap and result-merging policies. No claim about exact begin/end delivery ordering is derived from these excerpts.

The public addition is a new source note with safe indexes. Existing solution and runtime evidence bodies remain unchanged.
