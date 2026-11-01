# Main source and hand-derivation check

2026-11-01 UTC. Read the original Garland–Heckbert paper's extracted text, physical pages 3–5 (§§4–6.1), and the finite-plane limitation in physical page 6, §7. No visual inspection of figures is claimed. The paper's separate sampled, average squared surface-distance assessment is not a maximum error guarantee.

Read pinned meshoptimizer v0.25 commit `6daea4695c48338363b08022d2fb15deaef6ac09`, `src/simplifier.cpp` lines 765–856, 1046–1141 and 2381–2386. Position normalization, default point regularization and eligible edge contributions prevent interpreting the isolated plane equation as the full library metric. Ordinary API original-vertex reuse and admissibility remain independent restrictions.

Independently checked the proposed exact proof: all points of the closed triangle satisfy x≤1, so (2−x)²+y²≥1 with equality at (1,0,0); the unit-normal z=0 plane residual at P=(2,0,0) is zero. This is an original finite geometric distinction, not a constructed simplification output or measured silhouette. No executable or numerical test was run. The complete-metric and candidate restrictions must remain adjacent to the proof.

Primary sources: [original paper](https://www.cs.cmu.edu/~garland/Papers/quadrics.pdf), [pinned implementation](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/simplifier.cpp). No third-party figure, raw source body, runtime metadata or asset is included in this record.
