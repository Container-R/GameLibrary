# Independent fresh-invocation wrapper review

2026-10-31. Accepted bounded Linux integrity/freshness protocol, not execution authentication. Copied harness ab74e41ecf123c6a5ae1b60728d55ca06a4feb7f367d4f0bfcfdfab0257a5eb0, registry and tests unchanged into tool/. Original six fixture trees were hashed before/after real calls:306 files/full set unchanged; hashes rechecked after synthetic tests too. No main/remote edits.

## Actual calls and accounting

`python3 repeat.py` executed six registered legacy runners with child-O: all exit1/REJECTED, no old summary copied, zero Godot runs on these early paths. One normal focus invocation ACCEPTED and expected-UUID consumer exited0. Pinned focus source has version/help plus gate/naive/guarded, hence five source-audited Godot calls, three behavior cases. This is not independent syscall instrumentation and not six normal-positive reruns. Independent check_raw.py checked exact artifact hashes and raw focus ownership/identity outcomes: gate keeps close focus, naive transfers to replacement record, guarded transfers to safe owner, same path/different object identity preserved.

Copied15-test suite executed normal and-O, each15 methods passed; explicit unittest/require enforcement remains active. Environment overrides point to reviewer's new accepted invocation and distinct synthetic-normal/synthetic-O output dirs. Each suite executes three synthetic child processes plus one copiedfocus-O sentinel-origin rejection (no engine). Thus test repeats add six synthetic process calls and two extra copiedfocus-O rejects, not new normal Godot evidence. Synthetic timeout retains PARTIAL and rejects; exit7+PASS and exit0/no-summary reject at relevant gates.

Additional descendant_probe.py launches one synthetic leader which spawns one sleeping child in its inherited group, then exits0. Wrapper detects unexpected descendants and rejects. Actual receipt has group_remaining=true after bounded TERM/KILL attempts: **do not claim clean reaping or verified group disappearance for this probe**. This conservative unresolved-group state is a successful rejection-path observation, not successful cleanup. No Godot/native engine executed by this probe. Raw process/rejection/stdout/stderr retained.

## Architecture checks

Consumer binds caller's expected UUID, terminal ACCEPTED, integer exit0/no timeout/no unresolved or unexpected group, current trusted harness/registry hashes, exact copied source pins, required raw/parsed/summary artifacts and contained regular-file hashes. Focus adapter tolerates its legacy missing top-level status while requiring three known cases/checks/exits and raw/parsed equality. Only focus normal adapter is enabled; five others are reject-only. Explicit optimized-child gate cannot be bypassed by hypothetical successful child exit.

Input allowlist does not copy original results/history/caches; synthetic historical-PASS origin remains unchanged. Source files/output components are symlink-checked and resolved containment enforced; root aliases are canonicalized. This is point-in-time path consistency, not hostile concurrent filesystem defense. Receipt can be forged by a writer capable of coherently rewriting trusted files; no signature/actual execution authenticity inferred. Producer and consumer deliberately do not duplicate all legacy scientific oracles; this reviewer separately checked focus semantics.

Process launch creates own session and signals only that group, with bounded TERM/KILL and rejection if termination remains unresolved. Current implementation cannot guarantee all descendants/OS states are reaped, especially when leader has already exited; escaped sessions/uninterruptible I/O and hostile behavior are outside scope. Parent termination before final receipt leaves nonaccepted state, not durable transaction proof.

## Archive and reproducibility

repeat.py records actual invocation UUID directories, raw invocation stdout/stderr, expected consume result and original hash manifest. Current positive.json directory refers to local reviewer evidence; portable test replays must use FRESH_POSITIVE_INVOCATION with that UUID-named evidence copy and FRESH_TEST_OUTPUT with a new directory. Keep only receipt-listed outputs, copied allowlisted source files and receipt for portable evidence; generated HOME/XDG/TMPDIR caches are not necessary public evidence. Preserve original absolute metadata as historical, not current paths.

No material acceptance blocker found. Evidence supports six isolated early-rejection paths and one real focus normal path, not repaired legacy runners, validated normal adapters for the other five, universal cancellation or upgraded historical binary provenance.

## Owned-descendant state diagnostic

At parent request, ran one additional isolated descendant_state.py synthetic leader/child pair, no engine. Unlike initial probe, it logs actual child PID and reads that PID's /proc entry inside the same command namespace immediately after wrapper return. Wrapper again recorded unresolved group and rejected; subsequent owned-child observation was **gone**, no additional signals sent. Observation JSON preserves both facts: group probe time and child inspection time differ. Do not reinterpret initial probe as proven cleaned; its child PID was not recorded and later exec uses another PID namespace, so its final state remains unestablished. No arbitrary numeric PID/group was targeted across namespaces. Current diagnostic child cannot continue writes once gone; this is not general descendant cleanup proof. Total added descendant diagnostics are two synthetic leader/child pairs, separate from unit-suite counts.

Final author README6f63160ef11722bff559814bb10f3994c85fe074082c3a586a5437f05b98e448 read: natural-language polish and explicit nonguaranteed descendant reaping accepted. Harness ab74e41e… and registry bb063ecaf012b00cf16338fe21f043313624a8bf8d57931cd26c26376ace0aee unchanged. No source/result rerun for editorial change.
