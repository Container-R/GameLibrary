# Input Disable callback boundary — independent source review

2026-11-01 UTC. **ACCEPT for a new standalone safe source note**, with the explicit branch/example clarifications below. Do not amend or re-upload the existing fixed-step article; the gate's supplement recommendation is superseded by this publication constraint.

## Sources independently read

Opened official [InputAction documentation](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.11/api/UnityEngine.InputSystem.InputAction.html#UnityEngine_InputSystem_InputAction_Disable); returned metadata identifies Input System 1.11.2. Generator date is not release chronology.

Fetched original files at `c8518694c7fdd2c755755e028e2ec19cdceda19b` under [the official package source](https://github.com/Unity-Technologies/InputSystem/tree/c8518694c7fdd2c755755e028e2ec19cdceda19b/Packages/com.unity.inputsystem/InputSystem):

- Actions/InputAction.cs 789–802, 916–935.
- Actions/InputActionState.cs 227–265, 824–881, 1071–1082, 1925–2005, 2435–2569.
- Actions/InputActionMap.cs 335–350.
- Utilities/DelegateHelpers.cs 36–59; Utilities/CallbackArray.cs 41–75.

These establish Disable → reset → synchronous canceled listener entry before the outer call returns, shared disposal scope, and queued callback-list removal while locked. The processing assertion does not establish a safe rejection guarantee; helper exception handling does not provide a propagated failure acknowledgement. No implementation execution was performed.

## Started without an explicit interaction is coherent

The additional exact locator [ProcessDefaultInteraction, 1925–2005](https://github.com/Unity-Technologies/InputSystem/blob/c8518694c7fdd2c755755e028e2ec19cdceda19b/Packages/com.unity.inputsystem/InputSystem/Actions/InputActionState.cs#L1925-L2005) resolves this concern. A non-pass-through Value action without an explicit interaction can perform then return to Started while actuated (1958–1967, 1993–2004). A partially actuated button path is another source branch, but no second scenario is needed.

For the eventual note, use the Value-action branch explicitly, or state Started as the source-supported precondition. Do not describe the application “charge preview” as evidence of Unity's Hold interaction; that would leave the no-interaction branch. Application Active and InputAction Started are distinct state domains.

## Original witness and intervention scope

The two-release witness is valid only with all stated assumptions: owner still Active during Disable; canceled handler releases the same preview; outer stop also releases it; no idempotent guard or ownership transfer; no other listener mutates the setup. It proves two requested application release operations in that hypothetical code flow, not inevitable destruction, damage, an engine crash or an observed trace. Cancellation is not automatically a gameplay commit or a user-release reason.

Marking Stopping before Disable and assigning one cleanup owner are original application policies. Listener removal alone does not revoke callbacks already in a locked iteration. A borrowed action does not confer shared-state disposal authority. Deferring disposal to a known safe owner-controlled boundary must remain a proposal, not a universal next-frame guarantee or a claim that the Destroy assertion guards every callback context.

Keep the new public note self-contained and source-only; link the unchanged fixed-step article without copying its runtime identity data. Condense source locators and avoid reproducing library implementation. No Unity, input device, synthetic runtime, model, engine invocation or remote write occurred in this review.

## Authorized addendum — enabled during cancellation (2026-11-01 05:20 UTC)

Prior review identity: `2b93191826feb00affa3a456afef1294f7d5d102888c270ce1e732868389f005`. Independently re-read the pinned InputAction.cs 532 and InputActionState.cs 824–870, 2408–2416, 2435–2498. `enabled` excludes only Disabled. The internal transition writes Canceled into the action state before listener dispatch; the outer transition writes Disabled after callbacks return, followed by reset. Under this witness's no-other-action-mutation premise, a cancellation callback entered by Disable can therefore observe enabled true. Using `!action.enabled` as a shutdown-cause discriminator is unsound for this path. This is a source inference, not a runtime observation or a guarantee under arbitrary reentrant state mutation. No broader lifecycle claim is added.
