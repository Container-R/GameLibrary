# Independent implementation and numerical review

2026-11-01 UTC. **Accepted for the frozen finite scalar protocol. No material correction requested.**

Exact reviewed source: `scalar.py` SHA256 `832d4d3e99ef5d9525cb3b767de3f286b523305e77a5a7afb9fa776515c63e14`; `test_scalar.py` SHA256 `6e2b26c81c93181fb66b873b2439226d68ce0296607c0e30ec4d3b8b9f921dfe`; protocol `b39a921ebd231066e3d31ea2e52b3193212255210a63feb94c9ef1c016784c27`. Both copied source hashes match originals. Originals were not changed.

## Independence and actual executions

Before seeing author code/results, reviewer froze `reference/reference.py` (`0399074e…`) and ran its independent ODE integration once, retaining both resolutions and transition results. This uses the prescribed derivative, not the closed-form expression or author helper. Its RK4 method is mathematically the same classical method by design, not an independent numerical-method family.

After author freeze, reviewer read the full two files, README, RESULTS and author outputs. Copied exact code and parent protocol to `repeat/`; ran normal and optimized modes once each with distinct new output paths. Both exit 0, each 8 methods and 139 guard subcases. These are two additional suite executions, not new scenarios. Logs and JSON are retained in `repeat/fixture/`. No native engine or installed third-party library was run.

Original `reference/compare.py` (`2f4926b0d3bd9783bd3545b1ec9f13ead38b5066c616dc8ae6920ca01e8ec9b0`) then read all four author/reviewer outputs in one pure Python process. It checked both residual components at all 35 case/time rows against the prior independent coarse/fine arrays, recomputed error/refinement acceptance, and compared transition pairs/final state against independently integrated transition dynamics. Core fine-reference comparison uses the frozen 1e-7 tolerance; it does not apply the tighter analytic partition tolerance to a numerical ODE approximation. Matching RK implementations also agree within the reader's 1e-11 diagnostic tolerance. Comparison output and empty stderr retained. Final-state differences from independent fine integration are approximately (8.57e-12, 2.29e-11), not claimed exact agreement.

Reviewer process count to this acceptance: 1 original reference execution + 2 copied-suite executions + 1 static numerical reader = 4 pure Python processes. Author's 2 suite executions remain separate. No failed native attempt, engine, animation assets, participant observations, or performance evidence.

## Source inspection findings

- `number` rejects bool/custom types before conversion and rejects conversion overflow/nonfinite/out-of-domain values. All public state-pair inputs and outputs pass the same finite bounded validation. Pure functions return only after complete pair construction; no mutable-state transaction is being inferred.
- `decay` implements the accepted constant-rate initial-value solution; zero dt returns the validated pair. `rebase` uses actual output minus target for both components. `compose` adds same-time states. No epsilon snap, hidden rate conversion, clipping or fitted tolerance.
- Author RK4 stages use only the ODE derivative and independently restart coarse/fine from initial conditions. The written stages are classical RK4; the reference neither invokes `decay` nor an exponential. Both components and errors are finite-checked before acceptance. The coarse/fine maximum and small-error branch implement the frozen criterion.
- Direct event evaluation advances the old residual to the boundary before sampling LEFT target, rebasing against RIGHT target and composing at zero new age. Partition tests construct a rational time-grid union with both event boundaries, advance to each interval's end, and change target only after the old-side composition there. Both declared transitions are checked exactly once; final comparisons cover both components.
- The incomplete initializers discriminate the intended mistakes. Interrupted raw-target-only initialization requires both jumps >0.01. The first acceleration discontinuity is explicitly a C2 counterexample, not a C1 failure. Growth, zero crossing with nonzero velocity and the half-life convention are labeled counterexamples/limits, not defects.
- Explicit unittest methods remain active under optimized mode. The 139 rejection subcases are not 139 separately named tests. Invalid-output checks are distinct from invalid-input checks; endpoint cases avoid claiming the whole accepted input box is invariant.

## Limits and receipt handling

This is a small unittest harness, not the repository's hardened native-runner framework. Its README requires a new output path; it does not clear an arbitrary preexisting JSON before import/startup failure. Review uses fresh copies/new filenames plus actual exit/logs, so no stale-PASS claim is made. Do not market it as generic fail-closed archive ingestion or use a leftover JSON alone as a new invocation receipt.

Finite RK4 agreement and two-level refinement corroborate this implementation over the declared domain/cases; they are not a general error theorem. No independent renderer, contact solver, quaternion treatment, pose evaluator or target-derivative estimator is involved. Keep existing foot-contact and native animation evidence explicitly separate.
