# Independent Ogg Opus finite sequence acceptance

2026-10-31 23:27 UTC. Coordinator authorized one independent sequence at23:26:50. Before launch, checked author's actual receipt with its static consumer and compared every copied source byte to the current frozen author source; all matched. Executed only copied `final-source/run.py` once. No retry, extra media query, seek or changed input/options.

Author UUID: `2a1a6a1b-8731-4540-ac7d-f5ada6ec49ab`.
Independent UUID: **`1c7b7ced-e93e-44b8-bca0-ce7b8650a1ab`**, under `final-source/evidence/`.

Each sequence observed three processes: one version query, one encode, one decode, all returned0. Media stdout/stderr were empty; no timeout was observed. Combined author/reviewer count is six tool processes, comprising two version queries and four media operations. This is a same-installed-codec repeat, not an alternative codec implementation test or additional musical input.

Independent literal observed-count reader `check_observation.py` imports no author parser/consumer and invokes no codec. It reconstructs packets from actual lacing, obtains pre-skip from original OpusHead, derives code0 duration using RFC configuration groups, checks the first audio-page origin, and verifies original PCM formula, decoded bytes and two count differences. It checked both author and reviewer archives:

| Quantity | Both observations |
|---|---:|
| pages |4|
| completed audio packets |98|
| actual continuation pages |0|
| pre-skip P |312|
| final granule G |93971|
| total packet frames D |94080|
| tail trim D-G |109|
| decoded bytes |374636|
| presented frames G-P |93659|

Thus G alone overcounts by312; D-P overcounts by109. These values were read/derived after the frozen positive-pre-skip/positive-trim checks, not presumed encoder constants. Packet/frame units are per-channel frames at48kHz, not interleaved component counts. No waveform-equality assertion was made.

Raw parent stdout/stderr/exit are preserved as `native-parent.*`; original process logs, parsed metadata, source/tool/library before-after hashes, media hashes and lossless archive chunks remain under each UUID. `reviewer-independent-check.json` / `author-independent-check.json` record the separate literal checks. The reviewed author consumer additionally verifies CRC, complete bounded header/comment/page/packet metadata, exact source and selected identity pins; its static checks pass normal and optimized Python for the reviewer archive. The independent count reader complements that check; it is not claimed to independently reimplement every CRC or header-policy validation.

Static reproduction from this directory (no native processing):

```sh
python -B check_observation.py final-source/evidence/1c7b7ced-e93e-44b8-bca0-ce7b8650a1ab
python -B final-source/consumer.py final-source final-source/evidence/1c7b7ced-e93e-44b8-bca0-ce7b8650a1ab
```

The independent reader can use archived base64/gzip chunks when original binary files are omitted from public packaging. Original binary/decoded hashes are identities, not claims of cross-run encoded-file equality or lossy sample preservation. Both runs use the same installed libraries; local hashes do not authenticate upstream source or complete dependency closure.

No continuation occurred natively: only earlier synthetic framing tests exercised it. No native timeout, crash, malformed media or arbitrary-stream conformance coverage was added. Existing PCM-only work remains separate. Accepted result supports a narrow container/decode frame-count supplement, not seamless playback, perceptual quality, random access, pre-roll, game-engine import, resampling accuracy or universal gapless behavior. No remaining material blocker for that scope.
