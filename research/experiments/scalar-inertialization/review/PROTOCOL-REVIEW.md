# Independent numerical protocol review

2026-11-01 UTC. Candidate `animation-smoothing-triage/protocol.md` SHA256 `609407e015316007900c2366ff4531daf010ad6dc3bfd327106bee42824c87f2` read in full. Source review: `SOURCE-REVIEW.md` (`8a3c0c92…`). **Conditional acceptance pending the narrow negative-control correction below.** No implementation, numerical evaluation, engine, or native execution in this review.

## Required correction

Section 5, negative control 2 currently accepts value OR velocity jump. Require BOTH absolute discontinuities >0.01 in their respective units. The chosen second switch is deliberately nondegenerate, so an OR check needlessly permits one lost discriminator.

Independent algebra, not executed results: immediately after A→B at t=3/4, the residual pair is `r0=-0.7-0.5*sin(1.5)`, `u0=0.4-cos(1.5)` and `B=-1-sin(1.5)-cos(1.5)`. At elapsed 3/8 the surviving position is `[-1.075-0.875*sin(1.5)-0.375*cos(1.5)]*exp(-0.75)` and velocity is `[1.15+0.75*sin(1.5)-0.25*cos(1.5)]*exp(-0.75)`. Both are nonzero with substantial margin; the raw-target-only rebase loses each component. Preserve the candidate hash/history when changing the requirement.

## Accepted mathematical/test scope

- The seven cases cover zero state, pure displacement, pure velocity, initial growth, a position zero crossing, opposite signs, and distinct rates. Both nonzero-time state components are compared. The bounded API permits input tuples whose outputs are rejected; that is explicitly stated, rather than claiming its box domain is invariant.
- RK4 is specified solely by the two-state ODE, with independently started coarse/fine trajectories. Exact dyadic sample times avoid interpolation as a hidden reference. The absolute fine-error threshold plus coarse/fine improvement criterion is a useful finite cross-check. Two resolutions show a bounded refinement observation; they do not establish an asymptotic order theorem or certify the reference globally. The maximum-error ratio combines numerically represented component errors; individual component errors still need publication in their respective units.
- The small-error branch correctly reports ratio inconclusive instead of treating roundoff-dominated cases as convergence evidence. Predeclared tolerances must not be enlarged to obtain acceptance. All recorded errors, states and comparisons must first pass finiteness checks.
- Transition evaluation is correctly left-state → right-target rebase at zero age → subsequent advance. Global target time and local residual age are separate. Rational splitting at both transitions prevents a partition accidentally evaluating a different event schedule. The steady zero-residual control does not imply zero deviation during transitions.
- C1 is the selected contract; the first-switch acceleration jump is an intentional counterexample to C2. The crossing case does not confuse one residual-position zero with complete settlement. The half-life example tests a parameter convention, not source approximation equivalence or a finite-time completion promise.
- Comparison with a direct closed form in the partition test is acceptable because the separate ODE reference tests that closed form; partition agreement alone would not establish correctness. This remains an original scalar mathematical witness, not animation-engine, quaternion, joint/contact or visual validation.

## Implementation wording/guards to retain

Clarify accepted endpoint tests as explicitly chosen input tuples whose OUTPUTS remain in bounds, not every Cartesian combination of endpoint arguments. For example, an allowed rate/coordinate extreme may cause velocity outside the accepted output box; rejecting that result is consistent with the protocol. Exercise each numerical domain endpoint without claiming all endpoint combinations succeed. Negative zero dt is accepted as zero; bit-sign preservation is not implied.

Finite output checking includes derived error metrics and negative-control values, not only public API returns. Use explicit failures rather than relying solely on assertions for acceptance, or reject optimized mode as stated. Guard tests should cover each API's role-specific coordinate/velocity bounds; valid-input output-overflow rejection is not the same test as rejecting an invalid input. Pure functions returning a pair can meet the no-partial-state-update rule without inventing a transactional mutable-state model.

No other material protocol blocker was found. Final acceptance should bind the revised exact protocol hash, before implementation or any observed numerical outputs.

## Final exact revision acceptance — 2026-11-01 02:07 UTC

Read the complete two-hunk diff against preserved `history/protocol-before-review.md`: (1) both interrupted value/velocity jumps are now required; (2) endpoint tests explicitly use isolated valid-output tuples. No other protocol changes. Final protocol SHA256 `b39a921ebd231066e3d31ea2e52b3193212255210a63feb94c9ef1c016784c27` is **accepted** for the bounded implementation and finite numerical checks described above. The conditional blocker is closed. No code or numerical execution was performed by this review; subsequent implementation/reference correctness still requires review.
