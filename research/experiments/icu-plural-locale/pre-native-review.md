# Pre-native corrections

No native child had run when these corrections were made on 2026-10-31. `historical-pre-native-review/` retains the exact initial six source files, manifest, and six-method pure outputs (normal/-O). They are not failed ICU invocations.

- Independent reviewer and coordinator identified Python bool/int equality accepting malformed record inputs and intent fields. Final consumer requires actual integer inputs and actual boolean intent acceptance.
- Separate load/native trace filtering could accept interleaved load events. Final consumer checks complete four-load, eighteen-native-trace, one-terminal ordering, then validates names/phases and scalar facts.
- Coordinator identified batch spawn-count undercount if `run_one` raised after spawning. Final batch scans child receipts in `finally`; if an invocation is still unresolved or receipts unreadable, numeric total is unknown (`null`), with separately observed receipt count. A missing record is not proof of no process.
- Author replaced explicit ctypes.memmove input copy with direct uint16 array construction to remove an unnecessary explicit native helper from the counted experiment. Counted planned calls are ICU exports: version/open/six formats/close per successful configuration.

Final eight pure methods pass normal and optimized Python, zero child processes and zero native calls. Source-manifest pins identify the current implementation. Protocol and helper remain unchanged. Native execution still requires coordinator approval following final source review.
