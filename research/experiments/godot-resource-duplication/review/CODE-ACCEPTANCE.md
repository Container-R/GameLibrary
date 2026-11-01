# Final pre-native code acceptance

2026-11-01 03:07 UTC. Accepted exact final manifest c105634a0748ccd16589138bc94e5a292e80e4ff7f822cdb32f16f8160d60ddf after narrow correction.

- `PROTOCOL.md`: `748ab0748d80145721fa8ca3095b0264bf393b47d3062da424fe60f5605a5d0c`
- `config.gd`: `3811922cd872d2f117f66c706e7cce67da7ac93d0cc51b1315ab2f53e050d4b2`
- `config.tres`: `d80f2ed2c116b32ca8e5c625550d909c38bb2ba405a20ecbccb6e9ed1d958c8f`
- `consumer.py`: `26613da32adc38e793fbadcbbb67ba1dd12cd7088f12b5f81c44492896c97f73`
- `external.tres`: `00d32179f352e34991f7b45b8aff68606553ab54a22edc73183036b020458a6c`
- `isolation.py`: `bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970`
- `main.gd`: `19a245e40d70743ce78792a7bca3db494fafd171b3160b246a281eb3edd0e3c9`
- `oracle.py`: `fd80a5d0d744594236919be1a8b76406e7c9740dd867b5e0d0c3fc2735db7802`
- `project.godot`: `b6355e8cb497cbaff0af27bde642380b53929c8e16ae94a84ddb00bcfed6c7be`
- `run.py`: `311b58d024d5072e7fd19d26bbd0c95f02c699b48abbce8e743a13235015ed57`
- `test_pure.py`: `bc8396d9a2279b9cb9b9350d29f93f6e6f09971faad8a2d74096a91529eea22a`

Inspected exact consumer/test delta: recursive structural equality requires exact scalar/container types for raw/parsed and derived-oracle binding. Initial false-accept probe now rejects at raw/parsed association with otherwise valid synthetic receipt; new regression also rejects derived boolean replaced by integer1. Initial source/probe/review remain preserved. No GDScript/input/protocol behavior changed.

Fresh final exact-copy suites: six methods normal and six optimized, both exit0. Each suite has two guarded Python startup children, four Python children across this final pair, zero Godot/version/parse-only/native calls. Independent original false-accept probe repeated once on corrected copy, now rejection. Raw final logs and probe output retained. Earlier initial five-method runs are separate pre-correction evidence, not final coverage or native failures.

No remaining material blocker for the frozen finite graph experiment. Parent retains native invocation authorization. Snapshot/setup/source/environment/process-count/failure-scope findings in CODE-REVIEW.md remain valid; no broad security, lifetime, authentication or universal process-cleanup guarantee added.
