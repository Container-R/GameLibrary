# Initial pre-native code review — correction required

2026-10-31 23:44 UTC. Exact eight-source snapshot retained in `initial-code/`, with `INITIAL-SHA256SUMS`. Reviewed GDScript, runner, literal oracle, portable consumer and pure tests. Four author pure methods pass independently under normal Python and `-O`; output preserved separately. No engine, version process or native invocation.

## Findings

1. The callback owner oracle only constrains owner to the allowed identity set. `probe_initial.py` demonstrates a parent-disable exit still claiming Opener owner, and a viewport acquisition claiming null owner, both accepted. Pinned source's clear-before-exit/set-before-gain supports checking null owner on exits and target owner on enters/gains. This does not require callback eligibility to match the final post-setter state; that remains diagnostic-only.
2. Embedded `Engine.get_version_info()` is ignored. An arbitrary version object passes. Bind a declared minimal set of actual self-report fields to the separately captured version/protocol, without treating it as authenticated source identity. Keep synthetic controls explicitly synthetic, not evidence of a native run.
3. JSON duplicate keys are rejected, but NaN is accepted; default float parsing can also overflow to infinity. Reject nonstandard constants/nonfinite parsed numbers rather than permit ambiguous ignored metadata. This is a bounded evidence-format check, not a general engine metadata validator.
4. Coordinator independently identified that the whole GDScript sequence proceeds even if baseline or intermediate post-call state is unexpected; the only substantive oracle is after all mutations. Add small post-call failure gates that emit a partial failure trace and stop before subsequent mutations. Preserve the existing frozen successful sequence and diagnostic callback treatment.

## Other reviewed boundaries

Direct Control ancestry and actual parent/viewport/subtree fields are recorded. IDs use exact nonzero integers and allow negative values. Signal callbacks are passive. Setter-only override row requires Default owner. The final observation is a deferred callback, not a rendered-frame assertion. Consumer binds protocol/helper, source before/after, binary before/after, exact argv/environment path association, process return/status/time and raw-to-parsed data. Current normal timeout cleanup is bounded own-group SIGKILL/wait attempts, not guaranteed containment or normal-exit descendant census. Runtime source identity remains unauthenticated.

Corrections require a new frozen source manifest and pure review before execution. The demonstrated accepted mutations are synthetic checker counterexamples, not engine failures.
