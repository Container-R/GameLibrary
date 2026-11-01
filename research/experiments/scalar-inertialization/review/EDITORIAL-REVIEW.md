# Independent editorial and numeric evidence review

2026-11-01 02:13 UTC. Accepted scope and numerical reporting, with one narrow mathematical wording correction requested before final closure. No new model/native suite executed; only archived JSON arithmetic readback.

Reviewed draft hashes:
- `article-draft.md`: `5cfda3c7341137576563875efc8482b4b02a1d627f5c013f436a2cd05e1b93ae`
- `source-note.md`: `865d18fbc8433eed187063ac1a20ffdb453a67fd63d368cbfaf62116fd045d72`

## Correction

“目标每段可微且导数正确时保证转场的 C1 连续” should state piecewise C1 targets with finite one-sided value/derivative limits at transition boundaries and correct same-time sampling. Mere differentiability does not ensure continuity of the derivative. The acceleration comparison should explicitly apply when the corresponding one-sided second derivatives exist. The actual analytic targets in this fixture satisfy these conditions, so this is a prose-premise refinement, not an observed numerical failure.

## Accepted findings

Independently opened Holden’s original page and read the named critical-damper, half-life and inertialization text. Compact attribution is accurate: spring residuals preserve existing offsets during interruption; no fixed finish time or arbitrary-initial-state monotonicity is implied. Standard exponential implementation and own notation are separated from source approximation, demonstration and performance. Bollo remains an excluded historical alternative, not implemented damaged-OCR coefficients. No broad copyright permission inferred.

Recomputed all seven position/velocity fine-error maxima from the author's archived rk4_rows: every rounded table value matches. Checked the raw transition, expected-counterexample and independent-comparison records: velocity-only loss 0.3292627983; interrupted losses 0.9326096119 and 0.8882555148; acceleration jump 1.4829488067; growth 1.1682011746; crossing velocity -0.7357588823; half parameter result 0.5965735903; independent final differences 8.572476e-12 and 2.288636e-11. Counts match the numerical review: four same-suite executions, each eight methods with 139 guard subcases nested in one method, plus separate pre-author reference integration and later static reads. No new scenarios are manufactured from repeats.

The residual ODE solution/derivative algebra is correct for constant positive rate; infinite-time decay, possible initial growth and zero-crossing with remaining velocity are distinguished. C1 is not C2, two component units are kept separate, two RK4 implementations are not different method families, and finite samples/refinement do not prove global bounds. Parameter/guard domain, non-invariant output range and fresh-output/exit-status limitation are explicit. Foot contact, engine/visual performance and rotation are not upgraded.

Fixture and source-note links target the proposed publication layout; the existing root-motion link resolves from the intended animation article directory. Final prose closure should pin the corrected hash separately.
