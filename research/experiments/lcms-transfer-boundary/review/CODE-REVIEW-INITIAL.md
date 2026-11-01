# Initial pre-native LittleCMS code review

2026-11-01 00:52 UTC. Native execution is not accepted yet. Exact eight sources copied to `initial-code/` before probes; author source unchanged by reviewer. Initial child b736a244, runner b4f09ee5, checker73fbaccd, tests7ae5e2ef. See full copied/source hashes for exact identities.

Five author unittest methods passed normal and optimized Python in the copy. Each suite includes two guarded startup subprocesses, so four synthetic Python startups total and zero target CMM children, CDLL loads, profile constructors, transforms or CMM version calls. Raw suite outputs preserved separately.

## Source checks supported

Explicit ctypes signatures match the independently reviewed pinned header: pointer constructors, C int version/close, uint32 formats/counts, void operations and retained nonthrowing callback. Fixed layout guards precede CDLL. Selected absolute file/hash and relevant mapping checks remain narrowly scoped, not authenticated upstream provenance. Shared gamma is tracked once, transforms before profiles, callback alive until handler restoration. Applicable cleanup continues after a cleanup exception. Native output arrays start NaN; exact array readback, measured decoded→host multiplication→reverse input linkage and normalized reference comparisons are present. Decode failure prevents reverse work; first reverse reference failure prevents opaque conversion. No observed runtime result exists.

## Concrete archive false accepts

`probe_initial.py` constructs a fully synthetic valid archive with independent raw ENTER/RETURN records and literal reference payload. It imports only the stdlib checker and pure test-data helper. The valid control accepts. Each isolated mutation below also incorrectly accepts:

1. process.timeout=true;
2. process.drain_incomplete=true;
3. equal Python before/after digest strings consisting of64 nonhex z characters.

Output preserved in `probe-initial.txt`. Require successful receipt to reject timeout/unresolved/cleanup contradictions and require digest syntax. This is protocol consistency, not execution authenticity.

## Additional failure-recording / chronology concerns

Runner computes initial source/library/Python hashes outside its try block. Its failure handler computes after-hashes without per-read protection. An unavailable file can therefore prevent a terminal failure receipt or replace an original exception with a second exception. Record setup failure and unavailable after-identities explicitly; never upgrade such a receipt to success.

Consumer parses timestamp UTC offsets but compares original strings. Compare parsed aware UTC datetimes instead. Parent independently flagged this as well. Timing claims must distinguish the communicate timeout from process-start overhead rather than assert all elapsed time is bounded exactly20 seconds.

Child RESULT payload PASS occurs after its native cleanup/library-after but before the parent verifies source-after. Overall invocation acceptance must remain the parent source/pin/consumer-gated summary; prose should not equate the preliminary child payload with accepted archived run.

Preserve this initial snapshot and pure failures before correcting source. A revised freeze and independent pure probes are required before any native authorization.
