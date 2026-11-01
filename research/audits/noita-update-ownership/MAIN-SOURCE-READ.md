# Main Noita developer-testimony read

2026-11-01 UTC. Read the full original 80 Level interview body, including the dated header, first-person Petri Purho/Nolla Games introduction, selected Optimization paragraphs and then-future distribution wording. Publication date is 2019-04-05. This is original named developer testimony hosted by an independent publisher, not studio code, a current-service specification or an independent concurrency benchmark.

Selected optimization text distinguishes dirty-region work reduction from cross-chunk update concerns, then describes bounded movement and alternating update rounds. The useful historical mechanism is this separation; the source does not provide complete group coordinates, read sets, barriers, corner behavior, shared auxiliary-state handling or a deterministic execution proof. No image, geometric diagram, animation or video was inspected by main.

The original future-rule scenario must remain hypothetical. Changing an access envelope requires re-establishing the relevant ownership assumptions; it does not by itself prove a real game race. An optional abstract two-slot example can show that disjoint writes do not imply disjoint read/write intersections, but it must identify storage consistently and remain separate from actual scheduling, language memory semantics and observed outcomes. Reading an immutable old buffer is a different access model from reading the same mutable slots.

No game, source implementation, native process, numerical model, performance test or deterministic simulation was run. Existing fixed-step evidence does not transfer to this spatial ownership question. No article images, source body, private runtime data or user context is reproduced.

Source: [original interview](https://80.lv/articles/noita-a-game-based-on-falling-sand-simulation), Introduction and Optimization of the Falling Sand Simulation sections.
