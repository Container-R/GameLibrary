# Presentation latency — independent editorial review

2026-11-01 UTC. **ACCEPT after one precise wording correction.** Both drafts read in full against the accepted source review and independently read pinned Khronos clauses and Microsoft guide.

## Exact bytes and edit

- Original article SHA256: `616ee96dc091a87f6f9a8d6006796c2514ac1f270887b11d9ff711a524509fce`.
- Accepted article SHA256: `fb64436a50de8f68c65bbb2f06855c9348ded4e387fc3cbccb92cd167ad687fe`.
- Source note unchanged: `765543235d95c94e1c01ce980cb751850375e017efeb68bb220f56154d6e097a`.

The only edit replaces “规范也不允许依赖” with “规范提醒不要依赖” before the acquisition-blocking statement. The pinned clause uses SHOULD NOT, not MUST NOT; the new text preserves the recommendation without implying a prohibition. The separate requirement to await the image's synchronization signal remains correctly stronger.

## Acceptance checks

- MAILBOX replacement is confined to pending presentation requests, not cancellation of prior CPU/GPU work or proof of newer sampled input.
- Minimum requested images, actual capacity and work/request occupancy remain distinct. No image-count latency formula or universal lower-is-better policy is asserted.
- Both hypothetical runs retain the same actual image count, an available image, supported mode and one noncompeting new request. Replacement is not exercised. B explicitly assumes serialization rather than inferring it from unrelated work alone.
- Readiness and eligibility for the stipulated next opportunity remain separate assumptions. The 6→16 and 22→32 arithmetic concerns sampled-state age, not measured input-to-photon latency or a mode benchmark.
- Microsoft's waitable-swapchain example stays separately platform-scoped. Ordering and parallelism tradeoffs do not become Vulkan guarantees or permission to reorder authoritative gameplay.
- The diagnostic table is original unexecuted guidance. Compact source facts and pinned locators are appropriate. Neither draft claims rendering, device, timing or player experiments.

No additional correction required. The existing draft-checks record predates this edit and retains the original article hash; it must not represent a final-byte check without refresh. This review independently records accepted final bytes. No runtime, experiment, repository publication or delegation performed.
