# Offline amix initial pre-native code review

2026-11-01 03:31 UTC. Native execution held pending narrow failure-evidence correction.

Reviewed six-source manifest SHA256 `82a94e31b6f96bf4d1a4ff00f6193106e33e1e003211c88105d9dc61da89f812`, preserved unchanged with all six files in `code-review-copy/`. Read runner, signals, consumer and tests. Independent literal oracle remains `a904ecc7a41cbc9338f0b1ee8f48ecc046835a0792d67815e3bff9c039c36f2b`.

## Material pre-native finding

The outer failure handler writes FAIL but does not record source/tool after-state. Also a nonzero-return or timeout branch skips output hex archival, since that occurs after the successful-return gate. Partial `.f32le` files remain locally, but a text-only archive would lose those bytes. This does not affect a demonstrated native outcome (none exists), but falls short of the frozen failure-preservation contract. Add best-effort failure finalization: preserve primary error, independently record available after hashes or explicit unavailability, and archive already-existing partial outputs without waveform acceptance or any new tool invocation. Initial sources must remain preserved.

## Other reviewed boundaries

Finite commands, minimal selected environment, before-source/input/tool pins, stop-on-first-failure, exact full literal bytes and typed archive/summary association are present. Consumer rejects additional successful-process fields such as timeout/cleanup flags. UTC comparisons parse dates instead of comparing strings; no exact wall-duration assertion is inferred from process-creation metadata. Group cleanup remains bounded attempts, not universal cleanup. Protocol/source pins are consistency evidence, not binary/source authenticity.

Independent exact-copy pure suites passed normal and optimized: six methods each, four guarded Python startup children total, zero FFmpeg/native/version calls. Raw outputs and exit codes are beside this review. Passing these tests did not cover the newly identified failure-finalization requirement.

An independently authored stdlib literal/archive checker is being frozen against the final accepted manifest; it imports no author modules. Its expected byte oracle predates implementation. No execution result is claimed.
