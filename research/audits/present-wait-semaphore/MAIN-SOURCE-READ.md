# Main source inspection: present-wait semaphore reuse

Read 2026-11-01. The main integrator read the full pinned [Khronos Vulkan Guide chapter](https://github.com/KhronosGroup/Vulkan-Guide/blob/82887e8444045655cc4578827e4183be9de593ff/chapters/swapchain_semaphore_reuse.adoc). GitHub returned blob `5095b0045018083433571a5e7aae7177295c9fb9`; commit metadata independently confirmed snapshot `82887e8444045655cc4578827e4183be9de593ff` dated 2026-10-23. That date identifies the snapshot, not the chapter's last modification or a release.

The pinned [Vulkan 1.3.296 acquire paragraph](https://github.com/KhronosGroup/Vulkan-Docs/blob/486e4b289053a7d64784e7ce791711843c60c235/chapters/VK_KHR_swapchain/wsi.adoc#L1065-L1091) was also directly read through the connector after a raw-web cache miss. File blob `e73bec4543923acd871374df08fffa77103eed89`. No access restriction was bypassed. The raw web extraction reflows the Guide, so use named sections and pinned repository lines rather than mixing the two line-number systems.

Accepted scope: normal ongoing acquire/submit/present cycle, explicit acquired-image identity and corresponding acquire synchronization. The new resource-index example is an original unexecuted reasoning device; it is not a measured driver failure. The prior latency timeline and its assumptions remain separate.

Rejected scope: a complete compilable rendering loop, error recovery, swapchain recreation/destruction, queue-family ownership handling, extension implementation, all-resource index conversion, or an observed latency improvement. Reading the chapter's extension section does not authorize those broader claims. No GPU, model, validation layer or existing runtime archive was executed or inspected.

A completed synchronization dependency is not evidence that a particular image became visible to the user. Neither a chosen array index alone nor a CPU function return replaces the required synchronization relation. The public article should retain these distinctions rather than copying the source's abbreviated pseudocode into a production recipe.
