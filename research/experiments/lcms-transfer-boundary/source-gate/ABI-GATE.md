# Finite LittleCMS ABI/source feasibility gate

2026-11-01. **Read-only source and ELF inspection only. No ctypes/Pillow native import, library loading, version function, profile creation, transform, image generation or experiment execution.** This document refines `gate.md`, not an execution authorization or a frozen numeric-result protocol.

## Decision and narrowed input

The inspected fixed API can plausibly support one tiny genuine library-conversion comparison without installation or arbitrary ICC files. Recommend protocol review next, conditional on the acceptance requirements below. The intended main tuple is now **unequal RGB `(128,64,192)`**, alpha **128/255**, over opaque black, with the same tuple at alpha 1 as control. This supersedes the earlier neutral candidate: neutral RGB could not reveal channel permutation. Alpha 128/255 is not exactly 1/2. No expected output has been measured or fitted.

Hold straight association fixed. Compare direct encoded-domain arithmetic against library decode → original host source-over arithmetic in linear coordinates → library encode. The CMM does conversion, not the host's alpha arithmetic. This still does not prove general primaries/gamut accuracy or a universal preference for linear compositing.

## Immutable source identity

Official repository linked by the LittleCMS author's site: `mm2/Little-CMS`. GitHub plugin fetched `https://api.github.com/repos/mm2/Little-CMS/git/ref/tags/lcms2.19`: the lightweight tag object has type `commit`, SHA **`b76633e60c8387a77268fb3359277ca25b5fd75c`**. Header declares `LCMS_VERSION 2190`. Tag publication date was not independently established; do not infer it from file names. Installed byte/source correspondence remains unverified.

Exact inspected source at that commit:

| Source locator | What it establishes for this finite proposal |
|---|---|
| [lcms2.h 99–145](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/include/lcms2.h#L99-L145), [190](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/include/lcms2.h#L190), [684–743](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/include/lcms2.h#L684-L743), [972](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/include/lcms2.h#L972), [998–1038](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/include/lcms2.h#L998-L1038) | Scalar/opaque handles, format bit fields, RGB double format and xyY structures. |
| [lcms2.h 1092–1158](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/include/lcms2.h#L1092-L1158), [1246–1249](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/include/lcms2.h#L1246-L1249), [1646–1696](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/include/lcms2.h#L1646-L1696), [1725–1891](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/include/lcms2.h#L1725-L1891) | Fixed non-vararg function signatures, intent/flag constants, ownership cleanup and format getters. |
| [cmsvirt.c 101–215](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmsvirt.c#L101-L215), [638–682](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmsvirt.c#L638-L682) | RGB profile construction, matrix/TRC tags, built-in sRGB parameters and curve lifecycle. |
| [cmswtpnt.c 252–321](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmswtpnt.c#L252-L321) | RGB-to-XYZ matrix construction includes adaptation to D50. |
| [cmsgamma.c 496–541](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmsgamma.c#L496-L541), [909–920](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmsgamma.c#L909-L920) | sRGB type-4/inverse branches; gamma builder uses a parametric curve; gamma 1 is the proposed linear TRC. |
| [cmscnvrt.c 360–415](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmscnvrt.c#L360-L415), [1123–1134](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmscnvrt.c#L1123-L1134) | Absolute-intent adaptation and black-point compensation branches; choose relative intent and no BPC flag, not perceptual defaults. |
| [cmsxform.c 258–316](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmsxform.c#L258-L316), [917–939](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmsxform.c#L917-L939), [1289–1362](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmsxform.c#L1289-L1362) | Creation/linking path and float intermediates; default adaptation state is consulted, not proof that every stage is double precision. |
| [cmspack.c 1402–1450](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmspack.c#L1402-L1450), [3108–3155](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmspack.c#L3108-L3155) | Double RGB buffers are converted to/from float32 working values. `TYPE_RGB_DBL` describes external storage, **not a double-precision pipeline guarantee**. |
| [cmsopt.c 1919–1962](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmsopt.c#L1919-L1962) | `NOOPTIMIZE` prevents the later optimization selection, but trivial preprocessing occurs first. Do not claim absolutely no simplification. |

These are narrow source observations, not reproduction of full implementation. Original published prose should summarize this chain compactly rather than translate these files.

## ABI contract to freeze before code

For the inspected Linux ABI, plan explicit ctypes `argtypes`/`restype` for every called symbol, no default integer pointer returns and no varargs. Before native entry, check expected sizes/offsets: c_uint32 4 bytes, c_double 8 bytes; xyY three doubles, size 24 with offsets 0/8/16; triple three xyY structures, size 72 with offsets 0/24/48. The future process must reject unsupported layout, not reinterpret buffers.

| Function | Exact finite binding intent |
|---|---|
| `cmsGetEncodedCMMversion(void)` | returns C int; planned expected self-report 2190, not provenance authentication |
| `cmsCreate_sRGBProfile(void)` | returns opaque pointer; null is failure |
| `cmsBuildGamma(context, gamma)` | context opaque pointer NULL, gamma double 1.0; returns curve pointer |
| `cmsCreateRGBProfile(white*, primaries*, curve*[3])` | white/triple structs and exactly three pointers to the same owned gamma curve; returns profile pointer |
| `cmsFreeToneCurve(curve*)` | void; free the shared allocation once, not three times |
| `cmsCreateTransform(input, input_format, output, output_format, intent, flags)` | two opaque profiles and four uint32 arguments; returns transform pointer |
| `cmsDoTransform(transform, input_buffer, output_buffer, size)` | void; buffer pointers, uint32 **pixel count**, not byte/channel count |
| `cmsGetTransformInputFormat/OutputFormat(transform)` | uint32 readback; require selected format |
| `cmsDeleteTransform(transform)` | void |
| `cmsCloseProfile(profile)` | C int `cmsBool`; record/check cleanup return |
| `cmsSetLogErrorHandler(callback)` | void; callback signature `(context pointer, uint32 code, const char* text) -> void`, keep callback alive until all C work/cleanup ends; any captured CMM error fails the finite run |

Source tuple for linear profile: D65 `(0.3127,0.3290,1.0)`; R `(0.64,0.33,1.0)`, G `(0.30,0.60,1.0)`, B `(0.15,0.06,1.0)`; gamma 1.0. These match the built-in sRGB source primaries/whitepoint, differing in TRC. Constructors create v4.4 display RGB profiles with XYZ PCS in the compared source. Keep profile/curve/transform handles tracked and dispose in `finally`, deleting both transforms before closing both profiles. Built-in source frees its one shared curve after successful profile construction; use the same single-free ownership pattern, with null checks on every allocation. No user-selected profiles, ICC file parsing or profile serialization needed.

Both forward and reverse transforms use **TYPE_RGB_DBL = `(1<<22)|(4<<16)|(3<<3)` = `0x440018`**, no extras/alpha/planar/swap/premultiply bits; `INTENT_RELATIVE_COLORIMETRIC = 1`; `cmsFLAGS_NOCACHE | cmsFLAGS_NOOPTIMIZE = 0x0140`. No black-point compensation, proofing, gamut check, forced CLUT or plug-in installation. Float path already bypasses its cache in the inspected source; NOCACHE remains explicit. Alpha is a separately held host scalar and is never passed as RGB or gamma-converted.

## Adaptation and tolerance: what can and cannot be justified

Identical device primaries/whitepoint do **not** eliminate the internal D50 PCS. RGB profile creation writes D50 media white, chromatic-adaptation data and adapted colorant matrices. A paired conversion is expected to cancel corresponding colorimetric transforms only numerically; do not promise identity mathematics or no adaptation merely because both constructors receive D65.

The fixed source supports using a small nonzero comparison tolerance: the double input is explicitly cast to float32 before pipeline evaluation and expanded back afterward. It does not provide a global error bound proving every profile/point lies within a selected epsilon. `NOOPTIMIZE` does not change that fact.

Proposed finite acceptance policy for protocol review: absolute **1e-4 in normalized channel coordinates** for the selected forward, reverse and opaque-control comparisons to independently evaluated sRGB transfer functions. This is an original engineering threshold (0.0255 of an 8-bit code value), **not a LittleCMS accuracy guarantee or a measured result**. It is intended to tolerate implementation precision while remaining much smaller than the transfer-domain counterexample. Before execution, the protocol must compute/freeze reference literals independently and establish that the two candidate outputs are separated by substantially more than that threshold and that final rounding is not ambiguous. Do not expand the threshold after observing library output.

If the coordinator requires a formally proven worst-case library-error bound, this source inspection does **not** supply one: stop before native execution rather than mislabel this acceptance threshold as a theorem. A failed tolerance test would reject this finite hypothesis/configuration, not identify a library defect or authorize another profile/flag search.

## Installed linkage and safe finite process boundary

The selected absolute library is:
`/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages/pillow.libs/liblcms2-88eaba2f.so.2.0.19`

SHA256 `4cf9f69016c7804bcb4fa56f5bbc55640cb1b7196ac7b93ba29ed9df9bd9ff4d`.

`readelf -Ws` confirms exported definitions for all functions in the table; saved `lcms-selected-symbols.txt`. This does not establish they execute successfully. Existing `_imagingcms` dependency metadata points to this name, but the proposed fixed API process should load this **absolute path directly**, without importing Pillow or resolving generic `liblcms2.so.2`. Read/hash before and after; if later authorized, capture `/proc/self/maps` entries for the actual loaded file and runtime version. Mapping/bytes/self-report still do not authenticate correspondence to the public tag.

A small dedicated child with the existing exact isolation helper and minimal base environment suffices. No reusable ICC framework, loader search, arbitrary patterns, profile directory scan, installation, graphics API or images. Preserve return/null/error diagnostics and exact output buffers; initialize output with a sentinel so missing writes cannot look successful. Parent timeout/cleanup and archive checks should reuse the established finite pattern, not generate a new broad harness or coverage matrix.

**Stopping point now:** ABI/source feasibility supported for review, with explicitly non-guaranteed finite tolerance. No implementation or CMM execution yet. Next action, if selected, is one frozen small protocol and independent ABI/source review; no native work until separate approval.
