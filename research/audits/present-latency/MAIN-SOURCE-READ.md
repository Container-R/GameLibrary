# Main source read and scope

2026-11-01 UTC. Main integrator directly read the pinned Vulkan surface WSI lines 1535–1585 and swapchain WSI lines 255–278, 1065–1095 and 1355–1400 at commit `486e4b289053a7d64784e7ce791711843c60c235`. The selected clauses support the gate's presentation-request policy, minimum-image-count and acquisition-return/synchronization distinctions. In particular, returning from acquisition is not permission to access image data before the selected semaphore or fence signals.

The Microsoft DXGI 1.3 guide's body and sample loop were read directly: wait precedes event processing, update and rendering in that specific sample. The guide's parallelism tradeoff does not establish a Vulkan setting, an application-wide simulation ordering mandate or a physical-display latency guarantee. The page body was accessible despite a generic authorization banner; no login or bypass was used.

The independent source review is accepted. Its required clarification is substantive: earlier unrelated GPU work does not by itself serialize execution across engines/queues. The hypothetical run B must explicitly assume that the selected rendering cannot overlap or bypass that work. Readiness alone also does not establish next-display eligibility; that remains a separate stipulated condition.

No device query, execution, renderer inspection, measurement or model test was performed. The new timeline is an unexecuted counterexample to a setting uniquely determining sampled-state age, not a present-mode benchmark or a diagnosis of an observed machine.
