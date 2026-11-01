# FMOD virtualization supplement — editorial review

2026-11-01 UTC. **ACCEPT after one API wording correction.** Read the complete added section, baseline diff and source note against the independently read originals and accepted FMOD source review.

## Exact bytes

- Baseline article: `2eb0620deb8f97e95bc5d4ccce31395b0b1f8cf49616bf0279b9467e0431d13b`.
- Draft before correction: `b6a84b6ee229b5e22747ef6707fad84089aac66a342f1cce3952eb915811228c`.
- Accepted article: `895e730afa09d957891c20bab7ad26d7a73faf7b5f8e6b3da5ef72fc94ffa249`.
- Source note unchanged: `e3c7ab31fabf7c8bee06d994f198183f618fbfbe7c270fead545a22226fed5b0`.
- Refreshed baseline-to-final diff: `70a678e35337f7a6dd552f4d81a9b43cda51c72d19a8f7479b36d14700594827`.

The first sentence now says “EventInstance::isVirtual 查询成功且输出状态为 false” rather than “返回 false”. This separates the C/C++ FMOD_RESULT from its output boolean. No other article or source-note wording changed; the diff was regenerated to match final bytes.

## Acceptance scope

The new section correctly distinguishes the event polyphony observation from the underlying Core channels. Successful queries, relevant identity and observation times are required; separately collected states are not promoted to an atomic snapshot. The known-capacity-stealing row explicitly avoids diagnosing theft from an invalid handle alone.

The retained-channel opening/tail example is conditional and unexecuted. Default position continuation does not prove prior delivery; the Core start-from-beginning flag is not represented as restarting a whole Studio event. Neither eventual reactivation nor useful delayed delivery is guaranteed. Real status is not output/perception evidence.

Studio refusal, stopping and virtualization remain separate. Core's stealing shorthand is not generalized across Studio modes. START_FAILED is cross-referenced as an existing branch rather than claimed as a newly tested result. Original model counts, lifecycle meaning and historical Wwise limitations are preserved, and the new metadata explicitly labels source tracing and an unexecuted observation contract.

The source note accurately records the three documentation footers, mutable version-series URLs and absence of runtime verification. Existing critical-sound guidance is complementary; it is not used as a middleware test. No material further correction required. No runtime, listening, experiments, private environment inspection or remote writes performed.
