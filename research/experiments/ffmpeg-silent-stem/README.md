# Offline silent-stem normalization: finite observed evidence

An unchanged +0.5 stem was mixed with an all-zero stem. With normalization enabled, ending the zero stem changed the surviving stem's gain; keeping zero samples present did not. These are complete offline PCM observations, **not listening tests, middleware lifecycle tests, device measurements or proof of a player's experience**.

## Observed finite results

All inputs were original literal mono IEEE754 f32le bytes at 48,000 Hz. A contained 4096 samples of +0.5; B contained either 4096 or 2048 zero samples. Both input filters used `asetnsamples=n=256:p=0`; amix used equal weights, longest duration and zero dropout transition. Every output contained exactly 4096 frames / 16384 bytes; all bytes and all finite samples were checked, not only averages or selected windows.

| Configuration | Samples [0, 2048) | Samples [2048, 4096) |
|---|---:|---:|
| Full-length B, normalized | +0.25 | +0.25 |
| Short B, normalized | +0.25 | +0.5 |
| Short B, unscaled | +0.5 | +0.5 |

The index-2048 boundary and complete sequences matched the frozen prospective oracle without tolerance, excluded windows, retries or changed parameters. This does not reveal internal AVFrame boundaries directly, establish arbitrary mixing bit reproducibility, or recommend disabling normalization without a separate headroom policy.

## Author and independent runs

- Author UUID: `0522fc0d-998a-489a-ba2d-05a8418dabd2`; receipt SHA256 `67991e9951053ccc0d5cd8b62f7c024bb574e98d288d679e016ddc4a39db742e`. One normal runner invocation, exit 0; one separately recorded read-only consumer invocation, exit 0.
- Independent repeat UUID: `59a5d8a4-39ef-448f-8771-622108e7b86c`; receipt SHA256 `7b2d14f96f3f4899b2d8ff0e8b18721e415f4e4f573ef03c38405745a7e8402b`. Separate fresh copy and authorization; no source or expectation changes.
- Each run performed one version query and three mixes. **Total: two version queries plus six mixes, repeating the same three unique configurations.** Both recorded all four processes returned successfully; no native timeout/cleanup branch was exercised.
- The reviewer froze a standard-library-only checker before native execution, accepted the author's evidence before the repeat, then accepted the repeat. It imports no author output checker. Same installed binary/platform repetition is not an independent mixer implementation.

The frozen six-source manifest is `e830cfff7cbae792af06a6cdbba4e0a6a16e73fc66978328a1adbc046fd9540c`. The independent literal oracle hash is `a904ecc7a41cbc9338f0b1ee8f48ecc046835a0792d67815e3bff9c039c36f2b`; independent checker hash is `11d5163dd3e2a9c10406757553df0938a7e87e1b10b9a4a284cb116a349bfbde`.

Public archive layout uses the pinned sources plus author evidence at the top level, independent repetition under `review/native-repeat/`, and independent checker/oracle/acceptance files under `review/`. Local preparation keeps author evidence in the separate sibling `ffmpeg-silent-stem-author-run/` and review evidence in `deep-qa/audio-mix/`; those paths are not extra native runs.

## Pre-native corrections and pure tests

Initial manifest `82a94e31...`, original source files and six-method test outputs are preserved under `history/pre-failure-finalization/`. Main review identified missing best-effort post-failure file identities and portable partial-output archives. It also reproduced a timestamp-contract defect: a synthetic receipt with non-UTC offsets remained accepted. These were metadata/failure-path defects, not failed FFmpeg waveforms.

Before any native call, the runner gained failure-only finalization: capture source/tool hashes and any existing partial input/output bytes as reversible hex, or explicit unavailable/error records, while preserving the original exception and never continuing to another case. The consumer now requires string timestamps with UTC offset zero. Main's same finite non-UTC probe was rejected after the correction. No protocol, input or waveform expectation changed.

Final author pure suites passed **seven unittest methods under normal Python and seven under `-O`**. Reviewer copied-source suites separately passed the same seven methods in each mode. Each suite includes two Python-only guarded-startup children, not native mixing cases. The initial six-method history is not added to those final counts. The independent checker additionally passed one synthetic valid control and eight malformed-receipt rejects under normal and optimized Python: shifted boundary with rebound hash, non-UTC timestamps, bool returncode, unexpected timeout flag, injected environment, wrong selected library, missing process, and nonempty stderr with rebound hash. These finite static probes are not an execution authenticity or general security proof.

## Implementation and archival boundaries

- `signals.py` generates original literal inputs and checks the entire output waveform.
- `consumer.py` independently reconstructs the protocol bytes without importing `signals` or the runner. Strict JSON rejects duplicate keys/nonfinite numbers; recursive exact-type comparisons reject bool/number substitutions.
- `run.py` clears old PASS before local imports/optimized guard, checks frozen pins, creates a UUID receipt and launches at most four sequential child processes, each with its own five-key owned environment. Each has a 20-second timeout and bounded process-group cleanup attempt. Successful observations do not test timeout handling.
- `isolation.py` is unchanged helper `bcade741...`; selected HOME/XDG/TMP locations are not a sandbox or complete loader isolation.
- Full input/output lowercase hex, raw logs, receipts and source manifests are retained. Local `.f32le` files may be omitted from text-only publication because complete bytes reconstruct exactly; if binaries remain, the consumer also compares them to the archives.

Selected `/usr/bin/ffmpeg` and `libavfilter.so.10` file hashes are recorded before/after; one version query per invocation records the tool self-report. They do not authenticate the full dynamic dependency graph, official release provenance or correspondence to public comparison source commit `3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587`.

## Safe reproduction

Never run an archived historical directory in place. Copy only the six pinned source files, `SOURCE-SHA256.json` and this README into a fresh writable directory, leaving historical evidence, summaries and logs untouched. After obtaining the relevant execution authorization, run `python -B run.py` once there and capture outer stdout/stderr/exit. A PASS can be checked read-only with `python -B consumer.py <directory>`. The portable consumer and independent checker do not invoke FFmpeg. A changed pin, unavailable filter, timeout or different waveform must remain a failure—not a reason for an unreviewed retry, extra native probe or adjusted oracle.
