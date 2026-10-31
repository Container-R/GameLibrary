# Independent PCM loop-frame contract review

2026-10-31 19:14 UTC. Accepted finite offline evidence; no material issue. Read frozen contract before independent literal PCM oracle. Runnerf8beaf2c0a482bdf509eefce62b42a8807cde2a1f34565ed364d3f8678c2cd35; contract3addbf9e5923256ff0967a1517335d8cfc4d2dd1e03a596082b19665d4d5cbcc.

## Actual repeat and archive oracle

```
python3 research-drafts/deep-qa/music-loop-frame-contract/fixture/run.py > research-drafts/deep-qa/music-loop-frame-contract/run-output.txt 2> research-drafts/deep-qa/music-loop-frame-contract/run-stderr.txt
python3 research-drafts/deep-qa/music-loop-frame-contract/check_raw.py research-drafts/deep-qa/music-loop-frame-contract/fixture/results > research-drafts/deep-qa/music-loop-frame-contract/independent-output.json
python3 research-drafts/deep-qa/music-loop-frame-contract/negative.py > research-drafts/deep-qa/music-loop-frame-contract/negative-output.txt 2> research-drafts/deep-qa/music-loop-frame-contract/negative-stderr.txt
```
All exit0. Actual positive runner performs two offline FFmpeg filters plus two ffprobe and two version subprocesses. Its stderr empty; tool stderr retained separately. Independent checker imports no runner: constructs complete literal pre/body/tail PCM, validates all decoded bytes and unique endpoint tuples. Correct93659frames/374636bytes and offbyone93658/374632 match; latter loses intended last marker. Full source96539frames/386156PCMbytes. All three gzip/base64 archives strictly decode to actual whole-file bytes, sizes and SHA including archive bytes. Whole WAV hash is separate from decoded PCM identity. Archived checker also works with raw WAVs omitted.

Three synthetic isolated runner invocations: -O, missing-tool startup and actual nonzero /usr/bin/false replacement. All exit1 and remove prior summary; raw commands/stdout/stderr saved under negative/. No extra audio filters in these probes. Missing executable raises before per-tool status/log finalization; outer captured traceback and absence of current summary are the evidence, not a falsely recorded process exit. Subprocess timeout branch was inspected but not injected; no all-failure freshness or OS cancellation claim. Retained prior non-summary artifacts must not count as new completed run.

## Source comparison independently read

Exact FFmpeg doc/filters.texi atrim section3773–3822 at https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/doc/filters.texi#L3773-L3822 via GitHub plugin: sample end is first discarded, count-based options differ from timestamp options, atrim does not reset timestamps. Separate asetpts usage matches this fixture. Official pinned source is comparison, not authenticated local Debian build source.

FMOD2.04 current documentation accessed2026-10-31: https://www.fmod.com/docs/2.04/api/core-api-sound.html#setlooppoints and https://www.fmod.com/docs/2.04/api/core-api-common.html#fmod_timeunit . Inclusive loop endpoints, bounds/loopmode/buffer caveats, PCM versus PCM-bytes distinction support source-only mapping480..94138. No FMOD execution or installed SDK claim.

Arithmetic half-up93659 from3840000/41 is project policy, not universal middleware rounding. Artificial marker discontinuities and exact PCM success establish neither listening quality/click-free loop nor perfect long-run tempo. No device, playback, DAW export, compression/gapless, latency or actual musical transition proof.

No original/main/remote edits. Raw binary WAVs remain local; lossless text archives preserve independent run for publication without regeneration.
