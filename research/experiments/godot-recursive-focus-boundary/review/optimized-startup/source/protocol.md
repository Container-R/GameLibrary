# Candidate frozen protocol: recursive focus eligibility and explicit child override

2026-10-31. **Draft pending main acceptance; no implementation or new runtime/version invocation.** Source gate `research-drafts/modal-focus-depth-gate/triage.md` SHA256 `9714f4635e8acc6a7f32dfdf9ba277848582b240c9f3c140cd9b966fbd40a672`. If approved, preserve these bytes and record acceptance separately.

## Product rule and finite question

While the logical modal owns input, background Opener must not become the active focus target. Does setting only its parent's recursive behavior to DISABLED enforce that rule when the same child explicitly opts into ENABLED?

This is a deliberately incomplete application policy, not an engine defect or a native modal Window. The expected counterexample is **effective focus eligibility succeeds but application scope membership remains wrong**. No new identity, deferred-generation or input-device model is needed.

## Original fixed scene

One root Control named Fixture; direct Control children Background and LogicalModal; Opener is a direct Control child of Background and Default is a direct Control child of LogicalModal. No intermediate plain Node, CanvasLayer, SubViewport or Window. No other focusable node. All nodes remain in the same live tree and visible throughout; none is reparented, hidden or recreated.

- Root, Background, LogicalModal: local FOCUS_NONE.
- Opener and Default: local FOCUS_ALL; size `(160,40)`; Opener position `(0,0)` within Background, Default `(200,0)` within LogicalModal. No text, font, theme override or drawing oracle.
- Background initially FOCUS_BEHAVIOR_ENABLED; Opener initially FOCUS_BEHAVIOR_INHERITED.
- LogicalModal initially FOCUS_BEHAVIOR_ENABLED; Default initially INHERITED.
- Root behavior INHERITED. All nodes explicitly `visible=true`; no accessibility-specific mode.
- Stable process-local nonzero integer instance IDs recorded for all five nodes; no positivity assumption. Original Opener ID must remain identical at every phase.

The logical modal's product ownership is a recorded application label, not native engine modality. It becomes active at the background-disable phase; no actual user input is sent.

## One behavior sequence

Connect passive Control `focus_entered` / `focus_exited` callbacks on Opener and Default and viewport `gui_focus_changed` before the sequence. Callbacks record only; never grab/release focus, mutate recursive settings, schedule repairs or emit user input. Start the sequence via one deferred entry after construction.

All trace rows have a monotonically assigned sequence number and explicit phase. Read actual viewport owner (ID/name or null), local/effective modes, recursive behavior, live-tree and visibility states. Record callback target ID. Callback-time effective modes are **diagnostics only**, not the post-setter oracle.

1. `initial`: owner must be null; Opener effective ALL, local ALL, inherited; Background enabled. Acquire Opener exactly once. `baseline_after_grab`: actual owner Opener. This is the capability gate.
2. `before_parent_disable`: label logical modal ownership active, record Opener still owner. Call Background recursive setter DISABLED exactly once. `after_parent_disable` **after setter returns**: Opener still local ALL and inherited, but effective NONE; viewport owner null. Same child identity/tree/visibility. Require its focus-exited event to occur between before/after markers. No `grab_focus` call on the known-ineligible Opener.
3. Acquire Default exactly once. `modal_after_grab`: owner Default; Default local/effective ALL. Background remains DISABLED and Opener effective NONE.
4. `before_child_enable`: retain modal ownership label and Background DISABLED. Set Opener recursive behavior ENABLED exactly once. `after_child_enable` after return: same Opener now local/effective ALL, Background still DISABLED, owner remains Default. Setter alone does not request focus in this protocol.
5. Deliberately issue naive Opener `grab_focus` exactly once. `naive_after_grab`: actual owner Opener, outside the logical modal subtree. Default exited and Opener entered. This is the expected product-rule failure, not an expected process failure.
6. Queue a distinct deferred observation only after step5. `deferred_final`: actual owner still Opener and settings unchanged. Record that this is a separate deferred callback; do not assert a whole rendered frame elapsed. Quit successfully only after this finite observation.

Expected successful trace signal memberships: Opener entered twice and exited once; Default entered once and exited once; viewport gain signals target Opener, Default, Opener in that order. In particular, no viewport gain signal is expected for the parent-disable loss/null transition. Control callbacks must occur inside the corresponding call markers, but do not require an extra exact order between viewport gain and Control-enter signals beyond these memberships and transition boundaries. Record all signals, fail on extras.

### Important intermediate-state boundary

Pinned Control propagation source releases focus before updating its cached inherited behavior. Therefore an Opener `focus_exited` callback during parent disabling may observe local/effective ALL while owner is already null. **Do not demand effective NONE inside that callback, do not demand ALL either, and do not “repair” focus from it.** The effective NONE assertion belongs strictly to `after_parent_disable`. This avoids turning an intermediate notification into a post-transaction state oracle. Raw callback fields remain available for interpretation, not hidden.

## Evidence/process and failure protocol

One separately counted `--version` process plus **one behavior process containing the whole sequence**. No engine launch before source and pure-validation review acceptance. Later independent repeat is a separate authorization, not automatic. No FPS matrix, alternate hidden states, physical devices, synthetic navigation or additional background guard variant.

- Existing installed path `/usr/local/bin/godot`; historical expected SHA256 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`, self-report `4.6.3.stable.official.7d41c59c4`. Check current bytes before launch and after the sequence; mismatch stops. Self-report is not authenticated source provenance.
- Minimal explicit base environment PATH/LANG/LC_ALL plus exact additive `isolation.py` helper SHA256 `bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970`. Preserve five selected paths, not inherited secrets. No legacy runner/harness edits.
- Headless, single-threaded scene; original project has no external assets or imports. Exact argv frozen with implementation before review. Version and behavior each have a 20-second external deadline; behavior also has a finite 120-process-callback watchdog. These are failure bounds, not timing guarantees.
- Fresh UUID invocation/evidence directory, no prior output reuse. Remove stale PASS pointer before optimized rejection/local imports. Runner `-O` rejected before engine entry. Attempt and return UTC timestamps, argv, status and raw stdout/stderr retained; timeout cleanup attempts own process-group termination plus bounded wait, without guaranteed containment.
- No expected engine warning/error: both streams reject unexpected diagnostics; behavior stdout permits documented engine banner plus exactly one `RESULT_JSON` payload. Original source manifests before/after, binary identity and raw/parsed/output hashes retained. Valid JSON must reject duplicate keys and bool/int substitution for IDs/modes/counts.
- Pure independent expected oracle reads actual snapshot fields/signals and target identity/parent membership rather than treating recorded request names as focus results. Preserve a complete failed receipt/source/raw output and stop on first unexpected outcome; no quiet timing/scene/oracle changes.
- Portable static archive check needs no current engine, binds exact source and raw RESULT_JSON/parsed association, statuses/argv/identity and literal phase oracle. No execution-authenticity guarantee. Pure negative receipt mutations/startup checks do not count as native focus cases.

## Sources and scope

Official Godot4.6 Control enum/property/effective getter/grab_focus documentation, Viewport gain-signal/get-owner documentation, and pinned comparison source control.cpp2285–2378, viewport.cpp2699–2718/3726–3739 were read before this protocol; see source gate for links. Public source commit `35e80b3a8822a9df9be390814b62f44c0a9c69e8` is not established as source of the installed binary.

No real keyboard/gamepad/mouse action, button activation, pointer filtering, modal navigation containment, focus indicator visibility, human perception, screen-reader/certification, multiple users, native windows or Unity execution. This tests programmatic focus and a same-instance configuration transition only. A momentary synchronous null owner is not evidence of a player-visible blank frame.
