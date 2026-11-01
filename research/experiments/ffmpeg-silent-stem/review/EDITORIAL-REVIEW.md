# Independent editorial review: silent-stem normalization

2026-11-01 UTC. ACCEPT the two exact drafts below, without substantive correction. This review reads source reasoning previously checked independently, final code/native review records and prose; it performs no new native call, pure test or archive-checker execution.

- `research-drafts/audio-mix-depth-gate/article-draft.md`: SHA256 `916206042e42c146f33b0c8e37d7de607c364287b930513cad44f7aa7edfd3c2`.
- `research-drafts/audio-mix-depth-gate/source-note-draft.md`: SHA256 `4ed6cc3791dc24f3cdf53226ad48ca2fc84e9440a8bee2549b4903e4cd036053`.

## Evidence applicability

Read `NATIVE-REVIEW.md` and `CODE-ACCEPTANCE.md` in this directory. The article correctly reports two invocations of the same three mixing configurations: six mixes and two version queries, not six unique cases. Each 4096-frame/16384-byte output was fully compared, including the exact half-open sample2048 transition, against the pre-code literal oracle. The output table matches the recorded full-waveform result and does not infer internal AVFrame instrumentation from output bytes. Pure suites and independent synthetic mutations are separately classified; pre-native failure-finalization/UTC corrections are not described as native failures.

The EOF/internal FIFO mechanism and active-input normalization explanation agree with the pinned original source read during protocol review. Silent samples are not equated with inactive input. The zero-dropout arithmetic caveat remains qualified; the actual observation is not generalized to all float implementations. Installed self-report and two selected file hashes are explicitly not complete dependency or release/source authentication.

## Engineering and claim boundaries

The proposed stem-preview/export handoff is original engineering reasoning, not an allegation about a studio's pipeline or measured workflow benefit. Input participation, duration, weight and gain policy are useful separate delivery fields. Normalize is correctly distinguished from loudness measurement and subjective quality. The normalize-off control is not a universal repair: headroom/limiting/output-format policy remains outside this finite test. No middleware, playback device, latency, listening, resampling, arbitrary EOF arrangement or platform-wide bit identity is claimed.

Proposed `SOL-SFX-002` has no collision in the inspected current `gamelibrary-work/solutions` files. Relative links are consistent with the proposed audio solution/source-note locations; the new experiment/source-note links depend on the integrator copying the selected archive.

## Separate publication dependency (not a correction to these drafts)

The current fixture `research-drafts/ffmpeg-silent-stem/README.md` still opens with “awaiting native authorization” and an unqualified claim that no FFmpeg invocation has occurred. This was accurate at pre-native freeze but is stale as a current public overview. Before publishing, preserve or label it as historical pre-native documentation, and provide a current overview linking both accepted receipts and native review. Do not modify pinned runtime sources or erase the chronology. The two reviewed drafts already report the current results accurately.
