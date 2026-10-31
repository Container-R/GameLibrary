# Actual Godot actor callbacks and same-tick combat policy

## Result and scope

Four fresh installed-engine processes, one complete combat physics frame each, on 2026-10-31. Fixed actual child order Begin,A,B,End; Begin priority -100, End 100. Independent actor Node callbacks have priorities 0/10, swapped between runs. They are not a manually sorted actor loop in a coordinator.

| Mode | A/B priorities | Actual callback order | Final HP A/B | Qualified attacks |
|---|---|---|---|---|
| Immediate | 0/10 | Begin,A,B,End | 1/0 | A→B |
| Immediate | 10/0 | Begin,B,A,End | 0/1 | B→A |
| Staged | 0/10 | Begin,A,B,End | 0/0 | A→B, B→A |
| Staged | 10/0 | Begin,B,A,End | 0/0 | B→A, A→B |

Initial HP is 1 each; damage is 1. Immediate callbacks check current HP and mutate immediately. Staged callbacks qualify from Begin's HP snapshot, queue intents, and End commits them. All four callback records share one actual Engine.get_physics_frames value (1 in these runs), with delta approximately 1/60. Actual node priority/group, entry HP and eligibility are recorded. Child order is read from get_children at completion. Default inherited main-thread process group only; no cross-group test.

Staged event order changes but normalized events and final HP agree. This is a chosen application policy allowing qualified attacks to survive same-tick death, not an engine-provided transaction. Sequential first-strike can be another deliberate game rule. These results are not a fairness evaluation or engine bug report.

## Reproduce and evidence

Run `python3 run.py`; requires existing `/usr/local/bin/godot`. Four engine processes only, each using headless/single-threaded-scene flags, isolated HOME/XDG directories and a 20-second external timeout. No installation.

- contract.md was frozen before implementation and calls: ef2ff66f0e7124fc74cc67036b7cd6f248836fc093263bef3f89bb6ccba649d5.
- main.gd/main.tscn/project.godot: original fixture.
- results/*.stdout, *.stderr, *.status.json: raw trace/results, actual command/exit and timeout setting.
- Four TRACE_JSON records plus one RESULT_JSON per process; result includes intents/events, HP, version self-report and observed child order.
- results/summary.json: written only after all four trace/outcome checks pass; source and binary hashes included.
- run-output.txt/run-stderr.txt: author outer invocation; exit 0, empty stderr.

Begin snapshots once. End requires all four callback entries, disables all phase/actor physics callbacks, and a later idle callback prints result and exits. No second combat frame, sleeps, priority mutation during callbacks, node removal or external input.

The runner clears old summary before -O rejection, binary access or spawning. Timeouts preserve partial stdout/stderr and status; spawn errors preserve exception metadata. Nonzero status, stderr, ERROR output, missing/multiple result or trace mismatch fails closed. Old per-case files may remain following early failure; they do not constitute a newly completed run. No generic atomic-publication or OS cancellation guarantee.

## Instrumentation correction history

Initial four-process execution passed the frozen contract, but tree_order was a declared constant even though source insertion order was correct. Parent requested actual runtime child-name readback. Preserved initial main.gd/run.py/results/output under historical-declared-tree-order; corrected only that witness, not expected outcomes or scheduling. Final four-process repeat also passed. A crossed provenance request then added Python interpreter version/path and platform to the runner summary; the observed-tree-only batch is preserved under historical-observed-tree-only. Final runner again passed four processes. Three author batches are distinct repeats of four scenarios, not twelve unique scenarios. No engine failure was hidden. One README shell-command construction failed in the orchestration JavaScript before execution; it did not run the engine or modify evidence.

## API/source comparison and installed identity

Godot 4.6 Node documentation read 2026-10-31:
https://docs.godotengine.org/en/4.6/classes/class_node.html#class-node-property-process-physics-priority
and #class-node-private-method-physics-process.

Correct property is process_physics_priority, not process_priority. Lower values run first; equal values follow tree order. Callback requires enabled processing and tree membership. Here actor values differ; equal-priority ordering is not tested.

Pinned official 4.6.3-stable source comparison:
- https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/main/node.h#L186-L192
- https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/main/scene_tree.cpp#L1151-L1209
- https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/main/node.cpp#L91-L97

New binary SHA256: f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3.
Each process self-reports 4.6.3-stable, build official, fullhash 7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3. Public comparison tag resolves 35e80b3a… instead; prior investigation could not resolve self-reported hash in public source. Official is a self-reported string, not authenticated origin. Pinned comparison code is not verified exact source of installed binary.

## Limits

No physics contacts, animation, second-tick death eligibility, larger actor populations, concurrent groups, multiplayer/rollback, cross-platform determinism, fairness or performance evidence. Same installed binary/environment only. Existing Python policy supplement supplies separate model boundaries; this adds actual per-node scheduling evidence, not replacement coverage. Independent review pending at author freeze.
