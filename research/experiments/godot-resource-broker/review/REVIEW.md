# Independent same-path request broker review

2026-10-31. Accepted for this finite sequence and installed binary. Frozen contract f70e399b8aac89c6323ae29b78ebef281f0bf393f8fbe3fe727d700e216d1e50 read before copied execution. No author/main/remote edits.

Executed from workspace (all exit 0):
- python3 -B research-drafts/deep-qa/godot-resource-broker/fixture/run.py
- python3 research-drafts/deep-qa/godot-resource-broker/check.py
- python3 research-drafts/deep-qa/godot-resource-broker/fixture/check_freshness.py

Two actual fresh engine processes. Independent check.py imports no author code: literal modes1/3 and3/1, raw call sequence, exact integer identities, red/white colors, offsets0/1, source/binary hashes and unchanged controlled disk inputs. First polling observation LOADED in both; second request returns OK, status3, get1, status3, get2, status0. Results remain readable and R1==R2; firstREUSE aliases active, firstDEEP differs from active. Active descriptors unchanged. Invocation and summary IDs match current successful process receipts. Raw outputs and independent checker output retained alongside fixture/results.

Unlike prior candidate fixture's declared count fields, this fixture increments request/get counters at actual call sites and emits CALL_JSON immediately after each invocation. Inspected source confirms second request follows first LOADED without a prior get; both gets guarded by the required statuses; finished prevents later callback repetition. No third get or actual concurrent caller tested. Status0 after collection does not invalidate held resources; actual final descriptors support that narrow distinction.

Independently fetched official pinned core/io/resource_loader.cpp at35e80b3a8822a9df9be390814b62f44c0a9c69e8 via GitHub plugin. Sections516–538/568–625 show user-token lookup by requested path and early reuse with increment before new task mode assignment;791–801 show user_rc decrement and path registry removal at zero. These match the limited interpretation, not an independently authenticated mapping to installed binary. Immutable link: https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource_loader.cpp#L516-L625 . Previously independently read Godot4.6 ResourceLoader threaded methods in the immediately preceding candidate review; no documented independent-mode guarantee inferred.

Reexecuted author's two bounded freshness probes in copied directory: -O/missing engine reject, clear seeded PASS, write FAILED invocation with zero spawn attempts. No extra engine executions. Timeout and filesystem interruption not fault-injected; these tests are not universal receipt atomicity. Raw status counters correctly distinguish attempts from actual successful child executions.

README original broker recommendations remain explicitly unimplemented, not guaranteed solutions: merely keying an application map by(path,mode) cannot override the observed underlying same-path registration. Same exact path, same type hint, no mutations/worker race/timing/GPU/cancellation/performance or arbitrary load graph claim. Same binary SHA f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3; selfreported7d41… remains distinct from public35e80… comparison. Exact source hashes in independent summary; no material blocker found.
