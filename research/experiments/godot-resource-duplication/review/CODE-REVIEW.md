# Pre-native implementation review

2026-11-01 03:05 UTC. Native execution remains blocked pending one bounded archive-binding correction. Reviewed exact eleven-source manifest copied to code-review-copy/.

- `PROTOCOL.md`: `748ab0748d80145721fa8ca3095b0264bf393b47d3062da424fe60f5605a5d0c`
- `config.gd`: `3811922cd872d2f117f66c706e7cce67da7ac93d0cc51b1315ab2f53e050d4b2`
- `config.tres`: `d80f2ed2c116b32ca8e5c625550d909c38bb2ba405a20ecbccb6e9ed1d958c8f`
- `consumer.py`: `01ce8410cb5380af9558df42303a22aa789381a03746667fe9a803c1819d2b77`
- `external.tres`: `00d32179f352e34991f7b45b8aff68606553ab54a22edc73183036b020458a6c`
- `isolation.py`: `bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970`
- `main.gd`: `19a245e40d70743ce78792a7bca3db494fafd171b3160b246a281eb3edd0e3c9`
- `oracle.py`: `fd80a5d0d744594236919be1a8b76406e7c9740dd867b5e0d0c3fc2735db7802`
- `project.godot`: `b6355e8cb497cbaff0af27bde642380b53929c8e16ae94a84ddb00bcfed6c7be`
- `run.py`: `311b58d024d5072e7fd19d26bbd0c95f02c699b48abbce8e743a13235015ed57`
- `test_pure.py`: `0654efe60640deaa966d0d5e439aa659a570db201eb764d9d2ad3cfc17b313f7`

## Material finding

consumer.verify compares parsed JSON to raw-derived object using Python ==, accepting bool/number substitutions. Reproduced on an otherwise accepted synthetic archive: replace parsed all.json stages[0].d.values[0].colors[0][1] numeric zero with false, recompute only parsed artifact hash, keep raw stream unchanged. verify accepts. Probe and actual output preserved as probe_parsed_binding.py and probe-parsed-binding.txt. This is not fabricated native evidence or a wrong raw oracle; it contradicts exact raw/parsed association. Use recursive exact-type structural comparison for parsed association and derived-oracle association, plus bounded regressions. Preserve initial source before correction.

## Other inspected gates

Read complete GDScript, protocol, runner, oracle, consumer and pure tests. Setup checks precede copy/edit and validate live cached/root/alias graph, storage flags, resource paths/classification, untyped array, gradients and script. Snapshot dictionaries contain freshly constructed scalar arrays/strings, not mutable live resource arrays. Copies keep original references alive and use ordered append/internal/external mutations; no resetting witness state.

Runner uses fresh mode project copies, exact manifest/protocol/helper/binary checks, one version then three mode processes with stop on failure, isolated base environment, PID/mode/UUID binding and raw stream preservation. Maximum four native process attempts, no automatic retry. Timeout group kill/wait is bounded best effort, not universal descendant cleanup. Source/input before-after gates and parsed/raw association supplement the live graph oracle; no official-build authenticity follows.

Executed only exact-copy pure suites: five methods normal and five under -O, both exit0; each suite includes two guarded Python startup failures, four Python children total, zero Godot/version/parser/native calls. Additional synthetic binding probe is a pure Python check, not a resource observation. Raw logs retained. This review does not authorize native entry.
