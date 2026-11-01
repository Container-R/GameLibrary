# Input Disable callback note — editorial acceptance

2026-11-01 UTC. **ACCEPT** exact standalone draft `source-note.md`, SHA256 `784a088cf0b652ab898ba23564020cb75437fe08bb6d8b5bef849963cd24050f`.

Read the complete draft against the independently inspected pinned source and the enabled-in-callback addendum. The Value/no-explicit-interaction Started precondition is coherent; it is not presented as HoldInteraction. The bad-path witness expressly assumes the same preview, non-idempotent release, normal returns, and no other lifecycle mutation. Its conclusion is two application release calls, not an observed crash or unavoidable damage.

The corrected pseudocode sets Stopping before Disable. The callback neutralizer explicitly neither releases the preview nor changes ownerState; the shutdown branch returns before ordinary cancellation handling. The outer owner therefore performs the sole preview release on the stated finite normal-return path. Exceptions, asynchronous ownership changes and reactivation remain excluded rather than silently claimed safe. The unused illustrative stopReason records application intent and is not alleged to come from the API.

The enabled caveat follows the pinned source order under the stated no-other-listener-mutation condition. Disposal assertions, deferred listener removal and caught callback exceptions are accurately bounded; none is promoted to a universal safety or completion guarantee. Source excerpts are compact paraphrases with locators, while the application witness and policy are explicitly original and unexecuted.

The note contains no local runtime identity, observed device result or private preparation context. It is independently publishable without editing or re-uploading legacy articles. Links are fixed primary source locators plus the official versioned API documentation; no prospective experiment is represented as complete. No material correction requested; no code, Unity, device or native execution performed for this review.
