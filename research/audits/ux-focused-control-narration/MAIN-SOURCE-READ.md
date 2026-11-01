# Main source read — focused control narration

2026-11-01. Directly opened Microsoft [Xbox Accessibility Guideline 106: Screen narration](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/106), marked updated 2026-03-04. Read When should narration occur and How should an item be narrated (106–205 in the returned text), implementation control semantics and unchanged-description example (224–249), cancellation/repetition and focus interruption (316–318), context/state changes and programmatic properties (331–354). These are mutable guideline sections, not an SDK implementation or certification result.

The decisive rule distinguishes current focused-item narration from an uninterruptible queue of prior focus descriptions: moving focus should stop unfinished old-item narration and begin the newly focused item. Control name, role, value/state and needed interaction context supply meaning beyond a label. This does not authorize dropping every warning or dialogue, and the unchanged-description example is not a universal value-only rule.

Read the complete existing UX role article. Its settings confirmation/cancellation example supplies a useful unexecuted contrast: visual and input focus can be correct while narration still describes the prior actionable item. Proposed observation must bind spoken context to the actual control, not equate enqueue/submit success with audible completion. No latency threshold, user success rate or sound trace is invented.

Only the guideline text was inspected. No embedded video, screenshot pixels, screen reader, TTS device, UI runtime, player study or linked raw experiment was examined or executed. Adjacent focus or sound studies do not become evidence for this new setting-flow claim.
