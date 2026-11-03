# cgltf v1.15 unsigned-byte sparse VEC4: pre-execution protocol

Prepared 2026-11-03. NOT EXECUTED. This is a new finite unit, not a rerun or extension of the old two-FLOAT-accessor result. Compile/native remain prohibited until main writer and independent review accept these exact inputs. One later approved invocation permits one build and, only after accepted build, one native process containing exactly three cases. Stop on first failure; no automatic retries or changes to expectations.

## Fixed source and scope

cgltf v1.15 commit `360db1a95480fe102ae9c69b27c5d101167ff5ba`, upstream header and MIT LICENSE freshly retrieved from the public GitHub fixed commit and byte-compared to the existing published copies. Header SHA256 `e378a21c084bf1f288bb799de827bb26906efb024255f1ecf1705ea13f11c6ec`; LICENSE `f619925f80ef862497aaf8e8155ef218fa6a2190055129523ca3df9119a9ba95`.

Sources: https://github.com/jkuhlmann/cgltf/blob/360db1a95480fe102ae9c69b27c5d101167ff5ba/cgltf.h and same commit LICENSE. Read component conversion, accessor_read_float, complete unpack_floats and pointer-fixup stride path. No source edits. MIT notices retained. Header fetch serialization initially appended a newline; removed exactly that added byte after comparison, not an upstream modification.

Three generic accessors, no mesh/skin/JOINTS/WEIGHTS semantic. In particular the zero-base configuration is not a claim of valid skin weights. No GPU, engine, installation, network, external URI, malicious input, partial output capacity, interleaved base or performance probe.

## Frozen input and oracle

All configurations use exactly sixteen bytes:
`ff 00 00 00 00 ff 00 00 01 00 00 00 40 bf 00 00`.
Dense VEC4 elements occupy bytes0–7; byte8 is sparse uint8 index1; bytes9–11 are zero padding; bytes12–15 replace the second VEC4 with [64,191,0,0]. Buffer views are (offset,length) (0,8),(8,1),(12,4), all stride absent. One buffer data URI embeds these bytes; one UNSIGNED_BYTE(5121), VEC4, count2 accessor with sparse count1. Sparse local offsets absent/zero. No unknown fields or groups pass the full-file hash gate.

Cases in fixed order:
1. dense-normalized.json: normalized true, base view0 and offset0. Expected [1,0,0,0,64/255,191/255,0,0].
2. zero-normalized.json: normalized true, base and accessor byteOffset omitted. Expected [0,0,0,0,64/255,191/255,0,0].
3. dense-raw.json: normalized false, base view0 and offset0. Expected [255,0,0,0,64,191,0,0].

The two fractions in cases1/2 are compared with absolute error <=1e-7 against independent double rational expressions, specified before execution. All other values compare exactly. Finite output required. Nine significant decimal digits preserve binary32 observation precision. No after-the-fact expected/tolerance modification. expected.json stores literal rational strings, not cgltf-generated output; harness and consumer separately spell their expected arrays. This author-side duplication is not independent verification.

## Real API sequence and stop conditions

For each case read bounded JSON, parse, check actual parsed counts/type/component/count/normalization/base/stride and view/sparse references, reject unrelated asset groups, verify exact data URI BEFORE load_buffers. Load and compare all16 bytes BEFORE validate. Whitelist and bytes establish index1<count2 and every accessed span; validate alone is not a general safe parser or full conformance certification.

Require parse/load/validate success; query unpack_floats(NULL,0) returns8; full eight-float unpack returns8 and matches oracle. Call read_float on sparse element0 with capacity4 and require false; never inspect that call's output. Each successful row reports observed API statuses/counts and actual eight values. False read outcome is represented after checking its actual return. Emit and flush each row before moving on. First failed check stops remaining cases, preserves earlier stdout and private failure label; no missing case is filled with invented zeros. Free owned parsed data, close input file. No artificial allocation failure test.

## Runner identity, isolation and diagnostics

Only invocation after approval: `python3 -B run.py NEW_DIRECTORY`. Explicit fixed cc command with `-std=c99 -O0 -Wall -Wextra -pedantic harness.c -o probe`; compiler absence stops without installation. No compiler version discovery or installed-binary fingerprint. Compile30seconds/native5seconds, kill whole process group including after leader exit. Cleanup has one total two-second deadline covering leader reaping and polling killpg(pgid,0): only ESRCH confirms group absence; a still-present group at the deadline, permission error or any other exception prevents PASS and is retained in private diagnostics. A successful kill or leader wait alone does not confirm group absence. group_absence_confirmed records that limited check, not proof about descendants that left the group or an operating-system sandbox. Compile must exit0 with empty stdout/stderr; any warning requires separate review, not suppression or category allowlisting. Native must exit0 with empty stderr. Consumer requires exactly three rows and exact schema, rejects duplicate keys, booleans as numbers, nonfinite values, wrong counts/order/tolerance.

Fresh directory exclusively created; no reuse, deletion or old PASS. Original manifest and all eleven input files bound; all copied to new work, checked before launch, between stages and after, including on failure. Manifest has exact file set. No mutable external oracle. No shell. Minimal PATH/locale/TZ plus eleven owned HOME/XDG/TMP locations: HOME, XDG_CONFIG_HOME, XDG_CACHE_HOME, XDG_DATA_HOME, XDG_STATE_HOME, XDG_RUNTIME_DIR, XDG_CONFIG_DIRS, XDG_DATA_DIRS, TMPDIR, TMP, TEMP. Each absolute path created0700, symlink ancestry rejected, exact env mapping and permission checked, exclusive write/read/remove probe before each Popen. This extends the existing five-location isolation contract; not a sandbox, no claim to audit every filesystem write. Runtime directories retained privately for inspection, not recursively deleted.

private-raw holds process stdout/stderr, error details, binary/work and runtime directories. No full environment, private paths, PID or installed binary identity goes into public-safe. Technical source/input/output hashes and statuses may be projected. Consumer-valid rows are reserialized through a fixed schema into values.json; raw stdout stays private. result.json is written through a closed pending file and atomic replace only after all checks; it alone represents overall acceptance, values.json never does. A write failure must not leave a finalized PASS receipt. Failure results preserve available stage statuses but do not claim three cases completed. Public-safe remains subject to independent publication review, not automatic upload permission.

Preparation permits only text/JSON/hash/AST static inspection. No compiler, native, runner invocation or runtime probes were performed in preparation. Any revised protocol/manifests require review and a fresh attempt; old published results and old sources remain unchanged.
