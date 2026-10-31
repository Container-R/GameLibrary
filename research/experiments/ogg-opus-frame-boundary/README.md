# Ogg Opus: three distinct frame counts

Original finite CPU fixture, 2026-10-31. This is an encoded/container boundary extension to the PCM loop-frame experiment, not a playback or gapless-loop test. The frozen input is synthetic numeric stereo data, not third-party audio.

## Actual author observation

Accepted source: `run.py` SHA256 `301fd5346075d0d7ce4c4ecd26545c4a2e4b3efe298bca284216a2181eaf14c8`; full source manifest in `pure-evidence/SHA256SUMS` and the receipt. Frozen protocol remains `4024d6fd…`, approved separately before implementation/native execution.

Evidence UUID `2a1a6a1b-8731-4540-ac7d-f5ada6ec49ab`: one version query, one encode, one full decode, all exit 0. The encode/decode streams were empty under `-loglevel error`. No retry or failed native sequence. Process timestamps and exact argv are in `evidence/<UUID>/receipt.json`.

| Quantity | Actual frames at 48 kHz, per channel |
|---|---:|
| Original input and fully decoded presented PCM N | 93,659 |
| Actual OpusHead pre-skip P | 312 |
| Container final granule G | 93,971 |
| Coded duration D from 98 actual packet TOCs | 94,080 |
| Final trim T = D − G | 109 |

The generated file has four pages and 98 audio packets, each code 0 / config 31, yielding 960 frames per packet. Initial granule equality was checked against completed packet durations; this stream has zero initial PCM offset. Both `G − P = N` and `D − P − T = N` hold. Treating G as the presented endpoint adds 312 frames; subtracting P from coded duration but omitting T adds 109 frames. These are finite observed counterexamples, not universal pre-skip/trim constants.

No continued page occurred in the actual generated stream. A synthetic continued Tags-page case is tested separately; it is not observed encoder continuation coverage. Header padding and comment lengths are checked within the bounded subset. Valid Opus layouts outside that subset stop the experiment, not become general format errors.

Original and decoded PCM each contain 374,636 bytes = 93,659 stereo frames × 2 channel components × 2 bytes/component. Their hashes differ as expected for lossy coding; no waveform equality or audio-quality judgment is asserted. Encoded Ogg Opus is 23,808 bytes. Hashes and full lossless gzip/base64 archives are in the receipt. Each text chunk is at most 65,536 bytes; the decoded PCM archive uses eight chunks. This artificial signal's compression ratio is not a music-size prediction.

## Source and runtime boundaries

Source reasoning: RFC 7845 §§3–5.2; RFC 3533 §§5–6 (Informational); RFC 6716 §3.1 Table 2 and §3.2.2; Xiph original Ogg framing/CRC documentation. The bounded input's exact phase/metadata constraints are in `protocol.md`; it is not a general-purpose Ogg validator or Opus entropy decoder.

FFmpeg self-report is `7.1.5-0+deb13u1`. Binary SHA256 is `e8a8d46f5225f3062cec7c07fb145d58ae73c603cb740dcd5bad34bfb54e455a`; five selected resolved library identities are recorded before/after. The installed libopus SONAME/path and bytes do not establish its upstream release; package lookup found no matching package records. FFmpeg source documentation at commit `3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587` is explanatory comparison, not authenticated source for these bytes. Its listed frame-duration range differs from installed help; 20 ms is common to both and actual TOCs were independently checked.

No device/GPU/game engine/middleware invocation, auditory click/seam/perceptual test, seeking/pre-roll or random-access loop test, live transport, codec-internal resampling proof, performance guarantee or full conformance claim. A presented-PCM loop interval remains in presented-PCM coordinates; this full-decode count does not make arbitrary encoded seeking safe.

## Verification and historical corrections

- Author pure suite: five methods in normal and optimized Python; original CRC reference, finite layout negatives, synthetic continuation, consumer type/FAIL-receipt guards. No codec process.
- Pre-native review found four consumer evidence-binding gaps; exact initial source snapshot and independent synthetic false-acceptance evidence remain historical. `IMPLEMENTATION-REFINEMENTS.md` records corrections. No flawed consumer was used for a native run.
- Final author native sequence: two media processes plus one version process.
- Static consumer normal and optimized both accept this actual archive; these are zero additional media processes.
- Independent actual repeat accepted UUID `1c7b7ced-e93e-44b8-bca0-ce7b8650a1ab`: the same frozen sources and installed tools produced the same P/G/D/T and presented-frame counts. The reviewer independently read actual packet durations and checked a text-only archive copy; this is not an independent codec implementation. Combined author/reviewer: two encodes, two decodes and two version queries, one unique input/configuration.
- One separate seeded-summary `python -O` startup rejection exited 1, removed the old success summary and created no evidence directory; it invoked zero codec/tool processes. No actual native timeout was injected.

No result file is execution authentication. The consumer checks archive consistency, exact source/pin associations, recorded process outcomes/argv, page/packet fields and independent arithmetic. It needs neither a current codec executable nor historical absolute filesystem locations; recorded paths are compared as data. An attacker able to forge an entire mutually consistent archive is outside this consistency check's claim.

## Reproduction without overwriting archives

For native reproduction, create a **new external disposable directory** and copy only `protocol.md`, `run.py`, `reader.py`, `common.py`, `consumer.py`, `test_pure.py`, and `isolation.py` into it. Inspect and explicitly approve the already-installed pinned binary/libraries before running `python run.py` in that copy. Do not run inside the archived author, reviewer or historical source directories. The runner clears a previous success summary, creates a fresh UUID directory, and preserves failures; identity mismatch blocks media. No installation is part of this procedure.

The new runner supplies only PATH/LANG/LC_ALL plus the unchanged five-key isolation helper. This is not a sandbox. On timeout, the runner attempts to terminate its own process group and performs bounded cleanup; escaped descendants are not universally contained. Preparation/cleanup failures remain visible.

Pure tests: `python test_pure.py` and `python -O test_pure.py`, preferably in the disposable copy. Static check: `python consumer.py SOURCE_ROOT EVIDENCE_UUID_DIRECTORY`; `-O` is also supported for this explicit-validation consumer. Archive reconstruction is bounded and may operate in memory; any extraction for external use should target a fresh disposable directory, not overwrite archived originals.
