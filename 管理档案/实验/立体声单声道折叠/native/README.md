# Explicit mono matrix: native FFmpeg fixture

Run `probe.py` in a fresh temporary copy, as shown in the parent README, to keep the archive unchanged. Python standard library synthesizes 1-second, 48 kHz stereo PCM in a temporary directory; installed FFmpeg performs actual `pan` filters and writes result WAVs next to the copied script. No downloads, user recordings, Unity/Wwise code, or platform audio policy. Two successful runs produced byte-identical JSON, including hashes of every output WAV. Source code is sufficient to regenerate source and output.

Tones are periodic integer lookup tables, peak 4096/32768 (about −18 dBFS). Samples are rounded onto even integers and the negative half-cycle is exact integer negation, so half-sums are integral and don't depend on PCM tie rounding. An earlier development version with odd PCM values exposed half-integer rounding differences; this final fixture intentionally removes that irrelevant quantization ambiguity. The delay prepends exactly 32 zero frames to the right channel and truncates the tail to keep 48000 total frames. Metrics cover [1024,47104), strictly inside steady state and an integer number of both tone periods. Entire output samples are also compared with the explicit matrix, including onset.

Measured fold is 0.5L+0.5R, not a claim that every mono device uses that matrix:
- Identical 750 Hz L/R: peak4096, RMS2896.3395432856278, identical to one input.
- Opposite-polarity 750 Hz: interior exactly zero despite both inputs nonzero.
- Right delayed32 samples: 750 Hz (64-frame period) folds to zero inside; 1500 Hz (32-frame period) remains peak4096, RMS2896.5073795866633.
- Right-only 1500 Hz cue: left replicated to both outputs produces silence; folding then replicating produces two identical channels, each peak2048, RMS1448.2536897933317. True fold is not equivalent to selecting one channel. Replication doesn't restore information already canceled by the fold.

JSON contains filter strings, sample interval, FFmpeg version, integer sum-of-squares, RMS, peak, nonzero count, and WAV hashes. Readback asserts sample rate, channels, frame count and all sample values. Output audio is synthetic measurement material, not a listening-test result. Short fixed tones have abrupt edges; these are not polished delivery cues. Begin playback at low device volume if listening, and do not infer a universally safe sound pressure from dBFS.

Interpretation limits: 32/48000 seconds produces frequency-selective cancellation, not broadband silence for arbitrary material. Neither local pan output nor mathematical cancellation proves a player's mono accessibility setting, spatializer, speaker wiring, mobile device or game runtime uses the same route. Mono fold and channel replication are two distinct stages; assess each actual output channel rather than presuming an acoustic loudness result.
