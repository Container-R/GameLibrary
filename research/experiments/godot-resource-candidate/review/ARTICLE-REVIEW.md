# Resource ownership supplement editorial review

2026-10-31. Accepted section 5, “运行时补充：候选根不同，不等于可变依赖已隔离”. Reviewed article SHA256 `f2f57a3eab1febe6507e1e4e5dfc9eeff96334ca898b89b3b97353791d9c4282` identifies the entire file, but this pass covers section 5 only. Main files unchanged; no new runtime execution.

Read the accepted independent REVIEW.md, final main.gd control flow and author results/summary.json. The supplement accurately describes the two-case finite GradientTexture1D → external Gradient graph: candidate is never assigned to the active root; ordinary IGNORE yields a distinct root with shared dependency, so candidate mutation reaches the active graph; IGNORE_DEEP isolates the dependency in this graph. It does not promote that observation to universal graph/plugin isolation or thread safety.

Status [3] is correctly treated as first observed LOADED rather than a witnessed in-progress transition, synchronous loading proof or performance guarantee. Main-thread mutation occurs after the guarded get. request_count/get_count literal fields are clearly distinguished from the inspected single call sites and bounded control flow. The text does not assert independently instrumented call counters.

The positive-ID validator failure is reported as an overly strong oracle corrected to exact nonzero/stable integer identity, not an engine error; historical failure is not counted as another successful scenario. Same-process live IDs are not persistent asset identity. Source comparison and unresolved local-binary provenance remain separate. The scope excludes root publication, real concurrent mutation, cancellation, arbitrary graph isolation, GPU sampling and performance; these exclusions match accepted evidence. No material correction requested.

This editorial pass relies on the already accepted primary-source review and integrator's independently checked pinned loader/ObjectID source. It does not claim a fresh full source-code audit or engine repeat.
