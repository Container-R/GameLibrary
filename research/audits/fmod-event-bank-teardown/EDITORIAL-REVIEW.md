# Editorial review: FMOD event and bank teardown

2026-11-01. Accepted without further correction. This is a source-only review of an additive lifecycle subsection, not a middleware execution or listening result.

## Exact reviewed content

- `solutions/audio/music-state-transition-contract.md` — SHA-256 `0fb9f95ae8070e74c803275dec6b54ca46ab4f0efd297cf680439f54ce4294cb`.
- `research/source-notes/fmod-event-bank-teardown.md` — SHA-256 `42cbdf6cb4a30cf312db01f0937195ec8969370b6451da6cb0d44424464f0080`.

Compared the full article diff with its preceding revision. Changes are limited to verification metadata, the Bank source link, and the new scene-exit subsection. Existing model results, virtualization discussion, lifecycle definition and START_FAILED handling are unchanged; their evidence is not transferred to teardown. The source note is new. No staged content was edited during this review.

## Source and argument checks

Independently reopened the official [EventInstance reference](https://www.fmod.com/docs/2.04/api/studio-api-eventinstance.html) release, callback-type and stop-mode sections; [Bank reference](https://www.fmod.com/docs/2.04/api/studio-api-bank.html) unload and unloadSampleData sections; and [Studio Guide](https://www.fmod.com/docs/2.04/api/studio-guide.html) processing and callback sections. Also read the local source and main-reading reviews. Locator line numbers are reading aids, not immutable document revisions.

The new text keeps event release, bank ownership and sample-loading references separate. Its conclusion concerns missing lifecycle guarantees, not an observed truncation incident. The scene-exit alternatives are explicitly original and unexecuted, with shared-user coordination still required. Resource retention is necessary within the selected policy but not sufficient evidence of complete audible output.

The integrated wording “Studio 更新处理销毁” appropriately avoids making asynchronous initialization universal. Callback dispatch settings, later application processing and handle lifetime remain distinct. Neither notification is promoted into acoustic completion or an asserted notification order. Copying application records does not promise that a released SDK handle remains usable later. START_FAILED remains a separate failure path.

The practical addition is concrete: a scene's logical exit must choose whether to retain required resources for its event-end policy or accept interruption for reclamation. It does not supply a complete bank manager, universal tail protection, synchronous reclaim-time guarantee or user-memory protocol.

## Scope and publication checks

The note distinguishes observed manual metadata from release or installed-build authentication, retains the unsuccessful discovery-page read, and does not fill that gap from inference. Source recaps remain compact; the exit-policy example is distinguished from vendor behavior. No audio, diagrams, source listings or document bulk is reproduced.

The added prose contains no private execution identifiers, host-specific paths or runtime binary identities. No SDK, engine, listening, model or test execution was performed for this review. This acceptance applies only to the exact files and additive scope above, not to all audio content or every possible teardown configuration.
