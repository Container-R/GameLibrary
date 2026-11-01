# Godot recursive focus eligibility: same instance, different effective policy

Original finite headless experiment, 2026-10-31. This extends the existing modal-focus article's eligibility boundary; it does not repeat the old same-path/replacement identity experiment or implement a native modal window.

## Actual accepted observation

Corrected author UUID `8f698718-c420-4687-965d-4785a3154987`: one version query and one behavior process, both exit 0, stderr empty. The behavior sequence contains 12 explicit markers and 8 passive focus signals. Accepted `main.gd` SHA256 `4a6006f6ef378cf1c8801e1b77cc2cd5de354b25ade331682a112690233102ff`; full eight-source manifests before/after and exact binary identity are in its receipt.

All five original Control nodes remain live/visible with the same identities and actual recorded parent/viewport relationships. Opener's local `focus_mode` stays FOCUS_ALL. Its Background parent's recursive setting and its own override change:

| Observation phase | Background recursive behavior | Opener recursive behavior | Opener effective mode | Actual owner |
|---|---|---|---|---|
| Baseline after acquisition | ENABLED | INHERITED | ALL | Opener |
| Parent-disable exit callback | DISABLED | INHERITED | ALL observed, diagnostic only | null |
| After parent setter returns | DISABLED | INHERITED | NONE | null |
| After explicit modal fallback | DISABLED | INHERITED | NONE | Default |
| After child ENABLED setter returns, before grab | DISABLED | ENABLED | ALL | Default |
| After deliberate naive background grab | DISABLED | ENABLED | ALL | Opener |
| Separate deferred final observation | DISABLED | ENABLED | ALL | Opener |

The explicitly enabled child can acquire focus while its background parent's recursive setting remains disabled. That is an observed counterexample to the **application assumption** that the parent's setting alone forms an unbreakable modal scope barrier. It is not an engine defect: the documented child override permits this. An application that allows such an override may have a different valid policy. Effective focus eligibility and application scope membership answer different questions.

The callback row is an important intermediate-state distinction: actual owner was already null, but inherited effective mode had not yet settled to NONE. The frozen oracle deliberately requires NONE only after the setter returns; it does not require any particular effective-mode value inside that callback. Passive recorders do not repair focus, call setters or request input. A synchronous no-focus transition is not proof of a visible blank frame.

Viewport gain signals target Opener, Default, Opener. There is no gain signal for the intervening loss/null state. Actual owner snapshots and Control exit events are therefore retained separately. A deferred callback is not treated as proof that a rendered frame elapsed.

## Failure history, not erased

Initial author UUID `fb2313fd-98a4-44b1-9527-12547d3925af` remains **FAIL**: both native processes returned 0, but behavior stderr contained two SCRIPT ERROR diagnostics while the passive recorder attempted a full-tree snapshot in a focus-exited callback. Its serialized 20-row finite trace satisfies the later static inspection, but nonempty stderr prevents accepting the invocation.

`historical-teardown-callback-failure/` preserves the exact failed eight sources and full original receipt/streams. `CORRECTION.md` explains the source-consistent teardown inference; separate stdout/stderr capture does not prove their cross-stream chronology. The only post-failure source change makes `record()` return after `finished`, which is set after the final snapshot/gate or explicit failure. It closes the declared observation window; it does not suppress errors within it or claim that teardown emits no signals. The original oracle, scene, settings and timing were not widened.

Earlier pre-native review also tightened callback-owner, typed self-report, nonfinite JSON and in-engine postcall gates. `historical-pre-native-review/` preserves that initial code; independent pure synthetic false-acceptance probes are review evidence, not native runs.

Current author counts: two behavior attempts and two version queries; one failed invocation and one accepted invocation of the same unique sequence. Independent corrected-source native repeat accepted UUID `96fca0bb-b725-4072-9549-1192b45bdd49`, with empty stderr, exit 0 and an independent literal raw checker. Combined author/reviewer counts are three behavior attempts (one failed, two accepted) and three version queries, one unique finite sequence. The repeat uses the same installed binary, not an independent implementation. Four-method pure tests normal/optimized and static consumer normal/optimized invoke no engine. A separate seeded-PASS `python -O` startup check exited 1, removed the old summary, created no evidence directory and called no engine/version process. No native timeout branch was exercised.

## Sources and evidence applicability

Official [Control 4.6](https://docs.godotengine.org/en/4.6/classes/class_control.html#enum-control-focusbehaviorrecursive) enum/property/effective-mode documentation defines inheritance and explicit ENABLED overrides. [Viewport 4.6](https://docs.godotengine.org/en/4.6/classes/class_viewport.html#class-viewport-signal-gui-focus-changed) documents that its focus signal is for acquisition, not every loss.

Pinned explanatory source: [control.cpp2285–2378](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/gui/control.cpp#L2285-L2378) shows recursive eligibility and release-before-cache propagation; [viewport.cpp3726–3739](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/main/viewport.cpp#L3726-L3739) clears owner before exit notification. These source observations explain the proposed checks but are not authentication of installed source identity.

Installed binary self-report `4.6.3.stable.official.7d41c59c4`; SHA256 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`. Public comparison commit `35e80b3a…` does not match the runtime-reported full hash. Neither the word `official` nor a same-binary repetition authenticates the upstream build. Process-local IDs are nonzero integers, not persistent keys or required-positive values.

No actual keyboard/gamepad/mouse event, click/activation, focus indicator screenshot, navigation confinement, screen-reader/certification, native Window modality, multiple users or Unity integration. Tree visibility is not a perceptual visibility test. No promise of complete input isolation follows from this one programmatic acquisition sequence.

## Safe reproduction and static inspection

Do not run inside archived author/reviewer/history directories. Copy only the eight manifest source files into a **new external disposable directory**. Inspect sources and pinned binary identity, then run `python run.py` there only with explicit authority for a native repetition. The runner creates a new UUID, clears a stale summary before optimized rejection, and uses explicit base PATH/LANG/LC_ALL plus the exact five-location isolation helper. It is not a sandbox. A timeout triggers an attempt to terminate its own process group and a bounded wait; escaped descendants and all cleanup success are not guaranteed.

`python test_pure.py` / `python -O test_pure.py` use synthetic traces only. `python consumer.py SOURCE_ROOT EVIDENCE_UUID_DIRECTORY` (also with `-O`) validates recorded statuses/argv, source and raw/parsed hashes, IDs and literal finite oracle without a current engine. Recorded historical paths are data, not dependencies. Static consistency does not authenticate execution or an adversarially fabricated mutually consistent archive.
