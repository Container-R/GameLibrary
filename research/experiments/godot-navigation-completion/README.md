# Path exhausted is not requested target reached

Original finite NavigationAgent3D observation, 2026-11-01. This extends SOL-AI-001 without modifying the older navigation-sync/radius fixtures. No character collision locomotion is claimed.

## Contract and execution

Frozen protocol SHA256 `7e5197e2368bb8be30c446b3a8ac1cc2274b781e77e2db8238a1788963d53dad`. Eight source hashes are in `SOURCE-SHA256.json`. One map holds two original disconnected convex XZ rectangles `[0,10]×[0,4]` and `[20,30]×[0,4]`, Y=0. No baking, links or collision shapes. Two separate Node3D parents start `(2,0,2)` with targets `(8,0,2)` and `(22,0,2)`; both agents have avoidance disabled.

Actual map/region readiness and requested settings are checked before assigning targets. Initial real agent paths and projected target owners are checked before movement. The driver advances each parent by at most0.5 toward its actual next path point. It does not replace the engine path or place the partial-route actor at the requested goal.

Per driver callback, each active agent has exactly four explicitly updating calls in order: get_next_path_position, is_navigation_finished, is_target_reachable, get_final_position. All queries for both agents occur before either position assignment. No post-assignment updating getter is called until the next callback. Signal callbacks only record data and latch finish; after finish no further position write occurs. The callback is SceneTree.physics_frame, before node physics processing, not an assertion that a physics step completed. Watchdogs are240 readiness callbacks,48 driver callbacks and per-process wall deadlines, not guaranteed arrival timing.

## Actual author result

UUID `67f74800-c547-4c0b-aba1-1bea7445f2c8`: one version query plus one behavior process, both exit0 with empty stderr. First native attempt passed. Source/binary before-after digests agree. It observed2 readiness callbacks and17 driver callbacks, with337 trace events.

| Agent | Target X | Final parent X / path endpoint X | Position assignments | Signals |
|---|---:|---:|---:|---|
| Reachable | 8 | 8 / 8 | 12 | target_reached then navigation_finished at driver callback13 |
| Partial | 22 | 10 / 10 | 16 | navigation_finished only at callback17 |

Final reached/finished/reachable values are true/true/true and false/true/false. The original partial target lies on the other region; it is not outside all navigation surfaces. Actual path starts were approximately `(1.99999988079071,0,1.99999988079071)` and pass the frozen1e-5 coordinate tolerance; archived values remain unchanged. These step counts are observed under fixed controlled assignments, not speed/performance measurements.

Independent repetition UUID `20597db7-f5c8-49d4-95eb-c4f80d1d781e` passed with the same337 events,17 callbacks and12/16 position assignments. Combined author/reviewer: **2 behavior processes + 2 version queries = 4 Godot processes**, repeating the same2 routes, not4 unique conditions. An original independent raw reader imports no author validator; both readers pass both archives under normal Python and `-O` (8 main static commands, zero new Godot processes). These are same-binary repeats, not cross-build confirmation.

## Validation and pre-native history

The portable consumer binds raw stdout to parsed result, exact sources, selected environment, commands, process statuses and binary hashes. The original oracle replays every query marker, signal, parent position and move_toward displacement; it requires all events in one callback to share a frame and successive callback frames to increase. It reconstructs final states rather than trusting a child PASS string.

`historical-pre-native-review/` preserves the first eight-source snapshot and pure results. Synthetic review found acceptance of collapsed frame identities and nested bool/int substitutions. Corrected code adds recursive typed comparisons, explicit numeric coordinate checks, callback frame checks and protocol pinning before any native launch. Seven final pure methods pass normal/-O, including a complete fabricated archive and finite source/argv/environment/UTC/raw association mutants. Each suite runs two guarded Python startup children; these are not Godot observations. `PRE-NATIVE-CORRECTIONS.md` describes the exact boundary.

Successful native execution does not test watchdog expiry, process cleanup failure, map initialization failure, dynamic repath or every schema mutation. On timeout the runner attempts bounded process-group cleanup; code inspection is not evidence of successful cleanup in every failure mode.

## Inspect without invoking Godot

```sh
python consumer.py . evidence/67f74800-c547-4c0b-aba1-1bea7445f2c8
python -O consumer.py . evidence/67f74800-c547-4c0b-aba1-1bea7445f2c8
```

These commands read archive bytes only and do not require the recorded binary or historical absolute directories. Reviewer artifacts use their own exact copied source and evidence directory arguments.

Do not execute run.py inside an archived directory: it removes summary.json and adds invocation data. A separately authorized repetition must copy exactly the eight source names in SOURCE-SHA256.json into a fresh disposable directory, preserve hashes and use the pinned installed binary. Then invoke Python run.py from the copy. No installation, source tweak, tolerance sweep or automatic retry is part of this fixture.

## Identity and limits

Installed file SHA256 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`; program self-report4.6.3.stable.official.7d41c59c4. Public comparison source commit `35e80b3a8822a9df9be390814b62f44c0a9c69e8` is not authenticated as that binary's source. Consistent hashes/raw records are not a signature of execution authenticity.

Evidence covers controlled Node3D position updates and actual navigation state/signals, not CharacterBody3D, move_and_slide, collisions, RVO, root motion, complete mission arrival, cancellation/repath races, concurrent/streamed navigation, frame timing, rendering or performance. Original application recommendations must keep requested target semantics separate from path exhaustion; some games intentionally accept reaching a partial-route boundary.
