# Frozen stored-byte alpha association contract

2026-10-31, before conversion/compositing calls. Original numeric buffers only, not artwork. Each is1x1 with four8-bit channels. Numeric domain is stored channel bytes; no transfer-function/ICC/linear-light transformation claim.

Source straight RGBA=(240,120,60,85), alpha=85/255=1/3. Associated RGBa=(80,40,20,85). Opaque black backgroundRGBA=(0,0,0,255). Integer output oracle uses nearest rounding for nonnegative exact rationals; chosen main conversion is exactly divisible.

Five finite groups:
1. Actual RGBA→RGBa conversion must yield(80,40,20,85). Explicit RGBa→RGBA conversion must recover(240,120,60,85) for this exact tuple only.
2. Correct straight RGBA source-over opaqueblack must yield(80,40,20,255). Explicitly converted source must yield same result.
3. Reinterpret associated rawbytes as straight RGBA (no conversion) and composite: ideal80/3,40/3,20/3, nearest integers(27,13,7), alpha255. This is intentional semantic misinterpretation; expected operation succeeds but result differs from group2. Not a malformed-file test.
4. Opaque controlRGBA=(240,120,60,255): association conversion preservesbytes; composite yields same opaque tuple.
5. Transparent controlRGBA=(240,120,60,0): premultiply yields(0,0,0,0); explicit unpremultiply remains(0,0,0,0), not original hiddenRGB. Original transparent source and convertedtransparent source both composite to opaqueblack. No divide-by-zero or lossless-roundtrip assumption.

No PNG, filtering,resizing,mipmaps,atlas,engine,GPU,physical display,perception or color-managed blending. Alpha0 control explicitly demonstrates lost hiddencolor; low-alpha quantization generally precludes lossless roundtrip but unlisted values are not tested. No claim all dark fringes have this cause or premultiplied format always preferred. Read source gate ../art2d-gate/GATE.md; pinnedPillow293218ad source comparison not installed-binary authentication.
