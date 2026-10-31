# Independent matrix-layout compiler review

2026-10-31. Accepted for finite compiler metadata and CPU host-interpretation scope. Read contract00ed61e278ef0411640e162a3b49059f702816a306f9797ca43784dede996b75, wrote oracle-before-run.md before reviewer compilation, copied current sources without author/main mutation.

Actual commands, all exit0:
- python3 research-drafts/deep-qa/shader-matrix-layout/fixture/run.py
- python3 research-drafts/deep-qa/shader-matrix-layout/check.py
- python3 research-drafts/deep-qa/shader-matrix-layout/negative.py

Two actual compiler child processes, one compilation each, same installed library. Raw stdout/stderr/status plus assembly and host bytes retained in fixture/results; outer/check outputs alongside. Own check imports no author reader/math. Literal named Params.transform interface/type checks establish RowMajor versus ColMajor, both Offset0/MatrixStride16/mat3 float32 and OpMatrixTimesVector. Explicit byte-offset readback checks the two48-byte little-endian buffers and CPU product14,32,53; row bytes read as columns yield30,36,45. These are CPU calculations, not shader execution results. Padding99 is excluded by the explicit offsets.

Three isolated seeded-PASS negative cases: -O parent rejection; child native-library missing path producing actual load failure; synthetic child emits malformed RESULT_JSON. All nonzero, current FAILED invocation, no success summary. Raw child/outer output preserved. Zero native compilations in negatives; neither timeout nor arbitrary filesystem interruption tested. Negative harness rejects -O itself and refuses existing output directory. Author runner clears old summary before optional work, then removes summary in handled exception path; current invocation/exit status remain required. No transactional receipt guarantee inferred.

Independently fetched pinned shaderc.h and env.h at3362e24c42ab5bf7ad32c0fec64b0a0ddeb2fda1 via GitHub plugin. Reviewed compute enum2, target-env enum0/version1<<22, SPIR-V1.0 value0x10000, compile assembly signature and result size/data/diagnostic/version-query signatures. Fixed ctypes bindings match these inspected C declarations (handles void*, size_t lengths/counts, enum ints, uint32 target version, unsigned-int output pointers); no varargs/callback ABI. Options/result/compiler lifetimes are protected by finally; bytes/diagnostics copied before result release, source remains alive across compilation. Library result version query is not a package-version claim. Header pin does not authenticate installed binary source.

Current library bytes independently hash to31400b359d2f4b4a43168978412a72913474725befb87966068cfac1922ac6c9, matching raw receipts. Version1.0 assembly target and query0x10600 are distinct. Same-library repeats are not a second compiler or driver validation. README correctly excludes GPU/CPU shader interpreter execution, uploads/bindings, standalone validator, generic reflection, nested layouts and physical rendering quality. Logical matrix algebra is distinguished from storage major order. No material blocker found.

Checker deliberately uses exact emitted textual identifiers for this frozen pair, not a generic disassembler. No claim that unchanged stride/byte count alone proves upload compatibility. Full pinned GLSL/Vulkan clauses were author/integrator source evidence; this review independently rechecked native ABI headers and actual assembly, not a new comprehensive standards audit.
