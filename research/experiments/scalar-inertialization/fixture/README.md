# Scalar spring-residual continuity fixture

Original Python standard-library model, not an engine implementation. `scalar.py` implements the bounded contract frozen in `../protocol.md` SHA256 `b39a921ebd231066e3d31ea2e52b3193212255210a63feb94c9ef1c016784c27`. The source/math gate and independent protocol review preceded implementation. Author's first normal and optimized-mode runs passed without changing frozen criteria; independent code/reference review accepted these same source bytes and a separately copied repeat. See the archive review records.

From this directory, use a new output path to retain original evidence:

    python test_scalar.py --output review-normal.json
    python -O test_scalar.py --output review-optimized.json

The script returns nonzero on failed unittest checks. Always check this invocation’s exit status and newly written report together; a preexisting JSON is not a receipt for a later failed startup. It uses explicit unittest assertions, which remain active under `-O`. No installation, dependency or native engine is needed. No reference source code or assets were downloaded/copied. Inputs, rates, exact event schedule, prospective tolerances and negative controls are detailed in the protocol; do not widen them after seeing results.

`test_scalar.py` independently integrates the two-state ODE with RK4 without calling the implementation/exp from the RK4 routine. Closed-form agreement alone does not prove global correctness; exact initial identities, moving-target composition, event ordering, two refinements and discriminating intentionally incorrect initializers supply separate checks. Raw arrays are always [position in L, velocity in L/s]. `RESULTS.md` provides the finite summary; JSON preserves component errors, exact source/protocol hashes, interpreter and command arguments. `results/commands.txt`, raw logs and exit codes retain both actual author processes. Guard tests are subcases of one unittest method, not139 additional named tests.

Pure functions return a complete bounded pair or reject; there is no mutable execution state whose transaction safety is being claimed. The output box is not invariant under every allowed input combination. Smooth input derivatives are supplied analytically; no claim covers estimating derivatives across an unknown clip discontinuity.

This verifies scalar C1 transition witnesses, not C2, exact completion time, no overshoot, physical realism, quaternion interpolation, joints, contacts, root motion, engine behavior, visual quality or performance. Residual zero crossings are not settlement of both states; no snap threshold is applied. Floating underflow outside the bounded witnesses is not a finite-duration theorem. Normal and optimized results are two executions of the same8-method suite, not16 distinct coverage scenarios.
