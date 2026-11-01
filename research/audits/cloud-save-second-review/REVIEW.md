# Cloud-save second review — useful negative within the declared domain

2026-11-01. Read-only review of current published article, original model and actual filesystem experiment under gamelibrary-work. Exact file hashes are in reviewed-source-sha256.json. No archive/main file changed; no new filesystem experiment, native engine, installation, network call or Steam operation executed.

## Result

**No new material in-domain correctness defect or unsupported result claim found in this bounded pass.** Do not create a patch or new fixture merely to increase findings. The highest-risk old issue—an unnotified same-revision changed payload bypassing dispatch—is already fixed with comparison against the loaded Save object, and its exact negative test asserts rejection without coordinator mutation. The separate actual path experiment correctly demonstrates why that serial model guard is not filesystem CAS.

This is not exhaustive verification or proof of arbitrary malformed-input safety. It specifically assesses the existing trusted internal, integer-valued, serialized model and the recorded two arranged path-publication traces.

## Model inspection and actual pure checks

Copied exactly test_cloud_resume.py and test_inflight_counterexample.py into model-copy. Executed their existing suites only: 20 transition/protection tests pass, plus the separate1-test in-flight-write counterexample passes. Two Python processes, no actual file replacement/cloud I/O. Raw stdout/stderr are retained.

Read through queue/dispatch/reload transitions and the previous adversarial audit:

- Dispatch rejects stale epoch/base, different full loaded baseline, changed queued value and closed mode; a successful dispatch increments epoch and makes other same-baseline jobs stale.
- Same-current-revision reload preserves dirty in-memory value rather than pretending it was saved. Direct-parent clean fast-forward and dirty/unknown-lineage conflicts remain distinct.
- Locally reserved/observed identities cannot be issued again; incoming known noncurrent identity is recovery-only. The256-entry set fails closed instead of forgetting history. It is not a global identity or complete lineage validator, as already stated.
- Missing/deleted candidates and newer disk views do not trigger default-save publication. Conflict choice/account switching/in-flight cancellation are explicitly outside implementation, not fabricated passing behavior.

A tempting but invalid “new finding” would feed bool/float values into trusted internal Save/edit/job inputs and exploit Python numeric equality. The existing README already restricts values to integers and constructor/jobs to trusted objects; the original published audit already identifies runtime-type preconditions. Such an out-of-domain example would not establish a newly discovered defect under the current contract. A future real decoder should enforce exact types and integrity before entering this model, but that is not tested here and is not a new fix request.

## Actual filesystem source and receipt review

Read experiment.py, author results and final independent repeated source/results, not only the README. check_archives.py performs read-only checks of the five archive manifest entries; final source identity; both archived two-trace arrays; expected10345-byte A/B encodings and hashes; recorded completion/publication flags; empty stderr and declared sequence. It imports no experiment code and makes no replacement call. Actual output is archive-check.stdout; zero new filesystem executions.

The sequencing is supported by inspected Event/pipe code, not inferred from the hard-coded barrier_order list alone: child signals old baseline checked; parent publishes and reads B, invalidates then releases; child publishes/skips, returns, parent joins and reads final bytes. Final code guards optimized Python and executes waits outside assert. Historical pre-fix review remains clearly labeled; final source hash is a0a3263830ed9f280e8217cb3c7e3228c58406bf864017d3a4ad5c45ab82cbf5.

Potential overclaims checked and NOT found:

- Recheck control is explicitly arranged and not a universal repair; another writer could intervene after the check.
- Delayed old work is before os.replace entry, not cancelled in-kernel I/O.
- Blocking filesystem operations may exceed coordination timeouts; README does not promise globally bounded termination.
- No continuous-reader, fsync, power-loss, CAS or real Steam result is claimed. tmpfs and lack of syscall tracing are explicit.
- Original20 protection tests,1 in-memory counterexample and2 actual filesystem trajectories remain separate counts; independent repetition is not extra scenario coverage.

## Recommendation and stop

Retain current evidence and scope. If the project later chooses an actionable extension, it should introduce a real decoder or a separately specified cooperative commit protocol—not claim this model's equality check itself supplies production CAS. That would need its own authorization/protocol and is not proposed as a required repair here.

This review stops after the requested bounded source/receipt inspection and existing pure suites. No speculative concurrency fuzzer, new runtime trace or artificial malformed-input “bug” was added. Static hashes/results support consistency, not authentication of historical execution.
