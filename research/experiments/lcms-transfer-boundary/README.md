# Finite sRGB transfer-domain handoff

This original numeric fixture tests one specific contract: decode encoded sRGB, perform host-side alpha arithmetic in linear RGB over opaque black, and encode again. It does not test an image, an ICC file parser, Pillow ImageCms, a display, or engine compositing. The existing ART2D Pillow alpha-association fixture remains unchanged and independent.

## Frozen experiment

`PROTOCOL.md` SHA256 `31792686b01bbe1a71d03fc66e7852e1771eb02dabf7431db43aa8f1d5fd69e6` was accepted before implementation/native execution. `protocol-reference.json` contains independently calculated Decimal reference values. Input is straight encoded RGB `(128,64,192)/255`, alpha `128/255`, opaque black background; the sole control changes alpha to `1`.

The selected vendored LittleCMS library has SHA256 `4cf9f69016c7804bcb4fa56f5bbc55640cb1b7196ac7b93ba29ed9df9bd9ff4d`. It self-reports version `2190`. Exact public source comparison is tag `lcms2.19`, commit `b76633e60c8387a77268fb3359277ca25b5fd75c`; correspondence of installed binary and public source is not authenticated. File hashes and the selected `/proc/self/maps` entries identify the observed choice, not all its dependencies or build provenance.

The child constructs two profiles (built-in sRGB; RGB with the same D65/Rec709 primaries and gamma 1), one owned gamma curve and two transforms. It uses RGB double buffers, relative colorimetric intent and fixed `NOCACHE | NOOPTIMIZE` flags. These are recorded construction inputs, not a complete readback of profile tags. Compared source uses D50 PCS internally and float32 intermediates; double storage is not a double-precision pipeline guarantee.

One decode is reused for two host-side alpha products, which are the actual inputs to two reverse conversions. The CMM does not perform the alpha multiplication. Every native result must be finite before comparison. Each channel must meet the predeclared normalized absolute tolerance `1e-4`; this is a finite acceptance choice, not a library-wide bound. There is no exact output-byte oracle: the green mathematical reference is too close to a half-byte rounding boundary for that implication.

## Actual accepted observations

| Observation | Author | Independent repeat |
|---|---|---|
| Invocation UUID | `35db4b98-af25-4248-a14f-cf56e196cde7` | `bb5b395c-6e2c-4f22-89e7-284c5a06f658` |
| CMM child processes | 1 | 1 |
| Explicit C API calls, including version and cleanup | 20 | 20 |
| `cmsDoTransform` calls | 3 | 3 |
| Exit / stderr / error callback | 0 / empty / empty | 0 / empty / empty |

Both observed normalized main encoded-linear RGB:

`[0.36293014883995056, 0.17460043728351593, 0.5512598752975464]`

The contrasting direct encoded arithmetic is:

`[0.2519646289888504, 0.1259823144944252, 0.3779469434832757]`

The opaque control returns `[0.501960813999176, 0.250980406999588, 0.7529411911964417]`. The raw result binds input buffers, actual decoded values, host products, reverse inputs, API entry/return sequence, formats, cleanup and callback observations. Source/library/Python before-after hashes agree. Total: **2 children, 40 explicit C API calls, 6 conversions, the same 2 alpha conditions repeated**, not 40 test scenarios. Version is queried inside each child, not in separate processes.

The independent reader imports no author validator or native interface and compares literal call order/arrays with its own Decimal reference. Main also ran both static readers against both archives under normal Python and `-O` (8 commands, zero CMM calls). This is same-library replication, not independent implementation agreement. Archive consistency is not execution authentication.

## History and failure boundaries

`historical-pre-native-review/` retains the original eight-source snapshot. Synthetic review receipts exposed acceptance of contradictory timeout/drain metadata and malformed Python digests; timestamp comparison and setup/after-hash failure recording were also tightened before any CMM execution. `PRE-NATIVE-CORRECTIONS.md` and the independent review preserve the distinction. No defective initial native attempt was run, and no native failure was hidden or relabeled.

Final pure suites have 7 methods in normal and optimized mode. Each suite starts two guarded Python subprocesses for optimized-startup/import-failure freshness checks; these do not load LittleCMS. Pure synthetic receipts and missing-source probes are not additional color conditions. The child result is only a child-observation PASS; the parent publishes its summary only after after-hashes and the archive consumer pass.

No native timeout/error/partial-cleanup branch was exercised. On timeout, the runner attempts to kill its owned process group and performs bounded wait/drain; this is neither universal descendant containment nor a demonstrated failure-path result. Filesystem preparation can fail; no full transactional filesystem guarantee is claimed.

## Static inspection and reproduction

Inspect archived observations without loading a native library:

```sh
python check.py . evidence/35db4b98-af25-4248-a14f-cf56e196cde7
python -O check.py . evidence/35db4b98-af25-4248-a14f-cf56e196cde7
```

For relocated reviewer evidence, supply its exact copied eight-source directory and UUID evidence directory. Historical absolute command/environment strings are checked as recorded associations; static inspection does not require the old paths or installed CMM to exist. The independent review directory documents its own static reader invocation.

Do not run `run.py` in archived source/evidence directories: it removes `summary.json` and creates new invocation evidence. A separately authorized native repetition must copy exactly the eight names in `SOURCE-SHA256.json` into a fresh disposable directory, retain their hashes, and use the recorded Linux ABI/library bytes. Then run `python run.py` from the copy. No install, fallback library, changed tolerance or parameter sweep is part of reproduction. The runner uses minimal base environment `PATH=/usr/bin:/bin`, `LANG=C`, `LC_ALL=C`, plus the exact five-location isolation helper.

## Engineering scope

This closes a narrow numerical asset-handoff gap: correct straight-alpha representation alone does not identify the intended color working domain. It does not establish that linear compositing is the artistic requirement for every UI or existing asset. Storage encoding, work domain, transfer responsibility, intermediate precision, quantization and artistic approval must remain distinct fields.

No third-party artwork, PNG decode/encode, profile-file input, GPU/driver, browser, DCC, real display, HDR/wide-gamut mapping, filtering/mipmaps, performance, perceptual benefit or arbitrary ICC correctness is covered. Successful finite cleanup does not prove every failure path. See the linked article/source note at integration for the original acceptance worksheet and primary-source locators.
