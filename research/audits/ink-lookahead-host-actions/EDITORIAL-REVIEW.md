# Editorial review: ink lookahead and narrative host actions

2026-11-01. Accepted unchanged as an additive source-backed mechanism in the existing narrative role.

## Exact reviewed content

- `roles/narrative/narrative-designer-writer.md`: SHA-256 `a90c5a22b4ad41dfd46e3f21b196292b705ddc0b2b645ccc14307e23d9c31e67`.
- `research/source-notes/narrative-designer-writer-role.md`: SHA-256 `5e97e7a2d086ea71625632575cc747ea12dbb30b4f9c72e99bfa6b85d065ef02`.

Compared the complete role diff with its preceding revision and read the dated source addition and local source/main reviews. Original studio attributions and semantic-handoff context are preserved. The new example is not attributed to those studios. No staged text was changed.

## Independent fixed-source check

Directly reopened [Story.cs at 35c63e52f1d36060930dc7ed3cfba38ea224b528](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs): ContinueSingleStep 590–660, snapshot routines 788–825, external call/binding 1943–2061, and the selected zero-argument convenience overloads 2104–2150. Tag resolution is separately recorded in the source review; this pass inspected the pinned content rather than resolving the tag again.

The unsafe string-evaluation rejection and newline-snapshot early return both precede the delegate invocation. The text does not reverse that order into an already-executed effect followed by rejection. General's true default and the inspected convenience overloads' false defaults remain distinct. Source restoration handles ink state, not an automatic compensation mechanism for independent host effects.

## Editorial and receiving-contract checks

The bridge reward example explicitly assumes execution during lookahead followed by restoration. Its unfinished-line observation is a hypothetical author's insufficient evidence, not a measured rendering deadline or guarantee that reward execution occurs at a particular display stage. The adjacent sentences deny a fixed call count and actual script execution; no correction is needed to preserve this scope.

The actionable responsibility is binding policy plus execution placement. Moving evaluation before text generation is explicitly not proof of waiting for player selection. A selected-branch path is proposed when selection must trigger an effect; it is not presented as a verified UI-to-reward transaction. Explicit false is not upgraded to exactly-once behavior across branch re-entry, saves or retries. The read-only-function warning also preserves the need for acceptable early/repeated evaluation rather than a simplistic no-write rule.

The role stays engine-agnostic overall, with this subsection limited to the fixed C# implementation. The note excludes unreviewed implementations and retains historical source scope. Source recap is compact, with no reproduced story content or code listing. No private execution identifiers or host-specific runtime metadata occur in the changed prose.

No compiler, narrative runtime, player interaction, reward system, model test or linked runtime/private evidence was inspected or executed. Acceptance covers these exact texts and the documented lookahead boundary, not a tested narrative commit protocol. No correction requested.

## Final source-note clarification

The source-note phrase “没有取得内部模板、源代码” was narrowed to “没有取得上述工作室的内部模板、源代码” so the historical studio-material limitation cannot be confused with the newly read public ink source. Reversing only that phrase reproduces the initially reviewed note hash exactly. No source claim or example changed.

Final accepted source-note SHA-256: `2372bc4ebdfcf2b2927f56f43e2316f3f9fc959d37a620159682ba1f952b1233`. The accepted article remains `a90c5a22b4ad41dfd46e3f21b196292b705ddc0b2b645ccc14307e23d9c31e67`. Initial reviewed identities above are retained as review history.
