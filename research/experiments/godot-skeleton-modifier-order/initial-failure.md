# Initial oracle failure — no retry yet

2026-10-31. Native commands in UUID `d950544e-f0af-4068-aa0f-780ede638355` both returned 0 (one version and one behavior process); full Python acceptance failed at the additional `is_interpolating() == false` check. All raw streams and parsed payload remain under `results/`; complete frozen sources and runner streams are copied under `historical-false-interpolation-oracle/`. This is not an accepted full run or an engine error.

Actual snapshots return `is_interpolating=true`, `get_interpolation_remaining=0`, `duration=0`. The initial checker inferred the Boolean from its name. The pre-code contract required duration zero and recording interpolation state; it did not freeze a false Boolean value.

Read original pinned comparison source on 2026-10-31:
- [Getter implementations, lines 383–389](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/look_at_modifier_3d.cpp#L383-L389): remaining time multiplies internal remaining by duration; Boolean returns whether internal remaining is approximately zero.
- [Interpolation branch, lines 593–606](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/look_at_modifier_3d.cpp#L593-L606): branch depends on positive internal remaining.
- [Transition initialization, lines 784–790](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/look_at_modifier_3d.cpp#L784-L790): zero duration returns without initializing transition.

This explains why the Boolean name is not a suitable sole acceptance oracle in the inspected source. It does not authenticate the installed binary's exact source or establish an engine defect. Proposed correction removes only the unfrozen false-value assumption, retains a Boolean type check and records its actual value. Duration, remaining time, every literal stage/global basis, origin, order and deferred-restored-pose expectation stay unchanged. Parent approval required before corrected execution; no warm-up or geometry adjustment.

## Approved correction and actual repeat

Main and independent reviewer read the same pinned branches and approved the narrow removal. Corrected UUID `94105a77-e9f7-4367-ba9e-dfd4802f1224` passed on 2026-10-31: one behavior process containing the same two evaluations, plus one version query. The GDScript, project, protocol and isolation helper were unchanged. Only the runner's false-only Boolean check became a Boolean type check. Original failed receipt remains FAIL; its native exit 0 is not retrospective full acceptance. No vector/tolerance/history adjustment occurred.

The official [4.6 method description](https://docs.godotengine.org/en/4.6/classes/class_lookatmodifier3d.html#class-lookatmodifier3d-method-is-interpolating), reread after the failure, combines a description of interpolation running with equivalence to zero remaining seconds. That wording does not justify our original false-only inference. We report the raw getter values, exact inspected source conditions and finite geometric result instead of declaring an engine defect or a universal corrected Boolean meaning.
