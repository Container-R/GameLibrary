# Pre-native code review corrections

2026-11-01. Initial exact eight-source manifest and pure outputs remain under historical-pre-native-review/. No CMM native attempt occurred with initial or corrected code.

Independent synthetic receipts reproduced false acceptance of timeout/drain-incomplete metadata and a non-hex Python digest. Corrected consumer requires the exact successful process field set, rejects cleanup/timeout contradictions, validates hexadecimal digest syntax and compares parsed UTC datetime values rather than lexical strings. These checks are archive consistency, not an asserted20-second wall-clock duration theorem.

Initial setup hashes moved inside the runner's guarded attempt. If later source/library/Python hashes become unreadable, failure recording marks unavailable_after explicitly instead of allowing the hash exception to hide the terminal FAIL receipt. A pure missing-source setup test mocks Popen as forbidden, confirms no target launch and checks actual terminal FAIL + unavailable source_after. This does not guarantee receipt writes under filesystem permission/full-disk failure.

Seven test methods normal/-O pass. Each suite has two guarded Python startup negatives; there are no target CMM children or library calls. The exact initial suite remains historical; do not combine repeated development checks into new color scenarios.

Child RESULT_JSON status PASS means its finite observation and own cleanup/library checks passed; it is not yet the accepted invocation. Only the parent's final summary after source/library/Python after-hashes and portable consumer validation accepts the whole run. No successful target observation exists yet. Child ctypes code, protocol, mathematical reference and helper are unchanged by these corrections.
