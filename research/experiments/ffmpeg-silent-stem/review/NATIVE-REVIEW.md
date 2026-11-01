# Offline amix independent native repeat

2026-11-01 03:34 UTC. Accepted the bounded observation. No material correction requested.

## Preconditions and actual attempts

The unchanged pre-native independent checker (`11d5163dd3e2a9c10406757553df0938a7e87e1b10b9a4a284cb116a349bfbde`) first accepted author UUID `0522fc0d-998a-489a-ba2d-05a8418dabd2`, receipt SHA256 `67991e9951053ccc0d5cd8b62f7c024bb574e98d288d679e016ddc4a39db742e`. Static normal/optimized results and an explicit pre-repeat exit0 record are retained. These static calls do not launch FFmpeg.

After the parent's separate authorization, copied the exact six files plus manifest `e830cfff7cbae792af06a6cdbba4e0a6a16e73fc66978328a1adbc046fd9540c` to `native-repeat/`. Source hashes were checked before and after. Executed exactly one normal runner invocation, no retry or changed option:

- reviewer UUID `59a5d8a4-39ef-448f-8771-622108e7b86c`;
- receipt SHA256 `7b2d14f96f3f4899b2d8ff0e8b18721e415f4e4f573ef03c38405745a7e8402b`;
- one version query and three sequential mixes, all exit0;
- version stdout retained, version stderr and all mix stdout/stderr empty;
- recorded selected binary/library and source/input before-after hashes unchanged;
- final independent checker exit0, without author checker imports.

Outer runner command, stdout/stderr/exit, source before-after records and complete receipt/raw/hex outputs are preserved. Native PIDs are local process metadata, not global identity/authentication. No extra help/filter/ffprobe/playback invocation occurred.

## Literal whole-output result

Each output has4096 mono f32le frames,16384 bytes; all samples match the pre-code literal oracle `a904ecc7a41cbc9338f0b1ee8f48ecc046835a0792d67815e3bff9c039c36f2b`:

| Configuration | Observed complete sequence | SHA256 |
|---|---|---|
| full-normalized | +0.25 on[0,4096) | `680aca77ba6b819a4489730f3e42f69ba9f6d7a5921e748a8a46eb1974d0867c` |
| short-normalized | +0.25 on[0,2048), +0.5 on[2048,4096) | `882c6f4354476535c7eec3d6c7e165d80ceefc3f52dc9b8663bf65c7acf70a4c` |
| short-unscaled | +0.5 on[0,4096) | `66e39e41bccc0a57ae90a77b426f4075e81ba877b0653c3aabe0a9e00762769c` |

Both accepted invocations used the same three configurations: combined two version queries plus six mixing processes, eight native processes, not six unique mixing cases. No native failure, timeout, clipping, internal frame scheduling instrumentation or audio-device result was observed. The prior failure-finalization/UTC corrections were pre-native code review findings, not failed mixer runs.

This establishes the fixed installed offline mix behavior: silence while present and EOF removal can differ under this normalization setting. It does not establish real-time middleware scheduling, perceived music quality, arbitrary float bit reproducibility or source authenticity of installed binaries. Static receipts and checker demonstrate recorded integrity, not authenticated execution. Full hex is portable; local PCM binaries may be omitted from publication without losing bytes.
