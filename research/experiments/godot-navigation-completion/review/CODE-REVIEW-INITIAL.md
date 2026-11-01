# Navigation completion — initial pre-native code findings

2026-11-01 01:16 UTC. Native execution remains held. Copied all eight frozen sources and full manifest to initial-code before testing. Initial identities: GD dce93971, runner9a76cbbf, oracle6536230d, consumer aab5c1b9.

Five author pure methods pass normal and optimized Python in the copy. Four guarded Python startup children across those suites; zero Godot/version/native processes. Raw outputs preserved. Independent probe_initial.py imports only the pure fixture/oracle and preserves the following false accepts:

- all seventeen synthetic driver callbacks assigned the same physics frame3;
- polygon index1 replaced with boolean true;
- initial identity navigation_layers1 replaced with boolean true.

The control accepts as expected. Global nondecreasing frames are insufficient: require every event within one callback to use its exact callback frame, and strictly advance between driver callbacks. Shallow list/dictionary equality silently equates nested booleans and integers. Use typed recursive identity/index/settings comparison and explicit finite numeric coordinate validation that rejects booleans without requiring Godot JSON coordinates to retain int-versus-float spelling.

Author independently noticed protocol pin is only checked by the final consumer. Require its expected hash before the first engine process, alongside helper/binary checks. Parent independently identified the same frame/type concerns and requested full synthetic receipt tests; these should exercise source/raw/version/environment/argv and process status association, not only final oracle flags.

Source inspection otherwise supports the declared phases: SceneTree.physics_frame is the explicit pre-node-physics callback; both query phases precede all position assignments; passive signal callbacks append/latch only; updating getters are not used after assignment. Initial map/region configuration, closest-point ownership and both initial path gates precede movement. Terminal latches stop later assignment. Fixed paths, exact node identities and actual step continuity are replayed rather than only accepting final flags.

No topology/runtime conclusion is established. Preserve initial sources and failed synthetic probes; revised exact-source review is required before native authorization.
