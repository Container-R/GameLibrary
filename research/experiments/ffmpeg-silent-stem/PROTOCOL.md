# Prospective finite protocol: silent stem versus ended input in offline amix

2026-11-01 UTC. **Candidate for review, before implementation or any new FFmpeg invocation.** Original gate.md remains unchanged. This replaces its provisional seconds-based lengths, not an observed result or failed run. No generated media exists for this protocol.

## 1. Question and fixed scope

Does the disappearance of an all-zero input change another unchanged stem's normalized gain? Test one installed offline mixer, not a middleware bus, game scheduler or musical/perceptual outcome. Three configurations below, no parameter sweep, no new clipping/loudness/device/latency claim. Frame here means one PCM sample per channel; mono makes sample count equal frame count. An AVFrame is a separate block/container concept.

## 2. Source-derived boundary, before an oracle

Comparison source is FFmpeg n7.1.5 commit `3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587`. These original files were independently fetched/read, not installed-source authentication:

- [af_asetnsamples.c, activate, lines52–98](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/libavfilter/af_asetnsamples.c#L52-L98): consumes requested blocks, and `p=0` forwards without end padding. Both lengths below are multiples of256, so no short terminal block is needed. The [asetnsamples and amix documentation](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/doc/filters.texi) supplies the option contracts.
- [avfilter.c, lines1396–1410](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/libavfilter/avfilter.c#L1396-L1410): EOF acknowledgement waits for the link frame queue to empty; later calls return the remembered nonzero status. This matters because amix's internal sample FIFO is distinct from that link queue. [consume_samples, lines1469–1488](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/libavfilter/avfilter.c#L1469-L1488) can drain remaining samples at end; it does not invent an extra256 samples.
- [af_amix.c, frame list, lines91–155](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/libavfilter/af_amix.c#L91-L155) records the first input's block sizes/PTS and consumes that schedule. [output_frame, lines296–389](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/libavfilter/af_amix.c#L296-L389) waits when a still-open active input lacks the required samples, drains an EOF input's remaining FIFO, and mixes only positive sample counts. It does not emit an arbitrary silent substitute block while awaiting input.
- [activate/request_samples, lines394–515](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/libavfilter/af_amix.c#L394-L515) marks EOF separately and clears INPUT_ON only when that internal FIFO is empty. Repeated EOF acknowledgement permits this check after draining. With A first and B exactly8 or16 blocks, both contribute for the first8 or16 complete output blocks. For short B, subsequent A blocks cannot consume nonexistent B samples; after EOF/empty removal they use A alone. End policy is explicitly longest.
- [calculate_scales, lines212–242](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/libavfilter/af_amix.c#L212-L242) uses active input weights, not audio energy. Equal weights initially give reciprocal normalization2. After B removal, dropout0 drives the clamp to the remaining weight1 for a positive output block. This is a prospective reading of floating-point implementation, not a cross-platform C arithmetic theorem: zero transition has a zero denominator in the source expression, not a separate explicit branch. Any nonfinite or different actual output fails the fixed oracle; do not replace zero with an epsilon or widen the transition after running.

Thus the prospective sample boundary is **2048**, not a guessed one-second timestamp or a demuxer's default packet size. Explicit block partition reduces the scheduling ambiguity. No claim is made that the output file reveals internal AVFrame sizes; it tests the resulting complete sample sequence. Different installed behavior is a retained counterexample/capability failure, not permission to tune.

## 3. Original bytes and literal output oracle

48,000Hz, one channel, headerless IEEE754 binary32 little-endian. Generate original files by repeating literal four-byte patterns, with no encoder, resampler or external asset:

| Input | Frames | Bytes | Every frame's hex |
|---|---:|---:|---|
| A | 4096 | 16384 | `0000003f` (+0.5) |
| B-full | 4096 | 16384 | `00000000` (+0) |
| B-short | 2048 | 8192 | `00000000` (+0) |

Each input filter is `asetnsamples=n=256:p=0`. Weights are `1 1`; duration `longest`; dropout_transition `0` in all cases. No offset, time trim, looping, gain command or automatic retry.

| Configuration | B input | normalize | Expected frames0..2047 | Expected frames2048..4095 |
|---|---|---:|---|---|
| full-normalized | B-full | 1 | +0.25 | +0.25 |
| short-normalized | B-short | 1 | +0.25 | +0.5 |
| short-unscaled | B-short | 0 | +0.5 | +0.5 |

All outputs exactly4096 frames/16384 bytes. Positive0.25 is little-endian `0000803e`; positive0.5 is `0000003f`. Decode every sample and reject nonfinite values before comparisons; require **all bytes** match the literal sequence, no tolerance, summary average or selected-region-only substitute. Binary powers and zero keep this finite arithmetic exact without claiming arbitrary mix bit reproducibility. The control disabling normalization is diagnostic, not a general recommendation; larger summed signals may need a separate headroom policy.

## 4. Prospective commands and process envelope

Exactly one version query, then three sequential mixing processes, each at most20 seconds after process creation; stop first failure. No help/filter probe, ffprobe, extra encoder, playback, preflight native call or retry. A later independent identical repetition requires separate authorization.

Version argv: `/usr/bin/ffmpeg -version`. First line must identify the previously observed `ffmpeg version 7.1.5-0+deb13u1`; archive full stdout, require exit0/empty stderr. This is self-report only. A changed identity fails, not permission to replace the tool.

For each table row, substitute only B path, normalize N, and fresh output path:

```
/usr/bin/ffmpeg -hide_banner -loglevel error -nostdin -n \
  -f f32le -ar 48000 -ac 1 -i <A> \
  -f f32le -ar 48000 -ac 1 -i <B> \
  -filter_complex_threads 1 \
  -filter_complex '[0:a]asetnsamples=n=256:p=0[a];[1:a]asetnsamples=n=256:p=0[b];[a][b]amix=inputs=2:duration=longest:dropout_transition=0:weights=1 1:normalize=N[out]' \
  -map '[out]' -c:a pcm_f32le -f f32le <output>
```

The graph is one argv value, not shell evaluation; spaces in weights are literal. No output-rate override, aresample or media codec delay is intended. Each mix must return0 with empty stdout/stderr and exact output. If format/filter availability fails, retain failure and stop. All actual process attempts (including ones that fail to spawn or never return) must be distinguished from successful calls. Four prospective processes are not four unique mixing conditions.

## 5. Identity, isolation and receipt acceptance

File-only rehash on2026-11-01 before this draft, no tool execution:

- `/usr/bin/ffmpeg`: `e8a8d46f5225f3062cec7c07fb145d58ae73c603cb740dcd5bad34bfb54e455a`.
- `/lib/x86_64-linux-gnu/libavfilter.so.10` → `libavfilter.so.10.5.100`: `420fe0833b4a7062a7ed811ce854c8cbdf566979aa32657a23ffe51dbea0d053`.
- Exact reusable isolation helper: `bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970`.

Use a new UUID output directory and fresh owned per-process environment roots. Minimal base environment is exactly PATH=`/usr/bin:/bin`, LANG=`C`, LC_ALL=`C`; helper adds HOME, XDG_CACHE_HOME, XDG_CONFIG_HOME, XDG_DATA_HOME, TMPDIR. Record those selected paths and exact base values, no inherited secret dump. No sandbox/loader-closure claim: the two selected file hashes do not authenticate the whole dynamic dependency graph or correspondence with the comparison source.

Before launching anything: remove a previous current-summary pointer before optimized-mode/local-import guards; reject optimized runner invocation; require fresh output files and correct protocol/helper/source/input/binary pins. Record exact source manifest including protocol, runner, generator/validator, portable consumer, pure tests and helper; freeze it before first native call. Record source/input/tool-library hashes before and after the invocation and input hashes before/after each mix. Use strict typed JSON and reject duplicate keys/nonfinite JSON numbers.

Record UUID, process role, exact argv/cwd/environment, actual PID when available, UTC attempted/returned timestamps, return status/exit code, timeout/cleanup outcomes, raw stdout/stderr byte hashes and output hash/length. Distinguish failed spawn, returned process and unresolved cleanup; do not label an unreturned child RETURNED. UTC chronology is metadata consistency, not physical timing proof. Run children in their own process groups; on timeout attempt group termination and bounded wait, preserving partial logs and cleanup failures. No timeout branch execution is implied by the successful case.

Final PASS only after all four processes and all after-hash/output/consumer checks succeed. A child exit0 or output presence alone is not PASS. On any failure preserve raw/partial outputs and failed receipt, emit no new PASS and execute no later case. A static consumer must independently reconstruct expected input/output bytes from this table (not invoke FFmpeg or import the author's mixing oracle), verify original raw-output associations and exact manifests/UUID/commands/environment/status, and require no timeout/unresolved-cleanup flags. Receipt binding is integrity checking, not execution authenticity.

## 6. Archive and pre-native stop

Archive full input/output bytes as lowercase hex text with decoded size+SHA256; each output is32768 hex characters. Keep local binaries, but text-only publication must reconstruct exactly rather than regenerate undocumented media. Raw process logs and exact selected source files accompany receipts. No graph screenshots or upstream whole-source copies. One optional independent repetition doubles process counts, not the three unique configurations.

Implementation and pure synthetic receipt tests may begin only after protocol review. Native execution separately requires exact code acceptance and explicit authorization. A failed waveform/EOF assumption is preserved and returned to source review; no boundary exclusion window, tolerance relaxation, different lengths, filter substitution or retry. Accepted evidence would concern only this offline gain/topology handoff; existing middleware scheduling, music quality and device behavior remain untested.
