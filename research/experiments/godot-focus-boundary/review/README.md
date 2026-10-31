# Independent review: Godot focus identity boundary

Reviewed and independently executed 2026-10-31. Frozen source copied from `research-drafts/godot-focus-boundary/` into `fixture/`; original files and outputs were not modified.

## Verdict

**PASS, no material blocker for the stated narrow claim.** Three actual Godot processes (capability gate, naive, guarded) each exited 0 and met the runner's assertions. Four source SHA256 values and the engine binary SHA256 match the original manifest. See `fixture/results/summary.json`, raw `.log`/`.json`, `runner-output.txt`, and additional `review-checks.json`. Optimized Python is rejected before tests; independent rejection saved in `optimized-rejection.txt`.

Additional independent inspection/assertions established:

- Initial Opener and Close receive actual focus signals; queried Viewport owner matches their IDs. Capability gate does not merely assume headless focus works.
- Old node is removed before new same-path node is ready; restore starts later through actual `call_deferred`, not a Python list or direct invocation disguised as engine work.
- Both strategies retain request_revision==revision==1. The observed guard is instance identity, not stale-version rejection.
- Old/new/SafeReturn/Close IDs are distinct within each strategy process. Runtime IDs are not compared across processes or represented as persistent identifiers.
- Naive owner is replacement Opener at return, deferred observation, and subsequent process; guarded owner is SafeReturn, and replacement never receives focus_entered.
- Logical modal is an ordinary Control container. README and supplement correctly exclude native Window behavior, full modal input isolation, visual accessibility, hardware navigation, Unity, and same-instance business rebinding.

The business-A versus business-B distinction is an explicit fixture/product contract assigned in original source, not an engine guarantee. Same-path replacement is not universally an error: products allowing business-key rebinding require another policy. This fixture demonstrates the stated preserve-original-identity contract only.

`call_deferred` may finish in the same idle cycle. The artifact correctly claims deferred execution ordering, not one full frame of delay, network latency, or concurrency coverage. No extra FPS matrix or unrelated cases were added.

## Primary reference cross-check

Official Godot4.6 docs accessed2026-10-31:

- [Object.call_deferred](https://docs.godotengine.org/en/4.6/classes/class_object.html#class-object-method-call-deferred): idle execution; nested deferred calls may run in the same idle cycle. Supports the bounded sequencing interpretation.
- [Viewport.gui_get_focus_owner](https://docs.godotengine.org/en/4.6/classes/class_viewport.html#class-viewport-method-gui-get-focus-owner): returns actual currently focused Control or null. Supports distinguishing actual owner from requested target.

Independent execution used `4.6.3.stable.official.7d41c59c4`, matching author version and binary digest. The runner records rather than pins arbitrary future binaries; this review attests only the captured binary and source hashes.
