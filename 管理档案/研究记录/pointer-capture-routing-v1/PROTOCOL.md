# Pointer capture routing: finite browser protocol v1

Freeze this protocol and all fixture input hashes after pre-execution review and before any browser launch. Original local HTML, no external assets or page navigation. Purpose: observe event recipient and geometric element under the pointer separately, and compare normal implicit capture loss with explicit release while the button remains down. This is not a game inventory implementation, touch cancellation, accessibility or browser conformance suite.

## Inputs and scope

Existing Chromium and Playwright only; no installation or browser download. Launch headless with Chromium sandbox enabled. If unavailable or forbidden, fail and stop, without disabling sandbox or changing host security settings. Browser environment uses an isolated writable HOME, XDG config/cache and temporary directory. Context requests are aborted, and HTML is supplied directly. This is not a claim of operating-system network tracing or zero browser process network traffic.

Viewport 400 by 200 CSS pixels, device scale 1. Two fixed original divs: source rect x20,y20,width100,height100; destination x220,y20,width100,height100. No transforms, scrolling, overlays, native HTML drag-and-drop or asynchronous item changes. A mouse with only its left button is used through Playwright's browser input API; not a physical mouse test. Do not synthesize DOM PointerEvent objects.

Each case uses a fresh page, checks both exact rectangles, moves to (50,60), clears the trace, presses left, then moves in one input step to (250,60). The source pointerdown handler requests capture only for the two capture cases. A document capture-phase listener records pointerdown, pointermove, pointerup, gotpointercapture and lostpointercapture. Each row includes actual target id, coordinates, buttons, button, pointerId, isTrusted and document.elementFromPoint result. The shareable JSON excludes host paths, process identifiers and installed binary fingerprints; raw stderr is private and requires separate review before any publication.

1. control: no capture; release at (250,60).
2. captured-up: capture source; release at (250,60).
3. explicit-release: capture source; after moving to (250,60), invoke source.releasePointerCapture with the recorded active pointer id while held; move to (260,60) to process the pending release, then release.

## Fixed acceptance

Require exact filtered event type/recipient sequence:

- control: down/source, move/destination, up/destination.
- captured-up: down/source, got/source, move/source, up/source, lost/source.
- explicit-release: down/source, got/source, move/source, lost/source, move/destination, up/destination.

Expanded names are pointerdown, pointermove, pointerup, gotpointercapture and lostpointercapture. All rows must have isTrusted=true and one nonnegative integer pointerId within a case. For all pointermove/up rows after the initial down, the geometric hit must be destination; x/y must be the requested point for that step. Require buttons=1 for moves and buttons=0 for up. Each case has exactly one down and one up; down must have target/hit=source and (50,60), buttons=1, button=0. up has button=0. No page errors or recorded capture call errors. Check viewport and rectangles, not only event labels.

Any mismatch or unavailable browser is FAIL, not a reason to relax the expected sequence. Preserve original outputs and failure stage. A second execution uses identical frozen fixture/runner/protocol input identities in a separate isolated browser environment. Do not label a repeated run by the same operator an independent replication.

## Source and interpretation

W3C Pointer Events Level3, Recommendation 2026-06-30: https://www.w3.org/TR/2026/REC-pointerevents3-20260630/ . Sections4.1.3/4.1.3.2 explain recipient override and pending capture;4.2.6,4.2.11 and9.2–9.5 explain up, capture loss and release. Source gate and independent reader analysis are separate from this protocol.

The cases establish only these original divs and this installed browser's reported version. elementFromPoint is used as a geometric comparison in this untransformed, unobscured fixture, not a ready-made inventory drop resolver. A successful source-targeted up is not itself game acceptance; capture loss following up is not itself application cancellation. No pointercancel is induced or simulated, no click behavior is asserted, and no native engine or mobile behavior is inferred.

## Execution bound and failure preservation

Invoke the runner under an external 60-second wall-clock watchdog, with termination followed by kill after five seconds if necessary. Save stdout, stderr and actual exit status separately before interpreting results. Raw stderr remains private because browser launch diagnostics may contain host details; any public failure account uses only reviewed diagnostic categories. Timeout, signal, missing or malformed JSON, nonzero exit, incomplete cases or changed input hashes are failures; never infer success from silence. A timeout may prevent normal temporary-directory cleanup; this is a failure limitation, not permission to relax sandboxing. Only a zero exit with complete PASS output for exactly the three frozen cases may be accepted. Runtime version strings are self-reports, not verified binary provenance. No second observation follows a failed first observation.
