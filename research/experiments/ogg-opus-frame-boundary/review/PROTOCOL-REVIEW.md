# Independent finite Ogg Opus protocol review

2026-10-31 23:20 UTC. Read candidate `research-drafts/ogg-opus-frame-boundary/protocol.md`, SHA256 `4024d6fda4d3533eeca3e124d79c398cae1ec540d143da7ef18b6fb0ba27db5e`. Source/protocol review only; no media generated, parsed, encoded or decoded, and no native invocation performed.

Accepted for bounded implementation, subject to separate pre-execution code review and coordinator authorization. No material change to the finite oracle requested.

The protocol incorporates the prior source-review conditions: identification packet alone on BOS page, comment packet beginning page1 and finishing its completion page, no shared audio on header-completion page, bounded comment counts/lengths with permitted post-list data, explicit negative-granule handling, and previous completed-audio-page tracking. Nonempty frame payload and last-packet trim bound are correctly labeled narrower fixture restrictions rather than universal format requirements. No unconditional stereo-TOC assumption remains.

The twenty-millisecond configuration set1,5,9,13,15,19,23,27,31 matches the independently read RFC6716 table. Code0 contributes one960-frame packet; no requested encoder option is substituted for actual TOC checks. Exact page offsets/CRC/lacing and initial non-EOS granule equality constrain the count inference before it is used.

The input arithmetic is internally consistent:93,659 frames ×2 channels ×2 bytes =374,636 bytes. Both last-frame modulo remainders are58, giving L1280/R1728; first frame is L-6144/R-3840. The generator formula is original numerical content, not a claim of musical representativeness. Lossy decoded values are not expected to preserve those samples.

The two count counterexamples are distinct and falsifiable: with positive measured pre-skip P, G-N=P; with positive measured tail trim T, (D-P)-N=T. G-P=N and actual decoded byte count/4=N must both hold. Nondecreasing EOS G versus the previous completed-audio granule is acceptable; requiring G strictly greater would unnecessarily exclude an entirely trimmed final page, but the frozen positive-length and trim bounds already constrain this original case. All three calculations depend on the verified zero-offset subset, not arbitrary cropped streams.

Successful author execution is exactly three tool processes: version query, one encode and one decode. No ffprobe media call is hidden in this count. Requested48kHz input/output is not described as auditing every internal rate operation. Protocol requires stopping on first unexpected result or unsupported layout, without repairing bytes, widening parser support or rerunning options to obtain a pass.

Source/tool/library before-after identities, raw process receipts, bounded20-second waits, unique outputs and lossless archive reconstruction are appropriate evidence controls. Implementation review should verify the actual environment/timeout process-cleanup policy rather than infer a sandbox or universal cleanup guarantee from this protocol. Static archive consumption must remain distinct from another native run and must bind the reconstructed original media hashes to the checked receipt.

Neither CRC nor hash consistency authenticates execution or dependency origin. This protocol establishes at most the single count boundary, not audio quality, seamless loops, seek/pre-roll, Unity/FMOD/Wwise or universal gapless playback. The original PCM-only experiment remains immutable. No new source-gate bytes were edited by this review.
