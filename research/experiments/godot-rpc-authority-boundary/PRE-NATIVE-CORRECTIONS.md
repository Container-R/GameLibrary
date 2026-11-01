# Pre-native receipt and barrier corrections

2026-11-01. Original nine source files, full SHA manifest and six-method pure outputs are retained in `historical-pre-native-review/`. No native/network attempt occurred with them.

Four inspection findings were corrected before any native authorization:
1. A later failure's cleanup re-observed the version process and overwrote its earlier return timestamp. The first observed return timestamp is now retained.
2. `finish` previously wrote RETURNED even if cleanup had not established process termination. A null observed return code now produces UNRESOLVED plus last-observation time, never a fictional returned time. Overall failure remains FAIL.
3. Final payload semantics were checked before parent STOP, but their equality to preceding raw EVENT lines was checked only afterward. Both complete raw EVENT/final associations are now required before the terminal barrier is created. The final archive consumer still repeats the check.

4. A reviewer synthetic receipt showed non-overlapping server/client lifetime timestamps could pass archive validation. The consumer now rejects that inconsistent recorded chronology; clock metadata is not independent physical-causality evidence.

Only `run.py`, `consumer.py` and `test_pure.py` changed. The added seventh pure method covers unresolved state and first-return-time retention without creating any child. Existing raw-envelope negative checks reject mismatched trace/final data. Seven methods pass in normal and optimized Python; no engine/version/socket/bind or transport test was performed. Source/rationale review is still distinct from execution authorization. See exact diff and `SOURCE-SHA256.json`.
