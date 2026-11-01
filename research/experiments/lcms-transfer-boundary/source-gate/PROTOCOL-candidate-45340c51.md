# Candidate finite protocol: sRGB transfer domain with direct LittleCMS conversion

2026-11-01. **Pending coordinator and independent protocol acceptance. No experiment implementation or native CMM execution.** The only executed calculation supporting this protocol is the separate stdlib Decimal reference script, not a color-library result. Source/ABI gate: `ABI-GATE.md`, SHA256 `5be2508747c93e6c67fbcd3199fea7f5b9e9c96a0155048715b1d412ecfc2a71`.

## 1. One input, two alpha conditions, one owned child

Original straight encoded RGB integers **(128,64,192)** divided by 255, over an opaque black working backdrop `(0,0,0)`. Main alpha is exactly the rational **128/255**, not 0.5. Control alpha is 1. No additional colors, profiles, flags, rendering intents or retries. Both output alphas are 1 by this opaque-backdrop source-over contract; alpha stays in host arithmetic and never enters the RGB transform.

One separately authorized author child performs its own library identity/version checks, profile/transform creation and both finite conditions. No separate native version process. At most one separately authorized independent same-source child afterward, only if author result is accepted. Each child has a 20-second external timeout; cleanup attempts are separately bounded. No native calls occur during source review, Python test imports or parent archive inspection.

The finite question is whether **a specified linear-working contract** differs from direct encoded-space arithmetic while straight association is correct in both. This does not declare encoded-space authored appearance universally wrong.

## 2. Mathematical reference frozen before native execution

`protocol-reference.py` computes the independent design reference using stdlib Decimal precision 80 and the fixed piecewise sRGB formulas read in the dated source gate. It neither imports Pillow/ctypes nor opens a native color library. `protocol-reference.json` stores full values. Decimals below are rounded for readability, not measured outputs:

| Quantity | R | G | B |
|---|---:|---:|---:|
| Encoded input | 0.50196078431372549 | 0.25098039215686275 | 0.75294117647058824 |
| Decoded input reference | 0.21586050011389916 | 0.05126945837404322 | 0.52711512570581298 |
| Main direct encoded arithmetic | 0.25196462898885044 | 0.12598231449442522 | 0.37794694348327566 |
| Main linear arithmetic reference | 0.10835350593952585 | 0.02573525753677464 | 0.26459112192291789 |
| Main re-encoded linear reference | 0.36293014378096514 | 0.17460041871860451 | 0.55125986884332577 |
| Opaque re-encoded reference | 0.50196078431372549 | 0.25098039215686275 | 0.75294117647058824 |

Main path absolute separations from direct encoded arithmetic are approximately **0.1109655148 / 0.0486181042 / 0.1733129254**. The smallest is >0.0486, far above the selected 0.0001 tolerance. If library outputs satisfy the frozen normalized reference threshold, the two main paths remain distinguishable by >0.0485 in every channel. Unequal channels also expose simple channel swaps; they do not establish arbitrary colorimetry.

### Acceptance precision, not a library guarantee

- Every native decoded output must be finite, in `[0,1]`, and within **absolute 1e-4 per channel** of the decoded-input reference.
- Host computes two working RGB triples from that **actual native decoded output** and the two exact alpha inputs represented as Python doubles. Require finite host values and record them. No native result is substituted with the mathematical reference.
- Every native reverse output must be finite, in `[0,1]`, and within **absolute 1e-4 per channel** of its frozen main/opaque encoded reference. These are direct output conditions, not an inferred propagated-error bound.
- Independently check that main library output differs from direct encoded arithmetic by >0.0485 in every channel; opaque output matches original encoded input within 1e-4.
- The source shows float32 intermediates despite external double buffers and internal D50 PCS adaptation. 1e-4 is this experiment's original acceptance criterion, not a universal error theorem or an assertion that the implementation will pass. A failure is retained and stops the sequence; no flag, profile or tolerance search.

### Pre-freeze rounding limitation retained

For reporting only, define byte quantization `floor(255*x + 0.5)` for nonnegative accepted values, no clipping. Mathematical reference gives direct `[64,32,96]`, linear `[93,45,141]`, and opaque `[128,64,192]`. **The native linear result is not required to quantize to the same byte triple.**

In particular, the green reference is 44.5231067732 code values, only 0.0231067732 above the 44.5 boundary, whereas normalized tolerance permits 0.0255 code values. Thus an accepted normalized result could quantize to 44 or 45. No native-output quantization is required or accepted as a result criterion; the byte triples above are mathematical illustrations only, never exact byte-equivalence proof. The initial ABI gate's desired unambiguous-rounding condition is explicitly superseded by this normalized-only acceptance. No input/tolerance was tuned after a native run; none has occurred.

## 3. Exact CMM construction and finite native calls

Load only the absolute vendored library named in §5. Bind the fixed functions and layouts in ABI-GATE, with explicit argument/return types. Before library loading, require C uint32 size4, double size8, xyY size24 offsets0/8/16, triple size72 offsets0/24/48, and pointer sizes consistent with the recorded local process. No guessed varargs or implicit pointer conversion.

Constructor configuration:

- Source `cmsCreate_sRGBProfile()`.
- Linear profile `cmsCreateRGBProfile()` with D65 `(0.3127,0.3290,1.0)`, R `(0.64,0.33,1.0)`, G `(0.30,0.60,1.0)`, B `(0.15,0.06,1.0)` and three references to **one** `cmsBuildGamma(NULL,1.0)` allocation.
- Forward source→linear and reverse linear→source transforms, both `TYPE_RGB_DBL=0x440018`, intent1 relative colorimetric, flags `0x0140` NOCACHE|NOOPTIMIZE. No BPC, null-transform, proofing, forced CLUT, plug-ins or arbitrary ICC files.
- No alpha/extra-channel, planar, swap or premultiplication format bits. Source and destination buffers must be distinct fixed arrays.

Planned successful call counts:

| C API | Calls | Purpose |
|---|---:|---|
| cmsGetEncodedCMMversion | 1 | Require self-report2190; not source authentication |
| cmsSetLogErrorHandler | 2 | Install owned callback, restore NULL after all cleanup |
| cmsCreate_sRGBProfile | 1 | Source profile |
| cmsBuildGamma | 1 | Shared gamma1 curve |
| cmsCreateRGBProfile | 1 | Linear profile |
| cmsFreeToneCurve | 1 | Free shared curve once after constructor attempt has finished |
| cmsCreateTransform | 2 | Forward and reverse |
| cmsGetTransformInputFormat | 2 | Actual format readback |
| cmsGetTransformOutputFormat | 2 | Actual format readback |
| cmsDoTransform | **3** | Forward1pixel once; reverse1pixel for main and reverse1pixel for opaque |
| cmsDeleteTransform | 2 | Finally cleanup |
| cmsCloseProfile | 2 | Finally cleanup; check boolean result |
| Total on fully successful sequence | **20** | Three conversion calls, not 20 color scenarios |

Each input/output buffer has three doubles =24 bytes, Size=1 pixel. Decode the original tuple once; reuse that actual output for both alpha conditions. Encode the main working triple, then the opaque working triple in separate calls. Source tuples/array lengths/counts are checked before C calls. Output arrays start as NaN sentinels; every expected element must be overwritten with a finite result. Do not count sentinel setup as an input color case.

Emit call-entry and call-return records around each C API invocation, with function name, finite arguments/configuration, returned status or null/non-null handle observation. Opaque handle labels are sufficient; do not claim constructor inputs are tag readback. Callback signature is `(context pointer,uint32 code,const char* text)->void`, retained alive through cleanup; record diagnostic text/code with a bounded retained-text length. The callback must not throw into C: catch Python callback errors into a separate failure flag, retained until cleanup completes. Any callback error, null allocation, wrong version/format, nonfinite output, semantic mismatch or cleanup failure makes the attempt FAIL. `cmsDoTransform` is void: absence of a return error code cannot substitute for callback/output checks.

Finally cleanup releases each successfully allocated resource at most once, transforms before profiles. A failure stops further conversion work but still attempts applicable cleanup. Preserve actual attempted/returned call counts rather than inventing the full20 after partial failure or process termination. The shared curve is one allocation, never three frees. Restore error handler only after resource cleanup and before callback lifetime ends. Publish final PASS only after all cleanup returns, callback-error flags are checked and source/library after-hashes are verified; never emit success before finally completes.

## 4. Artifact, process and failure contract

One fresh invocation UUID directory. Exact minimal base environment plus existing isolation helper SHA `bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970` supplies HOME/XDG_CACHE_HOME/XDG_CONFIG_HOME/XDG_DATA_HOME/TMPDIR. No secret environment dump or general sandbox claim.

Runner removes a stale summary before optimized-mode rejection/local imports. Parent records actual attempted/returned UTC, argv, process exit/status, raw stdout/stderr and cleanup attempts. Child is launched in its own process group; on timeout parent attempts termination and bounded wait/drain, honestly recording unresolved cleanup. No automatic restart or independent repeat without new authorization.

Sources include this protocol, reference script/data, exact helper, original runner/child/checker and finite pure tests; bind before/after hashes. Record Python executable identity, library bytes before/after, version result, selected loaded mappings, constructor configuration, format readback, call log, all three native output buffers and host arithmetic. Strict JSON rejects duplicate keys, nonfinite metadata and bool/int substitutions; sentinel NaNs are not serialized into accepted output. A portable static checker reads supplied sources/raw receipt only, not current native libraries. Hash agreement is consistency evidence, not execution authenticity.

Keep archive small: no images, binary ICC profiles, whole process maps, copied upstream sources or broad synthetic matrices. A few pure tests should discriminate changed reference/format/count, wrong channel order, bad raw association and failure-summary freshness. They are not native color cases. Exact test code and manifest receive review before the single author child is authorized.

## 5. Library identity and explicit limits

Absolute path:
`/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages/pillow.libs/liblcms2-88eaba2f.so.2.0.19`

Expected SHA256 `4cf9f69016c7804bcb4fa56f5bbc55640cb1b7196ac7b93ba29ed9df9bd9ff4d`. Do not load generic `liblcms2.so.2`, import Pillow as an implicit loader, install another CMM or choose a fallback file. After loading, record only relevant `/proc/self/maps` entries and require this resolved library mapping; reject a different additional LittleCMS mapping. This verifies selected process mapping consistency, not the full dependency supply chain or upstream build provenance.

Comparison source is tag lcms2.19 commit `b76633e60c8387a77268fb3359277ca25b5fd75c`; runtime self-report and matching bytes do not authenticate that origin. The existing alpha-association fixture remains unchanged and retains its separate stored-byte scope.

Stop after the authorized child's accepted finite observation or any failure. No GPU, engine, browser, PNG, arbitrary ICC/gamut/HDR/profile correctness, filtering, image quality, calibrated display, perception, performance or general color-management certification. No claim that an intentional encoded-space artistic workflow must be replaced.
