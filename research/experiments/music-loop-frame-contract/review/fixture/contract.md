# Frozen original PCM interval contract — 2026-10-31

Before implementation: sample rate48000Hz,2channels,signed16-bit little-endian PCM. A sample frame contains one L and one R component;4bytes/frame.123BPM explicitly quarter-note beat,4/4,onebar. Idealbar frames3,840,000/41; nearest integer half-up policy yields93659. This is project fixture policy,not a middleware standard or sample-exact infinite tempo.

Frame intervals halfopen: pre[0,480),body[480,94139),tail[94139,96539). Total96539frames,386156PCMbytes. Body93659frames,374636PCMbytes. Correct FFmpeg atrim start_sample480,end_sample94139. Deliberate offbyone end_sample94138 yields93658frames,374632bytes. FMOD2.04 source-only inclusive mapping would use480..94138; no FMOD invocation.

Marker tuples (L,R), integers exact: pre constant(-111,111);body default(100,-100); body first frame480=(1234,-2345); body last frame94138=(3456,-4567);tail constant(222,-222). First and last body markers unique. Offbyone's finalframe is(100,-100),not the intended lastmarker. These artificial numerical values are not a music/perceptual quality test and will not be played.

One original WAV, two actual FFmpeg extracted WAVs. Compare all decoded output PCM bytes against independent literal body construction,not only duration/samplemetadata. Save actual commands, exits,stdout/stderr,tool/version/hash. RawWAVs localonly; lossless gzip(mtime0)+base64 textarchives and originaldecoded SHA/size. Externaltool output WAVheader need not be byte-identical to originalgenerator; compare PCM and separately archive actual wholefiles.

Scope: finite offline PCM filtering only,no device,GPU,DAWexport,middlewareloop,click,latency,codecquality,gaplessclaim. Sourcegate music-timing-gate/gate.md. Original sources FMOD2.04 Sound::setLoopPoints and FMOD_TIMEUNIT; official FFmpeg n7.1.5 atrim docs, pin recorded separately.
