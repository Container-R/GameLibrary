# Main exact-evidence and source read

2026-11-01 00:39 UTC. Read full prior article (SHA256 2fc2423598b2b040c7dadf6e304c575f0e27e37fcca48307f7c9949a78441b70) and full run.py (7895e68073e93b09eacbd86879baec1d3be6e5bc5be22df65a7307f925e6f74f). Prior five conversions and six composites operate on original 1x1 byte buffers and explicitly exclude sRGB/linear/ICC. No new execution occurred in this read.

Opened W3C CSS Color 4 current and dated 2026-10-29 Candidate Recommendation Draft, sections 10.2/10.3 and conversion code: same sRGB primaries/white point, distinct nonlinear transfer; piecewise thresholds 0.04045 and 0.0031308. This is draft CSS color definition evidence, not a game-engine implementation contract. Interpolation sections do not establish arbitrary compositor behavior.

Opened historical PNG second edition 2003-11-10 Recommendation, section 13.16: RGB compositing equation uses intensity rather than encoded values. This does not mean the proposed fixture reads PNG or validates present-day decoder/display behavior. No source illustrations, videos or images were inspected.

Sources: https://www.w3.org/TR/2026/CRD-css-color-4-20261029/ ; https://www.w3.org/TR/2003/REC-PNG-20031110/#13Alpha-channel-processing . Gate/protocol still pending; no native library import, color transform, image generation or engine run authorized here.

Read SVG2 dated 2018-10-04 CR painting section 13.9: color-interpolation initial sRGB, linearRGB selectable. Thus this extension must fix a chosen working contract, not call every encoded-space operation a bug. Existing role/asset appearance may intentionally depend on encoded-space rendering; no browser or SVG execution occurs.

00:40 UTC: GitHub original tag lcms2.19 resolves b76633e60c8387a77268fb3359277ca25b5fd75c; directly read pinned include/lcms2.h signatures/format macros and src/cmsvirt.c RGB and sRGB profile constructors. Built-in source profile uses D65(.3127,.3290,1), Rec709 primaries, linked identical TRC pointers and frees the single tone curve once. RGB profile creation uses D50 PCS and adaptation tags, so matching nominal primaries is not proof of an identity arithmetic pipeline. This pin is comparison evidence only, not binary provenance authentication. No native call occurred. Header fixed signatures will need independent protocol/code review before any ctypes binding.

00:41 UTC: read pinned cmsxform.c FloatXFORM and cmspack.c UnrollDoublesToFloat / PackDoublesFromFloat. Double input/output storage does not imply double-precision internal evaluation: float intermediates/casts are visible in this path. Any proposed tolerance must acknowledge that implementation boundary and remain a predeclared finite acceptance criterion, not an unproved global library error bound.

00:48 UTC: independently read pinned cmsgamma.c type4/inverse and gamma1 builder; also cmsopt.c preprocessing-before-NOOPTIMIZE branch. This supports the stated narrow comparison/configuration but not exact installed-source correspondence, full-double precision or universal error bounds. No source implementation copied into the planned oracle.
