# Server allocation gate: measurement age is not future headroom

Discovery only, 2026-10-31. No runtime, toy benchmark, cloud access or main/remote edits. Proposed future artifact: a narrow NET case study, not a universal placement algorithm guide.

## Primary-source identity and actual reading

Tomasz Mozolewski, Riot Games, [Improving Performance by Streamlining League’s Server Selection](https://www.riotgames.com/en/news/tech-blog-cpu-usage), **2025-01-16**, English; accessed 2026-10-31. First-party historical report, not current-service documentation or independently reproduced results. Body self-identifies the author and Robin Maddock as League tech leads. No substantive first-party implementation link was needed to clarify the selected boundary; no source code or underlying dataset inspected.

Exact sections read: The Old and the New (text-view 23–28); The Goals (29–49); Building a Simulation (50–52); Game Cost (73–75); Game Duration (76–78); Game Starts (96–98); Auto Scaling (115–127); Solution Criteria (130–162); Results (163–211); Scoring (212–246); Live Results (251–261); Learnings (262–287). Text-view line numbers are retrieval locators, not stable source-code anchors. Appendix graphic and scoring-formula images were not inspected; do not reconstruct formulas or graph values from captions.

## Compact source-derived factual recap

Considered selectors included LeastCPU, LeastGameCount, RoundRobin, Random, and randomized low-load subsets. Per-minute game CPU and arrival observations fed regional/day simulations. Assumptions included uniform hardware within a scenario and an eligibility CPU cap; variants included refresh intervals, orchestrator count, machine size and startup time. New machines required startup; retiring machines drained ongoing games.

The reported LeastCPU counterexample combines 30-second observation refresh with low initial match CPU that rises later: placements bunch on a newly cheap-looking machine, and correlated game ages produce later load peaks. This is a reported simulation result, not a new experiment here. RoundRobin was selected for robustness and maintenance simplicity, not because it won every scenario. The live comparison reports lower variability and changing the autoscaling target from 40% to 50%; it attributes hardware savings to that rollout. These are historical author claims, not portable thresholds or a controlled causal experiment. Learnings explicitly notes limitations from varying game durations and changing fleet membership.

## What is known versus unresolved

- Algorithm names describe selectors, not complete executable specifications. Tie-breaking, pending-placement reservations, telemetry timestamps, concurrency serialization, failure handling and eligibility-list update details are **not established by the inspected prose**. Do not invent them from the orchestrator description.
- Distinguish data collection granularity from allocator refresh cadence: the source's per-minute workload collection and the reported 30-second selector refresh are different concepts. Neither is our recommended sampling interval.
- “Uniform hardware” is a stated simplifying condition; varying machine size across scenarios does not prove a heterogeneous-capacity fleet implementation. Preserve that distinction instead of resolving it by assumption.
- Live-shard comparison is described, but exact rollout dates, cohort selection, confounder control, raw observations, confidence intervals and reproducible scoring implementation are not available in the inspected text. Do not turn its cost claim into a guaranteed result or scientific randomized comparison.
- RoundRobin's selector not using CPU does not remove the wider system's need for eligible-host state, capacity governance or autoscaling. Selection and admission are separate responsibilities in our proposed analysis; this is not a claim that the original implementation omitted either.

## Original narrow engineering question

**Before assigning the next match, can the allocation owner distinguish the age of the last load observation from work admitted since that observation, and can the workload owner explain how newly admitted matches grow after placement?**

The useful counterexample is not simply “CPU is a bad metric.” It is that a currently low reported load can coexist with a concentrated cohort of young matches that has not yet expressed its later demand. Fresh telemetry alone does not necessarily remove that second problem. Conversely, this source does not prove a game-count selector handles arbitrary modes, machine capacities or admission constraints.

## Proposed original measurement/placement handoff — unexecuted

A bounded next case can contribute this worksheet without copying Riot's graphs or fabricating a benchmark:

| Producer → consumer | Evidence to hand over | Decision it can support, not guarantee |
|---|---|---|
| Gameplay performance → fleet team | Per-match demand by elapsed match age and mode, source build/configuration, observed variability and unknown coverage | Whether a just-started match is a credible proxy for its future demand; identify which modes lack evidence |
| Telemetry → allocator | Measurement timestamp, collection window, ingestion/availability timestamp, missing/stale status and unit/aggregation meaning | Whether a selector is comparing contemporaneous observations; not whether future demand fits |
| Allocation → monitoring | Decision time, eligible-host snapshot, selected host, selector version, requests assigned since last observation and outcome | Reconstruct a placement burst without assuming CPU immediately reflected each admitted match |
| Fleet lifecycle → allocator | Ready/draining membership changes and evidence that an instance can receive a new match | Distinguish requested capacity from usable capacity; avoid counting a draining host as freely reusable |
| QA/operations → release owner | Workload cohorts and scenario boundaries, per-host exceedance observations, functional failures and unresolved differences between replay and live service | Choose a scoped trial and stop criteria rather than promote the best average score automatically |

These are **our proposed fields**, not disclosed Riot internal schema. Pending assignments might require a reservation mechanism in a real system, but this gate neither prescribes one nor claims the article implemented it. No request IDs, production traces or player data are invented.

A future authorized evaluation should predeclare policy candidates and constraints, preserve the same workload evidence while varying observation age and lifecycle conditions, then distinguish simulation outputs from actual controlled live observations. It should inspect per-host/time behavior rather than fleet averages alone. Such a protocol needs actual project data and deployment authority; a made-up simulator cannot authenticate the reported result. No experiment is proposed in this discovery pass.

## Added value over current knowledge and recommendation

- The new online-services role asks which service-chain steps and substitutes a load test exercised. This case asks a different question: **whether an allocation decision uses timely measurements and an adequate model of work already admitted**.
- Destiny's configuration-admission case concerns incompatible runtime configuration and recovery. This case concerns time-varying demand and measurement/decision feedback, not configuration rollback.
- The client-prediction article handles simulation authority and replay, not host placement. Existing local SQLite results do not validate distributed allocator behavior.

Recommend one source-backed case focused on delayed-load observation and young-match cohorts, with a compact attributed historical recap plus the original handoff above. Do not add another role profile, broad cloud tutorial, toy calculator or numeric benchmark. Main acceptance is required before drafting the public case. Unknowns remain explicit; no claim that this source proves a universally superior allocator.
