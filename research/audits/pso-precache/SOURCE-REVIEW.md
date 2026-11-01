# PSO precaching coverage — independent source review

2026-11-01 UTC. **ACCEPT the bounded source-only gate.** No material correction required; retain the configuration and observation distinctions below.

## Original directly read

[Epic PSO Precaching, selected Unreal Engine 5.6](https://dev.epicgames.com/documentation/en-us/unreal-engine/pso-precaching-for-unreal-engine?application_version=5.6). Returned title identifies 5.6; no immutable commit, patch identity or publication date established. Read the full returned text, not images or engine implementation. Did not retry or bypass the author's unavailable standalone API page.

Locators: Configure (12–18); Component / Proxy Creation Delay Strategy (43–70); Loading screen (71–75); Memory (79–84); Validation (117–133); FMeshPassProcessor (227–239); Debug (265–275).

Source checks: resource collection can lack component-specific state. Proxy strategy 0/1 requires `r.PSOPrecache.ProxyCreationWhenPSOReady=1`; do not invent strategy value 2 for blocking. The broader component section separately describes proceeding with a blocking draw. Shader-only and minimal statistics require `r.PSOPrecache.Validation.TrackMinimalPSOs`; full adds render-target information. Shipping classification can merge Untracked into Missed. Outstanding compile count, driver-cache retrieval cost and the default 20 ms hitch threshold are separate observations, not first-display acceptance guarantees.

## Acceptance of original scenario

The proposed new pass/render-target combination remains explicitly unknown: it is neither asserted missing nor asserted to hitch. A historical zero count and shader-only success do not establish coverage of that combination's complete state or its first-use cost. This is a logical evidence-scope distinction, not a claim about counter atomicity or a discovered engine failure.

Keep skip/default-material/block choices as different product outcomes, subject to component support. Recording the collector-to-draw-state association supplies a useful engineering handoff beyond generic readiness advice. Do not promote a classification alone to a root-cause diagnosis, translate absent default-threshold events into a passed frame budget, or imply any one configuration is universally preferable.

For a public note, keep source-derived recap compact and the unexecuted acceptance questions visibly original. No engine, compilation, driver cache operation, rendering, image analysis, benchmark or native invocation was performed. No installed or private environment metadata is needed.
