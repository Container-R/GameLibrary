# Scalar spring-residual transition continuity

This is an original bounded numerical model, not an engine integration. The implementation uses a standard exponential, analytic target derivatives and explicit event times. Its accepted claim is finite scalar value/velocity continuity, including an interrupted transition. No skeleton, foot contact, root motion, arbitrary derivative estimator, animation quality, performance or platform claim follows.

- [Frozen protocol](protocol.md): inputs, units, exact event order, prospective tolerances and intentional counterexamples.
- [Fixture and invocation](fixture/README.md), [author numeric results](fixture/RESULTS.md).
- [Independent protocol acceptance](review/PROTOCOL-REVIEW.md) and [code/numerical review](review/CODE-NUMERICAL-REVIEW.md).
- [Independent reference](review/reference/README.md): separately written before inspecting author code/results, with retained two-resolution data.

Author and independent copy each ran normal and optimized Python: four executions of the same eight-method suite, not 32 distinct scenarios. Each has 139 guard subcases inside one method. The reviewer also ran one independent ODE reference and one static comparison reader. Main read exact code and reran the reader in normal and optimized modes against all four archives, without another model execution. Raw commands, status, tables and hashes are retained separately.

The reference uses the same classical RK4 method, independently implemented; this is not an alternative-method-family replication. Both components are compared at 35 fixed case/time pairs plus the explicitly split transitions. Finite agreement/refinement is not a global error theorem. Negative-control discontinuities and transient growth/crossing are expected witnesses, not suppressed failures.

## Read the archived comparison without executing the model

From this experiment directory:

```sh
python review/reference/compare.py fixture/results/normal.json fixture/results/optimized.json review/repeat/fixture/normal.json review/repeat/fixture/optimized.json
```

This reader is scoped to these known archives, not hardened untrusted-input ingestion or execution authentication. For a new model run, use a disposable copy preserving `protocol.md` beside `fixture/`, and a fresh output filename. Check the actual process status and current output together; an old JSON does not validate a failed new invocation. Do not overwrite historical outputs.

## Publication and provenance

Original source-code hashes and protocol are unchanged from the observed runs. The first protocol draft is retained in `history/` to show two pre-execution review refinements; no tolerance was changed after numerical results. Extended web discovery/source paraphrases remain local; no third-party source code, slides, figures, datasets or demo assets are redistributed.

Historical reference SHA256SUMS uses the original local-relative path recorded before execution; it is a source-freeze receipt, not a relocated archive command. Current archive bindings are in `archive-bindings.json`. Hash equality supports consistency, not authentic historical execution. Raw paths and platform strings describe the finite execution environment and do not establish current availability.

Publication wording refinement: the general C1 explanation requires piecewise-C1 targets with finite one-sided value/derivative limits; mere differentiability is not sufficient. The analytic ramp/sine segments already satisfy this stronger statement. Frozen protocol/code/result bytes and numerical criteria were not changed; this is not a newly run experiment. Acceleration comparisons assume the corresponding one-sided second derivatives exist.
