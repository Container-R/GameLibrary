# Pre-native code review corrections

2026-11-01. No Godot/version invocation occurred during this review. Frozen protocol7e5197e2 is unchanged.

The initial eight-source snapshot and five-method pure outputs are preserved in `historical-pre-native-review/`. Independent synthetic probes found that the initial oracle accepted all driver callbacks on one physics frame and nested bool/int substitutions in a polygon index or initial configuration. These are archive-validator defects demonstrated with fabricated records, not observed navigation behavior.

Before native authorization:

- Every event within a driver callback must have the same frame; callback frames strictly increase between steps. No claim of exactly consecutive frames or elapsed time follows.
- Recursive typed comparison rejects bool/int substitutions for indices and identity/configuration fields. Geometry coordinates retain explicit finite numeric comparisons rather than assuming serialized int versus float form.
- The protocol digest is now checked before launching the version query, not only during final archive consumption.
- A complete synthetic archive control and finite source/command/environment/timeout-cleanup/UTC/raw-parsed mutants exercise the portable consumer. Seven final pure methods pass in normal and optimized Python. Each suite launches two guarded startup Python children (optimization and missing local import); zero Godot processes.

Main's earlier in-progress read also prompted exact registered region/cell/agent-setting/hierarchy gates before target submission and an observed readiness callback count. Those were implemented before the first frozen source snapshot, not a runtime fix.

The fixture drives `SceneTree.physics_frame` callbacks, which precede node physics processing; recorded frames are not proof that a physics step completed. All updating getter calls for both active agents occur before either parent assignment. Movement remains original controlled Node3D positional assignment, not collision locomotion.
