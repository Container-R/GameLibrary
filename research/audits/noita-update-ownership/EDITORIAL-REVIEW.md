# Noita simulation note — independent editorial acceptance

2026-11-01 UTC. **ACCEPT unchanged** complete draft SHA256 `99961820461d913b171a4a7c8b8a4ff0101607b36008dc478e4287d04cb3c458` at `research-drafts/noita-simulation-article/source-note.md`.

Read draft, gate and SOURCE-REVIEW. Independently reopened the original 80 Level interview (https://80.lv/articles/noita-a-game-based-on-falling-sand-simulation), checking byline/date, first-person Introduction, Optimization of the Falling Sand Simulation and Distribution text. No pictures, video, engine source or executable were inspected; no runtime/model/concurrency test or author/legacy/remote modification.

## Scope and substance

The article correctly identifies named developer testimony hosted by a publisher, not studio-hosted implementation or independent audit. The original text supports the selected numerical and scheduling references at extraction lines 126–131; the note explicitly attributes the ownership explanation rather than certifying its safety. Historical early-access context and current-version uncertainty are preserved.

The concrete new mechanism is the relation between an allowed access envelope and an update owner's scheduling assumptions, distinct from dirty-region work selection. This is more useful than generic parallelism advice: a future material-rule change is handed to the scheduling maintainer with explicit read/write/auxiliary-state questions. The draft does not invent exact group coordinates, diagonal handling, barriers or a complete scheduler from the stated dimensions/round count. The hypothetical rule is clearly not a reported Noita incident.

## Independent set check

For distinct shared mutable slots x and y, W_A={y} and W_B={x} are disjoint, but R_A={x} intersects W_B and R_B={y} intersects W_A. This proves only the insufficiency of the write-disjointness premise for claiming that every relevant access pair is disjoint. The draft correctly withholds an actual race/outcome claim without overlap, synchronization and memory-model conditions. Separate immutable read storage is correctly identified as a different model, not disguised through reused variable names.

The original handoff table does not claim studio endorsement. The final limits exclude determinism, serial equivalence, performance benefits, visual effects and execution claims. Existing fixed-step results are expressly non-transferable. Source recap remains compact, with no broad interview translation, images or private runtime metadata. No material correction requested; acceptance covers this historical testimony and original set-theoretic boundary only.
