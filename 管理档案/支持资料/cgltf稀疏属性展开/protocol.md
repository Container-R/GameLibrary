# Public two-fixture cgltf protocol derivative — NOT EXECUTED AS THIS ARTIFACT

Public derivative prepared 2026-11-02 from an earlier pre-execution protocol. Local preparation observations have been omitted. This public protocol and its regenerated manifest were not the documents used in the two recorded executions; the original records remain unchanged. Source, harness, runner, fixture bytes, literal expectations and technical steps below are unchanged. Any future execution of this public derivative is a new execution, not a reconstruction of a private original receipt. No installation, engine, GPU, mesh import, private data, network, arbitrary file URI, malformed input, performance or security certification.

## Source and environment gate

cgltf v1.15 tag object bbeb5b0b070ddacddac6852fb72143eb68454937 resolves to commit 360db1a95480fe102ae9c69b27c5d101167ff5ba. cgltf.h and LICENSE are fixed upstream copies; MIT notices retained. Header source: https://github.com/jkuhlmann/cgltf/blob/360db1a95480fe102ae9c69b27c5d101167ff5ba/cgltf.h . No upstream source modification is intended; local file hashes identify the exact bytes compiled.

Runner uses cc with -std=c99 -O0 -Wall -Wextra -pedantic; if unavailable stop, never install. Harness checks 8-bit bytes, little endian and 32-bit binary float representation, not arbitrary architecture support.

## Public input identity and independent expectations

fixture.hex is the original 44 bytes, serialized into the exact data URI in both JSON files. Both have one buffer, three views, one FLOAT SCALAR count4 sparse accessor, sparse count2; no extensions, mesh or animation. No byteStride is present.

- base view offset0 length16: float10/20/30/40 at0/4/8/12.
- sparse indices view offset16 length8, local offset2: uint16 1/3 at18/20.
- sparse values view offset24 length20, local offset4: float7/9 at28/32.
- dense.json has accessor bufferView0 and byteOffset0: literal expected [10,7,30,9].
- zero.json omits both fields: literal expected [0,7,0,9], despite unused dense bytes remaining in the same buffer.

These expected arrays are specified before native execution, not calculated using cgltf or the old Python reader. Replacement is not addition; [10,27,30,49] is not accepted. All values are exactly representable; equality is exact and no after-the-fact tolerance is allowed.

## Gates and API order

Runner checks all public manifest hashes before compiling/copying inputs. The public manifest identifies the distributed derivative, not the original execution protocol. This exact-byte whitelist is the full-document metadata/URI whitelist; the harness additionally checks relevant parsed structure fields explicitly. Unknown JSON keys cannot pass the package hash gate. Do not treat the standalone harness as a safe arbitrary-asset loader.

Harness parses only dense.json and zero.json in a clean work directory. It checks counts, accessor type/stride/base/sparse references, exact view offsets/sizes, absent prohibited asset groups/extensions and exact self-authored URI before load_buffers. Then exact loaded bytes are compared against the fixed44-byte literal. These checks establish spans, independent offsets/alignment, tightly packed stride4 and increasing in-range indices before validate or unpack. cgltf_validate alone is not a memory-safety or full-conformance boundary.

For each input: parse success; load_buffers success; validate success; unpack_floats(NULL,0) returns4; actual unpack with full4-float output returns4 and equals its literal array. cgltf_accessor_read_float on the same valid sparse accessor must return false; the output from that failed call is never consumed. This is an API capability observation, not another malformed input or another geometry case. Free parsed data on success/failure.

No partial-capacity output probe: the pinned sparse write loop does not use a truncated float_count as destination bound. No interleaved dense base: sparse values advance by accessor.stride in this version. Neither behavior is exercised as a defect test. No duplicate/out-of-order index, short-view or old negative probes are transferred.

## Bounded execution and evidence partition

Invocation after authorization: `python3 -B run.py NEW_RUN_DIRECTORY`. The parent directory must exist; the run directory must not exist. Refuse reused directories rather than clearing or reusing a former PASS. Each attempt has fresh private-raw/work, HOME, TMP/TEMP/TMPDIR and XDG config/cache/data/state/runtime directories. Child environment is an explicit PATH/locale/timezone/home/temp whitelist; no inherited credentials, compiler flags, loader variables or private profile settings. No shell is used.

Compile timeout30seconds; native timeout5seconds. A subprocess timeout/nonzero exit stops the success path; stdout/stderr and actual return or timeout remain in private-raw. No old summary/binary can supply success. Exact allowlisted harness stdout and empty native stderr are required. Compiler warnings, if any, remain raw and should be reviewed separately even if compilation exits0.

`private-raw/` is local-only: raw compiler/native stdout/stderr, runner errors, work binary, temporary directories. Do not upload it or binary hashes, PID, hostname, absolute runtime paths, environment dumps, compiler discovery output or private machine fingerprints.

For a future new execution, `public-safe/` contains a result record of fixed input/source/protocol/harness/runner/manifest hashes, compile options, stage exit statuses, and (only on success) exact technical output with its hash. It is still subject to a separate public payload/privacy review; successful execution alone does not authorize publication. Failure exception text stays raw, not in public-safe.

An independent reviewer must inspect package files and their identities before any new execution, then independently inspect its actual receipts afterward; static syntax or hash checks are not native runs. Any unexpected result stops and preserves the attempt. Changes require an explicit revised manifest/protocol and a new run directory, with prior failed records retained.
