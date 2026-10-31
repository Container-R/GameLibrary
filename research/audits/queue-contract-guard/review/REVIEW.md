# Independent queue-contract guard review

2026-10-31. Accepted within documented additive scope. Copied validate_queue.py/test_queue.py into fixture; original draft/main repository unchanged. Added six independent unittest methods in fixture/adversarial.py. Its imported QueueTests also executes all nine author tests: **15 methods =9 author+6 reviewer**, not15 new tests.

Actual commands from workspace, each exit0:
- python3 -B research-drafts/deep-qa/queue-contract-guard/fixture/adversarial.py
- python3 -O -B research-drafts/deep-qa/queue-contract-guard/fixture/adversarial.py
- python3 -B research-drafts/deep-qa/queue-contract-guard/fixture/validate_queue.py gamelibrary-publish-shader
- python3 -O -B research-drafts/deep-qa/queue-contract-guard/fixture/validate_queue.py gamelibrary-publish-shader

Both test invocations report15 passed. Both real queue checks report49 tasks and0 artifact paths; raw streams retained. **This is discipline/ID validation of current queue, not artifact-existence coverage**, because optional paths are absent. No optional field migration was performed. Original draft's historical RENDER failure and48-task in-memory correction remain unchanged, not confused with this later49-task state.

Added checks cover duplicate/invalid taxonomy identifiers, non-string/blank core task fields, canonical root symlink, permitted in-root symlink, dangling outside symlink even for planned artifact, dangling inside published target, duplicate JSON keys/nonstandard constants, controls/Windows drive-relative/dot/UNC spellings, and permitted published directory. Planned missing path versus published missing is covered by inherited tests; unrelated legacy prose/status remains compatible.

Code uses explicit exceptions rather than assertions, so -O does not remove enforcement. Resolved root establishes containment boundary; path components are checked before normalization, target resolution catches existing/dangling symlink escape, and published existence check applies only to exact status published. Directory artifacts are permitted by design, not evidence that their required children exist. Unknown statuses and missing/empty artifact_paths remain allowed; this is intentionally not complete queue-schema validation. No TOCTOU defense or general hostile-filesystem security claim.

Parser rejects explicit NaN/Infinity and duplicate keys, while README correctly does not promise rejection of every numerical overflow in irrelevant metadata. No generic strict-JSON expansion requested. No material correctness blocker found for the declared recovery-state contract. CLI is read-only and emits current PASS only after validation; external redirection/old reports remain caller-owned evidence concerns.
