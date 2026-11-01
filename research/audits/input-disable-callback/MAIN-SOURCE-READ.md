# Main input cancellation call-path read

2026-11-01 UTC. Independently resolved official InputSystem tag `1.11.2` to commit `c8518694c7fdd2c755755e028e2ec19cdceda19b`. The selected official InputAction documentation identifies package 1.11.2; this is not a claim about latest or installed Unity.

Read pinned `InputAction.cs` 789–802 and 916–935; `InputActionState.cs` 227–265, 824–881, 1021–1053, 1071–1082, 1925–2043 and 2355–2569; `DelegateHelpers.cs` 36–59; and `CallbackArray.cs` 1–78. The ordinary Value-action path can remain Started without an explicit interaction, supporting the proposed finite witness without implying a Hold interaction. Cancellation dispatch happens before the disabling call finishes; application callbacks are invoked directly. Shared-state disposal and callback-list mutation must not be inferred to provide an application transaction or blanket safety guarantee.

The proposed double cleanup is original, conditional reasoning about deliberately specified application code. It assumes the same preview identity, two non-idempotent release paths, no ownership transfer guard and no other listener changing those assumptions. No engine trace, input event, actual release, crash, timing measurement or implementation test was produced. A standalone note can safely link the existing fixed-step article without changing it or transferring its different evidence.

Sources: [pinned repository](https://github.com/Unity-Technologies/InputSystem/tree/c8518694c7fdd2c755755e028e2ec19cdceda19b), [selected official API](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.11/api/UnityEngine.InputSystem.InputAction.html#UnityEngine_InputSystem_InputAction_Disable). No source body or private execution metadata is reproduced.

Additional exact check: `InputAction.cs` line 532 defines enabled by phase not being Disabled. In the stated no-other-listener-mutation witness, cancellation dispatch observes Canceled before the final Disabled assignment. Therefore checking only the negation of enabled cannot identify the application's shutdown intent inside that callback. This is a source-order inference, not a measured getter result.
