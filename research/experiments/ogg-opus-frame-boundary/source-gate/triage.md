# MUSIC codec/container depth triage — no encoding or decoding executed

2026-10-31. Scope: source and installed capability inspection only. No installation, codec invocation on media, input generation, third-party assets, main-tree or remote edits.

## Actual current evidence

Read `gamelibrary-work/solutions/music/pcm-loop-frame-contract.md`, SHA256 `063bbaec9a51b2c87d3beda8fdfcf4e5debd4c2d6e5f6deefc74eb85ecf93a0c`, and its actual experiment README/contract scope under `research/experiments/music-loop-frame-contract/`.

Existing actual evidence is 48 kHz stereo PCM16 WAV, finite FFmpeg atrim extraction of 93,659 versus 93,658 frames, with exact decoded PCM byte and marker checks. FMOD endpoint mapping is source-only. The article expressly excludes encoded padding/pre-roll/gapless behavior, resampling, audible clicks and device/middleware timing. This triage does not retroactively change those exclusions.

## One recommended finite boundary

**A fresh Ogg Opus stream's final granule counter is not automatically the length or loop endpoint of the presented PCM: header pre-skip and final-page trimming matter.**

Propose one original 48 kHz stereo PCM16 input of **93,659 frames**, preserving the existing non-packet-aligned body length as a new independent input. One actual FFmpeg libopus encode into Ogg, one actual full decode to PCM at 48 kHz, plus metadata inspection. No resampling, seeking, chain concatenation or playback loop is proposed.

The planned falsifiable question: does this identified local encoder/container/decoder route return exactly the input frame count, while the encoded final granule position differs from that count by the recorded pre-skip? If so, treating the final granule position itself as the audible PCM length is a concrete wrong-count counterexample. Exact pre-skip is **not guessed** or frozen to a remembered encoder constant; it must be read from the actual original stream. Unexpected results stop the claim rather than trigger padding edits.

This establishes a counted boundary only. Lossy decoded sample values are not expected to equal original PCM; preserving length does not prove waveform phase, marker identity, seamless looping or perceived quality. Nor does length alone justify seeking to a loop point: seeking/pre-roll is a separate excluded case.

## Primary sources actually read

### S1: container standard

[IETF RFC 7845, Ogg Encapsulation for the Opus Audio Codec](https://www.rfc-editor.org/rfc/rfc7845.html), T. Terriberry, R. Lee, R. Giles, **April 2016**, accessed2026-10-31. Read §4 Granule Position, §4.2 Pre-skip, §4.3 PCM Sample Position, §4.4 End Trimming, and relevant §4.5 initial-position restrictions.

The granule unit is samples per channel at 48 kHz, not stereo channel-component count. Pre-skip removes initial decoded samples; PCM sample position subtracts pre-skip from granule position. End-of-stream granules can trim the last packet. A stream may start at a nonzero PCM position, so the simple final-position-as-length calculation must be restricted to this freshly generated, uncropped, non-chained stream and checked against its initial conditions. No generic Ogg parser or arbitrary stream acceptance is proposed.

### S2: encoder option contract

[FFmpeg n7.1.5 comparison source, doc/encoders.texi, libopus](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/doc/encoders.texi#L969-L1064), accessed2026-10-31. Read wrapper identity and option mapping, particularly application, frame_duration, bitrate/VBR and mapping_family. This supports selecting explicit audio application, 20 ms frame duration and stereo mapping family0 for a future protocol. It does not authenticate the local Debian binary's exact source or predict its pre-skip.

**Preserved discrepancy:** this pinned documentation lists frame durations through60 ms, whereas installed encoder help advertises up to120 ms. Proposed20 ms is in both; no version-equivalence or full option-support inference is made.

No rate/latency/quality benchmark is derived from these documents. No source graphics or code copied.

## Actual installed capability inspection

Read-only commands (saved stdout/stderr):
- `command -v ffmpeg ffprobe`
- `ffmpeg -version`; `ffprobe -version`
- `ffmpeg -hide_banner -encoders` (discovery showed libopus)
- `ffmpeg -hide_banner -h encoder=libopus`
- `ffmpeg -hide_banner -h muxer=opus`
- `sha256sum /usr/bin/ffmpeg /usr/bin/ffprobe`

`capability.stdout` contains a combined repeat of version/help/path/hash inspection, not media processing. `capability.stderr` retains actual stderr. Installed help reports libopus encoder supports48 kHz and s16/flt; opus muxer is Ogg Opus. Both executables self-report `7.1.5-0+deb13u1`.

- `/usr/bin/ffmpeg` SHA256 `e8a8d46f5225f3062cec7c07fb145d58ae73c603cb740dcd5bad34bfb54e455a`
- `/usr/bin/ffprobe` SHA256 `cefc5f81c0b18429cdbf8fa5a89e1e9c759235e10f93f9b329ff1b2fdff26f46`

These commands show exposed capability, not successful encoding/decoding. Native library dependency identities still need recording if execution is approved; no installation is required by the observed tool listings.

## Proposed next gate, before code

Freeze one input, exact frame/channel/byte units and encoder options; define a small bounds-checked reader only for the generated single-stream Ogg layout (header pre-skip, page granules/flags, packet boundaries), not a replacement codec. Read the remaining official header/page-layout requirements before implementing that reader. Compare actual decoded frame count to93,659 and actual final granule minus pre-skip; require actual pre-skip positive to substantiate this particular counterexample, otherwise report it was not established. Record last-page trim evidence rather than deriving sample count from file bytes or assuming all packet durations are20 ms just because the option requested it.

Preserve input/encoded/output byte identities and exact commands, statuses, raw tool logs, source/tool/library hashes. A fresh isolated evidence directory should reject failures without leaving a stale PASS. Archive original small files losslessly or gzip+base64 if suitable; compressed size is not a real-music compression claim. Independent rerun would use the same installed codec and must be labeled accordingly.

**Decision:** feasible enough to proceed to a frozen protocol, not yet authorized as an executed fixture. It adds an actual codec/container boundary missing from the PCM-only article without asserting packet count equals output count. If framing observation cannot be validated safely, stop at source-only rather than invent a toy codec or loosen the intended oracle. No MP3/AAC/FMOD/Unity behavior, resampling, random access, hardware output, playback latency or listening-quality conclusion follows.
