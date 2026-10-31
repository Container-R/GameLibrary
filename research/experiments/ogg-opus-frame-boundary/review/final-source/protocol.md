# Frozen candidate protocol: Ogg Opus frame-count boundary

2026-10-31. **Draft pending review acceptance; no implementation, input generation, encoding or decoding has run.** Source gate: `research-drafts/music-codec-depth-gate/reader-source-gate.md` SHA256 `84704f7af4ffee144d08283a61d1665363bdfe51fbb2d0dc2a1c14c965de906b`. If accepted, retain these bytes and record approval separately.

## Purpose and counts

One generated original PCM input, one Ogg Opus encode and one full decode with the already-installed FFmpeg. Exactly **one version-query process + one encode process + one decode process** in the successful author sequence. No ffprobe media process, no playback, no seek, no chaining, no resampling experiment. Independent review may later repeat the same finite sequence in a separate directory; not counted as new formats or inputs.

Two prospective counterexamples must both be established:
1. Final granule counter alone overcounts presented frames because actual header pre-skip is positive.
2. Sum of actual packet frame durations, even after subtracting pre-skip, overcounts presented frames because final-page tail trim is positive.

If the emitted stream is outside the limited reader subset, has zero pre-skip or zero tail trim, or any declared oracle fails, preserve evidence and classify FAIL / NOT_ESTABLISHED. Do not widen the subset or change the input/options to obtain a passing counterexample without new approval.

## Exact original input, frozen before code

- Raw interleaved signed little-endian PCM16, 48,000 frames/second, two channels in L/R order.
- N = **93,659** frames; two signed16 components per frame; four bytes/frame; exact input length **374,636 bytes**.
- For integer i in [0,93659), generate:
  - L(i) = ((i mod 96) - 48) × 128.
  - R(i) = ((i mod 80) - 40) × 96.
- No floating-point tone generator, random source, external sample, dither added by our generator, preamble or appended padding. These bounded integer sawtooth-like numerical signals are not musical material or listening-test stimuli.
- Literal endpoints: frame0 = (-6144,-3840); frame93658: L=((58)-48)×128=1280, R=((58)-40)×96=1728. The full original PCM must be independently checked against the integer formula before encoding. Lossy decoded samples are **not** compared for equality with these endpoints or input bytes.

## Exact command templates

BINARY is resolved `/usr/bin/ffmpeg`; INPUT/ENCODED/DECODED are absolute paths in a fresh owned invocation directory. No preexisting output reuse. Record actual argv, process start/return, statuses and streams.

```text
BINARY -version
BINARY -hide_banner -loglevel error -nostdin -y -f s16le -ar 48000 -ac 2 -i INPUT -map 0:a:0 -c:a libopus -application audio -frame_duration 20 -b:a 96000 -vbr off -mapping_family 0 -f opus ENCODED
BINARY -hide_banner -loglevel error -nostdin -y -i ENCODED -map 0:a:0 -c:a pcm_s16le -ar 48000 -ac 2 -f s16le DECODED
```

No input cropping, atrim, timestamp shifting or manual edit to the encoded stream. Same requested input/output rate; this does not claim inspection of codec-internal sample-rate operations. Default Ogg page aggregation is recorded via actual output; exact serial, page count, pre-skip, packet count and decoded bytes are not guessed.

## Restricted generated-stream reader

Original stdlib implementation, not a codec or general validator. Limits: encoded file <=1 MiB; <=1024 pages and <=1024 packets; each length checked against remaining input before slicing/allocating. Unsupported-valid layouts must be distinguished in error wording from malformed structure.

1. Sequential exact page offsets. Require complete27-byte base header, OggS/version0, complete lacing/body, no unknown flag bits or trailing bytes. Single serial; sequence starts0 and increments without wrapping for this small file. Only first page has BOS; only final page has EOS; no data after EOS.
2. Every page CRC: direct polynomial0x04c11db7, init0/finalxor0, checksum bytes22..25 zero while computing over full page. Store original/computed CRC and page bounds. This is not authentication.
3. Reassemble Ogg packets using lacing.255 means continued; <255 completes, including zero terminator. Continuation flag must equal whether previous page left a pending packet. No pending packet at EOS/EOF. Record actual continuation occurrences; absence does not prove live continuation coverage. Parse granules as signed64: only -1 is allowed as a negative value. Page with no completed packet must carry -1 granule; completed header pages require0. Completed audio granules cannot exceed cumulative accepted packet durations; track previous completed-audio-page granule separately from intervening continuation/no-completion pages.
4. OpusHead alone on BOS page0, complete on that page and consuming all its payload with no second packet or pending tail; require exactly19 bytes, magic, version1, outputchannels2, inputrate48000, gain0, mappingfamily0. Pre-skip is actual little-endian unsigned16 and **must be positive**; no fixed expected312 or guessed codec delay.
5. Second packet OpusTags starts on page1: check magic and vendor/comment little-endian lengths within bounded packet; bound declared comment count to <=1024 and to remaining bytes/4 before iterating or allocating; completion must end its header page before any audio. Tags may span pages if structurally valid; record trailing padding byte count and ignore those permitted bytes, without a Vorbis framing-bit requirement or interpreting gain comments as new audio. No other header packets or multiplexing.
6. Audio packet subset: TOC code0 only, one nonempty frame with <=1275 payload bytes. A zero-length frame payload can be valid Opus but is **unsupported by this fixture**, not universally malformed. Other count codes also unsupported. Derive frame duration from actual RFC6716 Table2 config; require every audio packet has20 ms =960 frames at48 kHz, namely actual config in {1,5,9,13,15,19,23,27,31}. Do not require the TOC stereo bit to match outputchannels2; encoded channel mode can vary.
7. First completed audio page must not be EOS, and its granule must equal cumulative durations of audio packets completed so far. This independently anchors initial granule offset0. Every subsequent non-EOS completed audio page must likewise equal cumulative frames. No arbitrary initial-offset assumption from the file's name.
8. Final page has at least one completed audio packet, no unfinished packet, and final granule G >= previous completed audio granule, G >= pre-skip P. Require tail trim T = total audio-packet frames D - G, with **0 < T <=960**. The upper limit is our bounded subset restriction; RFC7845 states SHOULD, not universal MUST. Require P>0, G-P=N, and actual decoded byte count/4=N exactly, without duration-float rounding. Require decoded length divisible by4 and nonempty.
9. Explicit wrong-count arithmetic: G != N and G-N=P; D-P != N and (D-P)-N=T; D != N. Only use these after page/packet/origin checks. Do not infer loop point compatibility or waveform correctness.

## Receipt, failure and identity contract

- Source manifest includes protocol.md, run.py, reader.py, input generator if separate, and exact copied isolation.py. Use current five-key helper SHA256 `bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970`, without altering any historical runner or fresh-harness adapter.
- Each invocation creates a unique UUID evidence directory. Clear any top-level prior success pointer/summary before optimized-mode rejection and nonstdlib/local imports. `python -O` rejects before tool entry. Do not log full inherited environment or secrets; record five selected locations only.
- 20-second timeout per process. Attempt record flushed before spawn; exit/status after return. Preserve stdout/stderr bytes including timeout partial output, exit code or launch exception. Nonzero/timeout/launch failure blocks PASS. Version output is retained verbatim; encode/decode expect empty stdout/stderr with the specified error logging. Any extra diagnostics fail closed, rather than silently discarding warnings.
- Compare source/tool/selected library hashes before and after execution. FFmpeg expected SHA `e8a8d46f5225f3062cec7c07fb145d58ae73c603cb740dcd5bad34bfb54e455a`; self-report expected prefix7.1.5-0+deb13u1, full version log retained. Shared library identities are the five actual paths/hashes in reader-source-gate.md; mismatch stops before media processing. Record loader-resolution output separately; local hashes do not authenticate exact upstream source or all loaded code.
- Record original input, encoded and decoded file sizes/hashes; complete parsed page/packet/header metadata and literal count comparisons; commands attempted/succeeded separately. Success receipt only after all declared checks and unchanged identities. Failure receipt retains partial artifacts, never reuses old PASS.
- Archive exact original binaries using deterministic gzip plus strict base64, split into <=64 KiB text chunks if needed; manifest records each chunk hash and reconstructed original hash/length. Decoding archive for static verification only into fresh disposable paths. Compression ratio is not a real-music claim.
- Add a static consumer that checks source/output manifest association, raw execution statuses and independent literal count identities before accepting the recorded PASS. It must reject a FAIL/partial receipt and not need a current codec invocation. No synthetic parser negative is counted as an encode/decode run.

## Sources and limitations

RFC7845 §§3–5.2; RFC3533 §§5–6 (Informational); Xiph Ogg framing/checksum; RFC6716 §3.1/Table2/§3.2.2; fixed FFmpeg doc/encoders.texi libopus section at commit3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587. Source gate records actual reads and local library lookup limitations.

No PCM waveform equality after lossy coding, audible seam/click, game-engine import, FMOD/Wwise behavior, seeking/pre-roll, resampling accuracy, live/network transport, full format conformance, device timing, universal gapless support or performance claim. One successfully counted decoded stream is not an independently authenticated encoder implementation.
