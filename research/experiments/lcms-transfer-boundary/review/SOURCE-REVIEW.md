# Independent color-space depth source gate

2026-11-01 00:40 UTC. Reviewed gate SHA256 `bae2ade24e37ff4c5aa9f03cabdd6a3bd911a5d3fac2dc3d5024f3874e85ac65`, current SOL-ART2D-001 metadata and original run.py as text, source/capability receipts and MAIN-SOURCE-READ.md. No Pillow/CMS import, CDLL, native call, transform, image generation or numerical experiment.

## Decision

Accept the distinct question for a **narrow source/ABI feasibility gate only**. Existing five conversions/six composites are explicitly stored-byte-domain observations; they do not claim color management. Holding straight association/source/backdrop/alpha fixed while changing working transfer is a consequential independent handoff. There is no prior overclaim to repair and no need for another article or general ICC framework.

## Sources independently read and bounded support

- [SVG2 CR 2018-10-04 §13.9](https://www.w3.org/TR/2018/CR-SVG2-20181004/painting.html#ColorInterpolation) explicitly selects sRGB versus linearRGB for specified interpolation/compositing operations, with initial sRGB. Thus linear-light behavior must be a chosen product contract, not a universal claim that all encoded-space authored interfaces are incorrect.
- [CSS Color4 CRD 2024-02-13 §17](https://www.w3.org/TR/2024/CRD-css-color-4-20240213/#color-conversion-code) labels its transfer-function examples non-normative. Also opened the separately dated [2026-10-29 CRD](https://www.w3.org/TR/2026/CRD-css-color-4-20261029/). Keep each date/section attribution distinct; these are definitions/comparison mathematics, not evidence a game engine or arbitrary ICC path implements them.
- [PNG second edition 2003-11-10 §4.2 and §13.16](https://www.w3.org/TR/2003/REC-PNG-20031110/#13Alpha-channel-processing) separates opacity from gamma processing and describes intensity-domain compositing. This historical source supports the conceptual distinction, not current PNG decoding or display conformance; the candidate uses no PNG file.
- [Compositing CRD 2024-03-21](https://www.w3.org/TR/2024/CRD-compositing-1-20240321/#simplealphacompositing) supplies source-over relationships, not the chosen working transfer. Do not repeat the old association experiment as new ICC evidence.
- [Pillow ImageCms documentation](https://pillow.readthedocs.io/en/stable/reference/ImageCms.html), currently13.0.0, and actual installed ImageCms.py createProfile text agree on LAB/XYZ/sRGB choices. They do not provide a named linear-sRGB constructor. A nominal sRGB-to-sRGB conversion would not establish linear working arithmetic.
- [LittleCMS official engine page](https://www.littlecms.com/color-engine/) establishes the original maintainer/documentation route only. The gate has not yet established exact C ABI, profile creation semantics or a runtime-loaded library identity.

## Capability and proposed acceptance constraints

Read the existing ELF dynamic receipt: _imagingcms declares vendored liblcms2-88eaba2f.so.2.0.19 and relative RPATH. Its recorded vendored SHA4cf9f690 differs from system .2.0.16 SHAa0afaac5. These are file/dependency observations, not runtime load proof or authenticated release versions. If later using direct ctypes on the vendored file, say it is a direct identified LittleCMS experiment, not Pillow ImageCms execution. Resolve/hash the exact selected path and prohibit silent system fallback; separately specify dependencies and runtime self-report checks.

Before protocol/code, require a pinned original header and implementation trace for every selected function, field layout, scalar/pointer type, channel format, rendering intent/flags, lifecycle and failure return. Explicitly derive same-primaries/white-point linear profile construction and chromatic-adaptation behavior. Do not guess format bitfields or choose a tolerance after seeing native output.

The candidate neutral sample with alpha128/255 over opaque black and alpha1 control is sufficient to distinguish transfer-domain handling, but **not** to validate RGB channel order, primaries, gamut mapping or general ICC correctness. Alpha128/255 is not exact one-half. Keep alpha outside the RGB transform; an opaque output alpha does not establish RGB correctness. Compare the native forward/backward RGB conversions to independently derived piecewise math with frozen precision/rounding/tolerance, while labeling the compositing arithmetic as original host code, not an LCMS compositing API result. An opaque roundtrip alone cannot discriminate the domain mistake.

Prefer the smallest two-condition conversion/composite contract. No profile file parser, arbitrary assets, additional rendering framework or installed tool is needed. If safe exact profile/ABI/identity selection cannot be established from existing bytes and original sources, retain a source-only conclusion; do not replace it with a handwritten calculator and call that native ICC validation. No runtime is authorized by this review.
