# Independent ink save/content source analysis review

2026-10-31 19:00 UTC. Reviewed source-analysis.md initial SHA256 c72298335193a2942ee91ef45105b13ba9f22c59b171f41aac6e10439300dd49 and gate.md. No ink runtime/compiler execution, no synthetic substitute. Capability gate is author's bounded environment probe, not independently exhaustive machine inventory.

## Independently fetched pinned source

GitHub plugin read exact commit `35c63e52f1d36060930dc7ed3cfba38ea224b528`, base https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/ . Files/line ranges independently inspected:
- StoryState.cs25–26,56–60,654–794,1332–1339: save minimum8/current10; parse→LoadJsonObj→callback; flow mutation before all fields complete; no upper-version check at inspected gate; serialized format number is not content hash. Absence claim limited to inspected methods.
- Flow.cs18–28,79–89; CallStack.cs53–102,230–243: stack/choice-thread recovery and approximate warning branch; missing resolved object exception. Single-flow load contains two Flow constructions but no runtime callback/warning counts inferred.
- Container.cs229–274 and SearchResult.cs10–16: partial traversal preserves last reached object, flags approximate; container cast differs from correctObj. Not semantic narrative matching.
- Story.cs740–780: ContentAtPath delegation and separate PointerAtPath conditions; root-only fallback can error for nonempty traversed path, unlike blindly substituting thread condition.
- Story.cs2826–2857 plus2874–2895: Error throws; Warning passes through AddError formatting then appends diagnostics and does not ForceEnd. Formatting may itself encounter failing state; no unconditional warning-delivery guarantee.
- Story.cs416–470,533–580,90: external-binding/canContinue prerequisites, caught StoryException handling; later dispatch to onError then reset, or throw if handler absent even for warnings. Callback throw can prevent reset. Public currentWarnings exposes buffered list.
- Story.cs210–229: compiled format upper/lower compatibility is distinct from save structure and project content identity.

No material mismatch in the source table or source-only limitations. Normal load return, exact path, absence of warnings and author-approved continuation are correctly distinguished. No guarantee that deleting a particular knot triggers approximation, nor that a preserved path preserves meaning. Candidate instance reduces publication risk but not arbitrary host side effects.

## Narrow protocol clarification requested

onDidLoadState occurs before LoadJson returns. A host handler can itself Continue/ResetErrors or replace state, so copying warnings only after return does not inherently preserve the original load diagnostics. Author should explicitly restrict candidate handlers to non-mutating logging during inspection, or snapshot at callback entry before arbitrary host action; preserve caught exception phase. Existing prose already acknowledges callback arbitrariness, making this a narrow condition rather than a contradiction in source analysis.

No main/original source/remote edits by reviewer. Only this review artifact written. Original content-author acceptance protocol remains proposed/unexecuted; no observed next text/choices, warning counts, migration outcomes or runtime compatibility.

19:00 UTC final clarification read and accepted. Final inspected source-analysis SHA256 `270a09c1982605fe85c9e3a6b0a9ed1ca398aaac256cdedff406a19c9fc91ab7`: candidate handlers are explicitly log-only, no Continue/save/ResetErrors/state mutation or external side effects; required host actions snapshot diagnostics inside callback first. No remaining material issue in declared source-only scope.
