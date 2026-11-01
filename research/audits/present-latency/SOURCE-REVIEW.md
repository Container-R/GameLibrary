# Independent source review: presentation policy and upstream work

2026-11-01 UTC. **ACCEPT for source-only drafting**, with the scheduling clarification below. Reviewed gate SHA256 `8399fd1732d6e7d03520c3e207f21cc650e1d9ca33afee69d1adcf66b34bd48c`. No executable model, device or runtime inspection, experiments, or delegation.

## Original sources independently reopened

The GitHub tag API resolves `v1.3.296` through annotated tag `7353f6ced118815d61852a739b9eae6f0055d77a` (2024-09-26) to commit `486e4b289053a7d64784e7ce791711843c60c235`. Both exact files below were fetched through the GitHub connector after the web raw-file requests returned cache misses.

- [Surface WSI, lines 1545–1563](https://github.com/KhronosGroup/Vulkan-Docs/blob/486e4b289053a7d64784e7ce791711843c60c235/chapters/VK_KHR_surface/wsi.adoc#L1545-L1563): supports the MAILBOX pending-request replacement and FIFO ordering distinction, and mandatory FIFO support. Replacement applies to that presentation queue; it does not specify cancellation of earlier application or rendering work.
- [Swapchain WSI, lines 267–270](https://github.com/KhronosGroup/Vulkan-Docs/blob/486e4b289053a7d64784e7ce791711843c60c235/chapters/VK_KHR_swapchain/wsi.adoc#L267-L270), [1065–1091](https://github.com/KhronosGroup/Vulkan-Docs/blob/486e4b289053a7d64784e7ce791711843c60c235/chapters/VK_KHR_swapchain/wsi.adoc#L1065-L1091), [1368–1389](https://github.com/KhronosGroup/Vulkan-Docs/blob/486e4b289053a7d64784e7ce791711843c60c235/chapters/VK_KHR_swapchain/wsi.adoc#L1368-L1389): supports minimum image count, acquisition-return versus synchronization distinction, and separation of queued operations from presentation-engine image processing. Actual presentation timing remains platform-dependent. No image-count-to-latency formula follows.
- [Microsoft: Reduce latency with DXGI 1.3 swap chains](https://learn.microsoft.com/en-us/windows/uwp/gaming/reduce-latency-with-dxgi-1-3-swap-chains), last updated 2022-10-20: independently read the motivation and Steps 1–4, including wait → events → update → render → present. The article supports a specific waitable-swapchain technique and a parallelism tradeoff, not a Vulkan mapping or physical latency guarantee. The body was accessible despite the page's generic authorization banner; no login or bypass used.

## Hypothetical timeline and receiving boundary

The arithmetic is consistent: ready at 6 or 22, then the stipulated opportunities at 16 or 32, yields sampled-state ages of 16 or 32 milliseconds. With only one new request, MAILBOX replacement is intentionally not exercised. The example is a non-uniqueness counterexample to deriving latency from the setting, not a benchmark comparing presentation modes.

For the eventual prose, make the existing occupancy assumption explicit: **run B assumes the selected frame cannot overlap or bypass the earlier work, so its GPU work begins at 18**. “Unrelated work” alone would not imply serialization across independent queues or engines. Likewise, readiness at 6/22 does not itself guarantee eligibility for the next display opportunity; the gate already states the additional synchronization/platform assumption and must retain it.

No material source correction is needed. Preserve the distinctions between allocated storage, admission/work-in-flight, pending presentation requests and physical display observation. Do not convert the DXGI sample into universal simulation/input-loop advice, claim MAILBOX can never accompany other latency controls, or treat software timestamps as photon measurements. The narrowly original contribution is locating the intervention and correlating the sampled state, not recommending a universal mode or smaller buffer count.
