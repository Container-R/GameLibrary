# Factorio derived-cache case source receipt

Accessed2026-10-31. Source-only primary developer accounts; no game/runtime/source execution. Intended companion to [case-studies/engine/factorio-derived-cache-load-equivalence.md](https://github.com/Container-R/GameLibrary/blob/cc99dab476ab93db828afed227eb88b93574fcde/case-studies/engine/factorio-derived-cache-load-equivalence.md). 当前读者正文：[Factorio缓存失效与读档后的重算](../../GameLibrary/引擎与工具/运行时系统/缓存与存档/Factorio缓存失效与读档后的重算.md)。

| Source | Authorship/date verified on page | Exact section/location | Claim boundary |
|---|---|---|---|
| https://www.factorio.com/blog/post/fff-340 | Klonan,2020-03-27 | Unit group max speed; paragraphs after screenshot, extracted lines51–59 | Unsaved group-speed cache/load recomputation; previously stable dependency assumption changed; feature removal was diagnostic; notification/recalculation reported as remedy. No claim cache serialization was the remedy. |
| https://www.factorio.com/blog/post/fff-415 | Rseding,2024-06-14 | Deterministic multithreading is hard; extracted lines25–39 | Core-count-sensitive reproduction described; future2.0 remedy mentioned without algorithm. Not a verified shipping/status claim. |

Locations are reader aids, not permanent line anchors on HTML. Link directly to the original pages and use the exact section names. Original screenshots were not inspected and no diagram interpretation is claimed. The companion article omits the separate cyclic-reference case; it does not retell all of FFF340. Source-derived recaps are deliberately compact; acceptance tables and policy tradeoffs are original proposals, not extracted official QA procedures or performed tests.

S1 does not establish private field names, exact serialization schema, issue/patch number, checksum algorithm, complete mutation inventory for modern versions or present-day API behavior. S2 does not disclose the implementation of the fix; no inferred stable-sort/barrier solution should be attached to it. These are two different incidents, not independent witnesses verifying one another.

Existing NET article and network-reconciliation-depth-gate/source-note.md were read before selection. New value is the first-party cache/load-equivalence production failure and a clearly original stage-by-stage acceptance worksheet; no new toy simulation would authenticate Factorio behavior.
