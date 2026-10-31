# Public archive layout

Author and independent reviewer original WAVs are preserved losslessly as `.wav.gz.base64`; decoded whole-file size/SHA and PCM checks remain separately recorded. Raw binary `.wav` duplicates are omitted. No third-party music is included.

Negative probes copied prior successful fixture artifacts to test stale-summary handling. Public negative directories retain captured outer stdout/stderr and observations, not redundant copied old artifacts or generated mutated runners; `review/negative.py` preserves the mutations and can regenerate them from `review/fixture` in a fresh scratch copy after removing the archived `review/negative` directory there. Never remove historical evidence in-place. Old non-summary outputs in these probes are not new successful results. Missing executable raises before per-tool status logging; outer traceback is the actual evidence.

Review commands contain original workspace paths as execution provenance, not portable commands. For archive-only independent checking run `python3 review/check_raw.py results` and `python3 review/check_raw.py review/fixture/results` from this directory. To repeat filtering copy the fixture to fresh scratch, ensure the recorded FFmpeg/ffprobe paths and dependencies exist, then run `python3 run.py`. This overwrites that scratch results directory only. No device playback is performed.
