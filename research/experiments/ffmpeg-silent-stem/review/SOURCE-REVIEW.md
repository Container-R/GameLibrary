# Offline amix: independent source gate review

2026-11-01 03:26 UTC. Source-only gate accepted for a finite prospective protocol, not native execution.

Gate SHA256: `077fcdc7c3ac0214e7d01914ad81192cf86c0eedfd4b308e00202502cc0df4f4`.
Existing audio article SHA256 `66ac662caaa250bbf07b770ec48595c394d5cdd42016f707656af8ec1f143abb`; PCM article `268196522d3089921347fdac87b7507df038ad793b1be30f8d1050aecfb06d30`. Their scheduling model and frame-count evidence do not establish actual multi-input gain behavior. This proposed offline export witness does not validate middleware scheduling.

## Originals independently fetched and read

All at comparison commit `3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587` via the GitHub connector:

- [af_amix.c](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/libavfilter/af_amix.c): options, calculate_scales, config_output, output_frame, request_samples, activate.
- [af_asetnsamples.c](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/libavfilter/af_asetnsamples.c): activate and n/p options.
- [avfilter.c](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/libavfilter/avfilter.c): ff_inlink_acknowledge_status and frame consumption.
- [filters.texi](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/doc/filters.texi): amix options and examples.

## Boundary reasoning and required constraints

Active flags, not zero-signal detection, select normalized weight contributions. EOF and active status may coexist while samples remain buffered. Status acknowledgement waits for upstream queued frames and remains available afterward; amix clears active status once its own FIFO is empty. With matching 256-sample frames, lengths 4096/2048 divide evenly, so the prospective transition can be fixed at sample index2048 rather than accepted in an arbitrary post-hoc window. The first-input frame list and secondary FIFO gate prevent consuming A beyond available B while B is still unclosed. p=0 avoids final artificial padding.

For positive unit weights, normalization begins at1/2. After B is inactive, dropout_transition=0 selects immediate renormalization in this source path (the positive-frame decrement divides by zero and clamps to the remaining weight); this is a finite source prediction, not a universal floating-point/platform or installed-source identity guarantee. A zero-frame path is not an output sample. If the observed output differs, preserve failure rather than changing the boundary.

Freeze A=0.5 for4096 mono f32le samples, B=0 for4096 or2048, 48kHz, explicit equal framing, duration longest, weights1/1 and dropout0. Prospective literals: full B normalized0.25 throughout; short B normalized0.25 for[0,2048),0.5 for[2048,4096); short B unnormalized0.5 throughout. Require exact output length and finite all-sample comparison; do not replace it with a mean-volume check. Protocol must declare numerical tolerance before execution.

No source claim certifies local binary/dependency correspondence, general game mixers, perceived loudness, clipping policy or a real-time callback schedule. No native/media/version call or input file generation was performed for this review. Independent literal input/output hashes will be frozen separately before author code.
