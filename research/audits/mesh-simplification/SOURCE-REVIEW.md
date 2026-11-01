# meshoptimizer request/result boundary — source review

2026-11-01 UTC. **ACCEPT for a bounded standalone source note.** Gate SHA256 `c1c7b3dd0e7c1121e88230fe45dbee170b70b4c2137a78d1f6b338a580f25cea`. No material correction required.

## Exact original source inspected

Independently resolved official `v0.25` to `6daea4695c48338363b08022d2fb15deaef6ac09` and fetched the pinned files:

- [README, Basic simplification](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/README.md#L431-L454): requested reduction may stop short, its metric is approximate, and resulting indices reference original vertices. This supports a request-versus-accepted-result distinction, not a visual tolerance guarantee.
- [Header contract](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/meshoptimizer.h#L432-L448) and [scale conversion](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/meshoptimizer.h#L540-L546): actual returned index count and worst-case original-count destination capacity are explicit. Error conversion directions agree with the gate.
- [Simplifier source](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/simplifier.cpp): inspected rescalePositions 546–599; performEdgeCollapses 1462–1528; entry assertions 2279–2293; scale selection 2339–2341; loop/stop conditions 2421–2465; return/wrapper 2554–2565; simplifyScale 2870–2879. These support the described finite source mechanisms, without establishing the cause of any unobserved shortfall.

## Necessary bounded nuances

1. Counts are **indices**, not vertices. The proposed 300/150/75 counts are triangle-compatible. Collapses remove triangles discretely; do not turn a target into an exact-equality requirement. A returned count meeting a cap is distinct from matching it exactly. The code's target-dependent collapse goal does not supply a monotonic-output guarantee across the two independent requests.
2. With options zero, scale is the largest axis extent over the supplied vertex array, not a bounding-box diagonal or automatically a referenced-only subset. Sparse mode changes the extent domain; absolute-error mode changes units. Keep those modes outside the example and bind the scale to the same supplied vertex data. Finite nonzero extent is a necessary condition for the proposed division.
3. The ordinary wrapper supplies no attribute metric. Existing seams/topology and full vertex identity still matter, but the reported position-oriented approximation is not a bound on UVs, normals, skinning, silhouette or perception. Attribute-aware APIs must not silently inherit this metric interpretation.
4. The relative-to-model-unit multiplication is arithmetic, not observed displacement or a theorem about maximum surface error. A normal return and an error value do not certify appearance or performance.

## Acceptance of proposed example

Both requests remain unexecuted and have no fabricated result counts. Original-count output capacity is correctly retained even when the target is much smaller. Result count, metric, storage and downstream acceptance remain separate. No unconditional recommendation to relax error or switch algorithms follows. Existing accessor/import and texture evidence is not reused as simplification validation.

No simplifier execution, geometric fixture, model, image inspection, installation, engine or native experiment performed. The useful scope ends at source-supported request/result acceptance, not inferred outcomes on an unknown mesh.
