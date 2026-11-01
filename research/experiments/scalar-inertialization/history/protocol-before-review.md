# Frozen numerical protocol — scalar spring-residual transitions

2026-11-01 UTC. Proposed original implementation/experiment, **not executed**. Source gate: `gate.md`. No native engine, animation assets or source-code downloads. Freeze this protocol before implementation; retain failed results and explain any later protocol revision separately.

## 1. Mathematical contract and finite domain

Scalar coordinate units are arbitrary length units L; time seconds s, velocity L/s, rate lambda s^-1. This is a mathematical signal experiment, not a physical character.

API candidates:
- `decay(r,u,lambda,dt)` evolves a zero-goal residual.
- `rebase(output,output_velocity,new_target,new_target_velocity)` computes the new residual from actual output.
- `compose(target,target_velocity,residual,residual_velocity)` adds independently sampled target state and residual at the same time.

Every argument must be an exact built-in Python `int` or `float` (reject bool, string, None, complex and custom numeric objects), convertible to finite binary64. Conversion failure/overflow is rejected explicitly. Reject NaN and infinities before computation. Limits: absolute coordinate <=100 L, absolute velocity <=100 L/s; `0.125 <= lambda <=16`; `0 <= dt <=8`. Reject out-of-domain parameters, not clamp. A rebase/compose result or evolved state outside coordinate/velocity bounds is rejected explicitly before returning; callers must not partially mutate state on rejection. Domain is intentionally conservative and does not claim all in-bound inputs have in-bound outputs. Fixed accepted cases below stay inside it. Negative times and zero/negative rate rejected; dt=0 accepted unchanged. Internal elapsed times in this experiment stay <=8 s.

Use the standard `math.exp(-lambda*dt)`, not the source's `fast_negexp` approximation. No epsilon snapping, automatic velocity clamp, convergence-to-zero threshold, or changing-rate shortcut. No public half-life API in the first implementation.

Let B = u0 + lambda r0. Exact residual:

    r(s) = (r0 + B s) exp(-lambda s)
    u(s) = (u0 - lambda B s) exp(-lambda s)
    a(s) = -2 lambda u(s) - lambda² r(s)

This satisfies r(0)=r0, u(0)=u0 and r'=u. Differentiation gives u'=a, hence the stated ODE. At a switch, set r0=z_before-p_new and u0=w_before-p'_new. Then z_after=p_new+r0=z_before and w_after=p'_new+u0=w_before. This is C1 when each input segment has the supplied derivative. **C2 is not promised:** new output acceleration is p''_new-2 lambda u0-lambda²r0, which generally differs from the previous acceleration.

As s→infinity both residual components tend to zero for lambda>0. This is asymptotic; finite completion is not promised. Outside this bounded witness, floating-point underflow may nevertheless produce exact zeros; that numerical event is not a mathematical finite-completion guarantee. Settlement concerns BOTH residual position and velocity, not the first zero of position. Initial growth or zero crossing is possible. Critical damping does not make every initial-value trajectory monotone.

## 2. Frozen residual cases and sample times

| Case | r0 | u0 | lambda | Purpose |
|---|---:|---:|---:|---|
| Z | 0 | 0 | 2 | Zero residual identity |
| P | 1 | 0 | 2 | Nontrivial decay and half-life distinction |
| V | 0 | 1 | 2 | Initial velocity without position offset |
| G | 1 | 2 | 2 | Initial movement away from zero |
| X | 1 | -4 | 2 | Crossing at s=0.5, then approach from opposite side |
| N | -0.75 | 1.25 | 0.5 | Signs and slower rate |
| F | 0.25 | -0.5 | 8 | Faster rate |

Sample times exactly 0, 1/8, 1/2, 1, 2 seconds. Additional long sample s=8 for finite-output/decay report only, not RK4 convergence ratio. Report values, errors and domain acceptance, not just test counts. All cases are original inputs, not measured animation data.

## 3. Independent RK4 reference and predeclared tolerances

Reference integrates two states using ONLY derivative `dr/dt=u`, `du/dt=-2 lambda u-lambda²r`; do not call the closed-form implementation, exponential or its helper inside this reference. Use classical RK4, fixed h=1/128 s and h/2=1/256 s; sample times align exactly with both grids. Initial states are the table above. Compute fine/coarse trajectories independently from the original initial state, not by resampling a shared run.

For each state component at each sample <=2 s, absolute difference between closed form and fine RK4 must be <=1e-7 in that component's units. Preserve the coarse and fine errors in a raw numeric table. To avoid demanding order ratios in roundoff-dominated/zero cases, define E as the maximum absolute error across BOTH components and all positive samples for each nonzero case. Require E_fine<=E_coarse/8 whenever E_coarse>=1e-10. For smaller E_coarse require E_fine<=1e-10 and mark ratio inconclusive/roundoff-small, not evidence of fourth-order convergence. Z must remain exactly zero in both references.

These tolerances are proposed engineering acceptance criteria, not pre-observed results. If either condition fails, retain errors and diagnose reference, formula or tolerance assumptions; do not silently loosen them. Independent review should inspect the RK4 stages and nonshared implementation before trusting agreement.

Initial identities and `dt=0` use exact equality where arithmetic permits. Nonzero floating-point comparisons outside the RK4 test use `abs(actual-expected)<=1e-11 + 1e-11*abs(expected)`. This is a finite numerical tolerance, not an animation acceptance threshold. Analytic C1 proof is separate from a floating-point check; finite differences across a discontinuity are not the velocity oracle.

## 4. Changing targets and exact transition schedule

All targets use GLOBAL time t, so rebase and composition cannot confuse local clip time with residual age:

- Segment A, 0<=t<0.75: pA(t)=0.4t, pA'=0.4, pA''=0.
- Segment B, 0.75<=t<1.125: pB(t)=1+0.5 sin(2t), pB'=cos(2t), pB''=-2 sin(2t).
- Segment C, 1.125<=t<=2: pC(t)=-0.25+0.2t, pC'=0.2, pC''=0.

Start with zero residual and lambda=2. At each switch, evaluate old output and derivative exactly at the boundary from the LEFT segment and its existing residual; rebase against the RIGHT segment at that same global time. Compose at zero new residual age BEFORE advancing time. Record both sides' values/velocities/accelerations. C1 differences must meet the specified tolerance. At the first switch, verify the acceleration difference is nonzero by >0.01 L/s²; this is a labeled counterexample to a C2 guarantee, not a failure of the selected C1 contract.

Separate no-transition control: zero residual with sine target p(t)=sin(t), p'=cos(t), t=0,1/8,1/2,1,2. Composition must match the input exactly. This only shows no persistent filtering of a clean input when residual is zero; it does not prove no lag/deviation during transitions or under perpetual switching.

## 5. Discriminating negative controls

1. At first A→B switch, rebase position correctly but set new residual velocity to zero. Position remains continuous; velocity jump must exceed0.01 L/s. Label this deliberately incomplete initializer.
2. At B→C switch, rebase from B's raw target value/velocity, omitting the remaining first-transition residual. Require a value OR velocity discontinuity >0.01 in its units. Report both. Do not mistake raw source state for actual output.
3. For G, report r(1/8)>r0; for X, report |r(1/2)|<=1e-11 and r(1)<0. These demonstrate allowed transient behavior, not algorithm defects or a universal overshoot bound.
4. Convention h=0.5 s implies lambda=2 ln(2)/h in Holden's ideal mapping. With r0=1,u0=0, r(h)=(1+2 ln2)/4, not1/2. Require discrepancy >0.05 and report it. No claim that h is a measured completion duration; no source epsilon denominator reproduced.

No negative control is reported as a production failure or hidden inside passing safety counts. Separate “contract checks” and “expected counterexamples.”

## 6. Constant-rate partition and event handling

For each residual case compare direct evolution to elapsed2 s against iterative partitions: 60 intervals of1/30,120 of1/60,288 of1/144, and repeated irregular [1/128,3/128,4/128] until2 s. Compare BOTH residual components with the tolerance above. Form schedules with exact rational bookkeeping, convert individual intervals only at API boundary; record actual floating sums separately. The direct analytic answer at the exact elapsed time is the oracle, not a chosen reference schedule.

For the three-segment target, repeat output sampling with the same30/60/144 schedules but **insert/split intervals at0.75 and1.125 exactly**. Evaluate the analytic target at the interval's END when composing its advanced residual. Final output and velocity must match direct segment evaluation at2 s. This is a deterministic mathematical event schedule, not device input timing, engine scheduler behavior or platform determinism.

Changing lambda mid-step is excluded. Changing rates only at explicit boundaries would require its own contract; do not infer it from the constant-rate semigroup check.

## 7. Guards, records and stopping condition

Table-driven rejection cases: bool, string, None, complex; NaN/+inf/-inf; huge integer conversion overflow; coordinate101, velocity101; lambda0, negative, below0.125, above16; dt negative and above8. Include accepted exact endpoints and negative zero dt as zero. Include valid arguments whose rebase/compose result exceeds output bounds and require complete rejection/no partial mutation. Reject Python optimized mode if using assert-based harness.

Archive exact source URLs/locators (not source-file copies), interpreter version, commands, hashes, configuration, raw per-case errors, convergence table and negative-control values. Do not infer performance, joint limits, foot contact, quaternion behavior, asset correctness or engine compatibility. No source assets/code copied and no benchmark. The bounded unit is complete only when the frozen contract is implemented, independent reference/error tables and intended counterexamples are reviewed, and all failures are explained rather than suppressed. At this protocol stage **none of these checks has run**.
