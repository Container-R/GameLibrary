# Matrix layout handoff: same byte count/stride, different major order

2026-10-31. Two actual CPU compiler processes succeeded on first execution, with zero compiler status/errors/warnings and empty diagnostic strings. The original GLSL sources differ only in explicit row_major versus column_major. No shader was run on a GPU or CPU interpreter.

## Frozen question and result

contract.json was written and hashed before code/compilation: `00ed61e278ef0411640e162a3b49059f702816a306f9797ca43784dede996b75`. Logical matrix rows are (1,2,3), (4,5,6), (7,8,10); vector is (1,2,3). Sources consume Params.transform via matrix-times-vector into a storage output, preventing an unused declaration from being our only witness.

| Actual compiler output | Row case | Column case |
|---|---|---|
| Intended named block/member | Params.transform | Params.transform |
| Member decoration | RowMajor | ColMajor |
| Offset | 0 | 0 |
| MatrixStride | 16 | 16 |
| Logical type | 3 columns of 3 float32 components | same |
| CPU host record used in this finite model | 48 bytes | 48 bytes |

Both actual assemblies contain OpMatrixTimesVector and the same logical matrix type. Correct corresponding padded host encodings recover the intended matrix and CPU arithmetic product (14,32,53). Sending the row-grouped bytes but interpreting them according to ColMajor yields the transpose and CPU arithmetic product (30,36,45), despite being in-bounds with matching byte count/stride. Padding99 is intentionally not a matrix element. These products are **CPU interpretation/oracle results, not observed shader output**. The compiler evidence is actual emitted decorations/type/operation only.

The byte records are little-endian IEEE float32 in the Python fixture. That declared offline encoding is not a portable host ABI recommendation or a demonstrated Vulkan upload. Matrix storage major order and whether an application chooses row-vector or column-vector algebra are different contracts; changing a storage qualifier does not by itself ask GLSL to transpose the logical matrix operation.

## Reproduce

`python3 run.py` requires the already-installed `/lib/x86_64-linux-gnu/libshaderc.so.1`. No packages, assets or headers are downloaded. The parent uses two separate Python child processes, each making one original GLSL-to-SPIR-V assembly compilation. Twenty-second timeout, stdout/stderr and exit receipts retained. Compile source and all live runner sources are hashed in summary. run-output.txt / run-stderr.txt retain the actual author invocation (exit0, empty stderr). SOURCE-FREEZE.sha256 identifies source before first execution.

results/ contains full RESULT_JSON stdout, parsed result JSON, assembly text, 48-byte host records as lossless hex, per-process command/status and summary. invocation.json ties the current invocation ID/state to summary; cleanup precedes the optimization guard and native load. No PASS summary after the handled failure paths. Old case files can persist after an early failure and are not a current successful run. Interpreter parse/startup, permission errors and arbitrary process interruption are not transactionally covered.

The reader resolves OpName Params and member transform, then checks that exact member's decorations and chained float/vector/matrix type. It is intentionally not a general SPIR-V parser/validator. No standalone spirv-val, spirv-cross, glslangValidator or glslc was available in the bounded capability search; this does not claim the emitted module received independent validation.

## Native ABI and identity

compile_case.py binds every called function with explicit argtypes/restype, no varargs or callbacks: opaque handles void*, enums int, source length/result length size_t, environment version uint32, byte pointer void* copied using returned length. Fixed source/case names only, output length capped before copying; null handles/status/errors checked; compiler options/results/compiler released in finally. Status failure is retained in RESULT_JSON before child failure. Explicit target Vulkan1.0 (environment0/version1<<22), SPIR-V1.0 (0x10000), compute kind2, optimization zero0. No HLSL or extension negotiation.

Library SHA256 `31400b359d2f4b4a43168978412a72913474725befb87966068cfac1922ac6c9`. shaderc_get_spv_version reports production-version capability 0x10600 revision1; the actual emitted assembly says SPIR-V1.0 because that target was explicitly set. Do not mistake this query for shaderc package version. The library's exact release/build origin is unknown; assembly generator text “Google Shaderc over Glslang; 11” is also self-report, not authenticated provenance. The pinned v2025.2 header below establishes the inspected API contract, not matching exact binary source. Python/platform and actual library hash are recorded.

## Primary sources read

Accessed 2026-10-31:

- [GLSL variables](https://github.com/KhronosGroup/GLSL/blob/0099bf83b0288469917fc2e2972cb0a2b74d6711/chapters/variables.adoc#L5004-L5031): layout qualifiers, row/column contiguous storage. Commit 0099bf83… resolved main, dated2026-09-11.
- [Vulkan memory layout](https://github.com/KhronosGroup/Vulkan-Docs/blob/b94f8bd2d004d2949469d8a5071ee10eb7d23566/chapters/interfaces.adoc#L1844-L1928): equivalent vector arrays and base/extended alignments. [Uniform alignment and stride requirements](https://github.com/KhronosGroup/Vulkan-Docs/blob/b94f8bd2d004d2949469d8a5071ee10eb7d23566/chapters/interfaces.adoc#L1978-L2010), with feature qualifications; not a universal statement that all UBO layouts are std140. Commit dated2026-10-30.
- [shaderc v2025.2 header](https://github.com/google/shaderc/blob/3362e24c42ab5bf7ad32c0fec64b0a0ddeb2fda1/libshaderc/include/shaderc/shaderc.h): kinds36–48, optimization100+, initialize/release268+, options target400–411, compile532–545, result574–606. [env.h](https://github.com/google/shaderc/blob/3362e24c42ab5bf7ad32c0fec64b0a0ddeb2fda1/libshaderc/include/shaderc/env.h): Vulkan target/environment and SPIR-V enum values. Tag commit dated2025-04-23.

Only original source/fixture and short evidence descriptions archived, not third-party implementation code. Source-pins.json records extracted tag/commit metadata from gate.

## Limits and next acceptance

Independent review accepted in [review/REVIEW.md](review/REVIEW.md): a fresh copy repeated the two actual compiler calls, independently checked literal assembly/type/host bytes/products, and rejected three seeded-PASS synthetic startup failures (-O, missing library, malformed result). Those negatives made no native compilation calls and are not additional shader cases. Same-library repeat is not an independent compiler implementation. Two compiler cases and one CPU wrong-interpretation counterexample, not three executed shaders. No GPU device, driver, buffer upload/binding, shader dispatch, rendered artifact, performance, latency, cross-platform float result, generic reflection, arbitrary nested matrices/arrays, or vendor compiler comparison. Compiler success alone does not establish the host-to-device ABI. The new evidence is actual compiler-produced interface decorations tied to an independently stated mathematical intent; existing texture byte budgets and mesh accessor proofs do not supply this compiler witness.
