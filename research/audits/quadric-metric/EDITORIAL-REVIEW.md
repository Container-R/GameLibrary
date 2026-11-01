# Plane-quadric addition — independent editorial review

2026-11-01 UTC. **Accepted on substance and applicability; one low-severity homogeneous-coordinate notation clarification recommended.** No runtime, mesh generation, numerical experiment, legacy-file edit or remote action. Read the complete amended note, supplied diff, existing published note, source gate and independent source/math review. This is editorial/math review, not another independent retrieval of all primary sources.

## Exact reviewed bytes

- Amended `research-drafts/quadric-metric-article/source-note.md`: `97af137c6cf7027565dfe5994438adc833b82f4c5ccc5b0496c1f247324b1d1d`.
- Existing `research/source-notes/mesh-simplification-request-result.md` in the selected published snapshot: `b49b2a37b4817aa98283a49e0371e71f08c21c684ef92644278d231a2ec299f9`.
- Read-only string/diff inspection confirms the amended file is exactly the old note plus the new section before applicability; supplied `source-note.diff` exactly matches that addition. No older request/result contract was silently rewritten.

## Hand-checked proof

The triangle contains only points with x≤1 and y≥0. For P=(2,0,0), squared distance is (2−x)²+y²≥1, attained at (1,0,0), which belongs to the closed triangle. Therefore distance(P,T)=1 exactly. The plane z=0 has the stated unit-normal homogeneous coefficients; its quadratic expression is z² and vanishes at the lifted P. Positive-weight copies of that same term still vanish there. This is algebraic reasoning, not an executed solver or sampled metric result.

## Scope and evidence transfer

The isolated-term warning precedes the example. The immediately following paragraph explicitly denies that P is an original/candidate/reachable output vertex or that meshoptimizer returned zero error. Default point regularization, eligible border/seam terms, topology admission and error normalization are distinguished from the isolated paper term. The note therefore does not silently substitute that term for the complete v0.25 metric or output.

Point-to-one-triangle distance, two-complete-mesh distance and view-dependent silhouette are separately identified. Extra constraints are not called a Hausdorff guarantee; separate sampled assessment is not called a maximum bound. No visual, performance, runtime or actual asset acceptance claim is introduced.

Source-derived prose stays focused on mechanism and locators rather than translating the paper or reproducing results/figures/code. The explicit calculation is an original explanatory example. No private paths, host metadata, invocation identifiers, library hashes or execution receipts appear in the proposed public note.

## Low-severity notation recommendation

The function is defined for homogeneous v∈R4, but the displayed result says q_plane(P) where P was defined in R3. The intended lift is evident and the proof is correct; this is not a substantive blocker. Prefer define v_P=(2,0,0,1)^T and write q_plane(v_P)=0, or write the homogeneous argument explicitly. Main was notified before any change; reviewer did not edit author files. If applied, record the final exact hash in an addendum, without changing the proof, cases or conclusions.

## Final notation-only acceptance

Main applied the suggested explicit homogeneous lift. Final amended note SHA256 **`edd71b9565b0f5697bd23284c3f4c2fdfcc4ccc132f31e3fb4c64a05712514e5` accepted**. Read the final formula; reversing only the one-line v_P definition/use exactly reproduces the initially reviewed hash `97af137c6cf7027565dfe5994438adc833b82f4c5ccc5b0496c1f247324b1d1d`. No proof, interpretation, source scope or other prose changed. Initial review identity and correction history above remain intact.
