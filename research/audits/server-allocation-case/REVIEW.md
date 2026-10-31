# Independent source/argument review — CASE-NET-001

2026-10-31. Frozen draft, source note and discovery gate independently read; input hashes in `input-hashes.json`. Primary Riot article independently reopened and read. No main-tree edits, service calls, toy simulation, workload generation or benchmark executed.

## Verdict

**Accept as source-backed historical case plus original unexecuted handoff analysis. No material revision required.** Acceptance is not independent reproduction of Riot's simulation or live results.

## Source checks

Primary: [Tomasz Mozolewski, Improving Performance by Streamlining League’s Server Selection](https://www.riotgames.com/en/news/tech-blog-cpu-usage), dated2025-01-16; accessed2026-10-31.

- *Building a Simulation* describes per-minute source workload observations. *Results* separately describes30-second decision-input refresh in the reported LeastCPU behavior. Draft correctly separates those cadences, neither prescribing them nor silently equating them.
- *Game Cost* and *Results* support the distinction between delayed observations and low early-match demand that rises later. Draft attributes the reported behavior, then explicitly labels its two-time-interval framework as original analysis.
- *Solution Criteria* includes placement eligibility and uniform-hardware simplification. Hardware-size scenario variation does not establish a mixed-capacity fleet implementation; draft retains this limit.
- *Scoring*, *Live Results* and *Learnings* support historical strategy selection and bounded deployment claims. Draft does not claim universal RoundRobin superiority, replicate scoring weights, derive image values or assert controlled causal proof.

The official date and author match. Formula/weight/appendix graphics were not independently inspected in this review; the parent's reported cache-miss attempts do not confer knowledge of their contents. No argument here depends on them.

## Selection versus eligibility

The case's distinction is coherent: choosing within an eligible set is not the same as building that set. A selector's lack of CPU ranking does not imply the whole system lacks telemetry, capacity constraints or lifecycle checks. Conversely, an eligibility threshold does not prove that multiple placements between observations preserve a hard invariant. The draft does not invent Riot reservation, locking, tie-breaking or multi-orchestrator coordination details.

This is a proposed responsibility interface, not a recovered production algorithm. In particular, recording post-observation assignments helps make a question auditable but does not itself solve concurrency, cancellation or stale-state correctness; the article explicitly leaves those mechanisms unresolved.

## Original five-party handoff and acceptance questions

The gameplay-performance, telemetry, allocator, machine-lifecycle and QA/operations rows are clearly marked unexecuted. They name observable inputs/outputs and omitted claims, rather than present private studio schemas as known facts. Their division between measurement age, workload age and capacity readiness adds engineering value beyond an algorithm roundup.

Proposed comparisons separate latency changes from young-match concentration, require real permitted workload evidence, and keep simulation and deployment conclusions distinct. They neither fabricate distributions nor prefill numerical thresholds or savings. Fleet averages versus per-machine/time behavior are treated as complementary observations, not substituted for a new benchmark score.

## Boundaries accepted

Historical live comparison does not establish current service behavior or remove confounders. Uniform scenario assumptions do not validate heterogeneous capacity. No runtime logs, source implementation, raw dataset or images were inspected; no test PASS is asserted. The new case remains distinct from the online-services role, client prediction and configuration rollback work.

The modest-source recap and original analysis avoid copying diagrams, formulas, code or extensive source text. No cosmetic expansion or additional source padding requested.

## Review locators

Primary article sections: The Goals; Building a Simulation; Game Cost; Auto Scaling; Solution Criteria; Results; Scoring; Live Results; Learnings. Relevant access-time text positions are lines40–52,75,115–170,208–246,251–287; section titles are preferred over unstable reader line numbers.
