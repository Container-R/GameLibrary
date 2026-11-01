# Independent inherited focus eligibility source gate

2026-10-31 23:38 UTC. Read triage `9714f4635e8acc6a7f32dfdf9ba277848582b240c9f3c140cd9b966fbd40a672`, actual current UX article and archived Godot main.gd as text. No new code, native/version/capability command, runtime or existing-document edit.

## Existing scope verified

The current article explicitly has eleven Python policy-model tests plus actual Godot same-path replacement identity evidence. The archived gate/naive/guarded fixture changes instance identity, not ancestor focus eligibility. The proposed same-instance Control sequence therefore examines a distinct narrow boundary, not another replacement scenario. Neither old nor proposed evidence establishes keyboard/gamepad navigation isolation, native modal Window behavior or accessibility certification.

## Primary sources independently read

- [Control4.6 documentation](https://docs.godotengine.org/en/4.6/classes/class_control.html): FocusBehaviorRecursive enum, focus_behavior_recursive, focus_mode, get_focus_mode_with_override, grab_focus and focus-enter/exit signals. Inherited behavior follows the parent; explicit ENABLED can ignore the parent's restriction and use the local mode. Effective mode and local mode are distinct. These semantics support the proposal but do not establish application scope membership.
- [Viewport4.6 documentation](https://docs.godotengine.org/en/4.6/classes/class_viewport.html#class-viewport-signal-gui-focus-changed): gui_focus_changed reports acquisition, not a loss-only transition. Actual owner/null and Control exit are necessary separate observations.
- [Pinned Control implementation](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/gui/control.cpp#L2285-L2378), effective getter/recursive propagation/grab; [notification cases](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/gui/control.cpp#L3952-L3960). Propagation traverses direct Control children, stops through explicit child overrides, and releases focused inherited-disabled descendants. Crucially, release occurs before updating the descendant's cached parent-enabled field. A focus-exited callback may therefore read the old effective mode during propagation; post-setter state is a different observation boundary. Enter/exit notifications emit the corresponding Control signals.
- [Pinned Viewport acquisition](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/main/viewport.cpp#L2699-L2718) and [release/getter](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/main/viewport.cpp#L3726-L3739): release clears owner before exit notification. Acquisition sets owner, emits viewport gain, then sends Control enter notification. Passive callbacks permit a finite ordering observation; callback-triggered repair would change the experiment.

All accessed2026-10-31. Documentation version path4.6 is explicit. Pinned comparison commit35e80b3a is not authenticated source of the previously observed local binary; retain the shared runtime-provenance note and verify actual bytes only after separately authorized execution.

## Oracle clarification required before freeze

**Do not require effective NONE inside focus_exited callback.** During ancestor propagation, the child cache may not yet be updated. Freeze callbacks as passive event/ID/owner recorders, then assert effective eligibility only in the explicit synchronous snapshot after the setter returns. If eligibility is also logged inside a callback, label it in-callback observation and do not silently compare it with the post-setter row.

Likewise, returning from a deferred callback is not proof of a rendered frame. The null-owner interval is a synchronous controlled state, not evidence that a user sees a blank-focus frame. No invalid-node grab is needed to manufacture a warning.

## Prospective finite post-call table

All settings/IDs below are intended observations to freeze, not executed results:

| Operation completed | Background recursive | Same Opener recursive/local/effective | Expected owner |
|---|---|---|---|
| baseline acquire | ENABLED | INHERITED / ALL / ALL | Opener |
| disable Background | DISABLED | INHERITED / ALL / NONE | null |
| explicit fallback acquire | DISABLED | INHERITED / ALL / NONE | modal Default |
| enable Opener override, before grab | DISABLED | ENABLED / ALL / ALL | modal Default |
| deliberately grab Opener | DISABLED | ENABLED / ALL / ALL | original Opener |

The setter-only override row matters: becoming eligible does not itself mean acquiring focus. An optional post-counterexample repair should be omitted from the minimal accepted sequence or separately frozen, not silently added. Stable exact nonzero instance IDs, direct Control ancestry, inside-tree/visible state, local/effective settings and viewport identity should be recorded. Do not require IDs to be positive or persist them as application identifiers.

With passive handlers and no initial focus, source predicts three viewport gains, three Control entries and two exits for this sequence, with no viewport gain at the disable-only or enable-only boundary. Treat this as a candidate finite source-derived expectation, not a universal callback ordering contract across arbitrary scripts or proof of the installed implementation. Unexpected actual behavior must stop the claim rather than trigger extra timing/configuration permutations.

Gate accepted for protocol drafting with the callback/post-setter distinction explicit. The substantive finding would be that recursive eligibility is overridable, so a product's modal scope policy cannot be reduced to that engine setting alone. It would not prove a complete navigation trap, input containment or accessible modal design.
