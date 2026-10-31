# Initial implementation review before native invocation

2026-10-31 23:04–23:05 UTC. Main read child4e333192, runnerf4d4a8d7 and consumer21235d8a. No native launch authorized. ABI and fixed one-double call lifecycle match protocol; output length/status is checked before reading finite UTF-16 units, and nonnull handle closes on normal failure paths.

Required bounded corrections: preserve global load/native/terminal chronology instead of merely comparing filtered event subsequences; reject bool-as-int for top-level inputs and attempted input values; require actual bool in intent acceptance (independent reviewer additionally demonstrated False→0 substitution acceptance). Failed batch spawn count must not say zero when an exception after actual spawn prevents run_one returning; reconcile actual per-config receipts or state uncertainty. Initial source/manifest/pure logs are pre-execution history, not failed native attempts.

Author proposed replacing explicit ctypes.memmove with direct Python-built uint16 input array; main agrees to reduce the explicit native surface and avoid confusion over the count of ICU exported calls. These changes do not alter frozen patterns, inputs or expected markers. Final source inspection and independent reject probes must precede native launch.
