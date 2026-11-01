# Crossfade correlation — independent source and algebra review

2026-11-01 UTC. **ACCEPT** gate SHA256 `9a5c82bff1ff20f5ce9f94946a84487c35967756e8d92890646aa8f8355cd8f3` for a short source-only note. No material mathematical correction. One publication clarification: explicitly select overall `level=1` when connecting the ideal unit-gain curve to XFade2, rather than implying the documented level input is absent.

## Independently read originals

- [Official XFade2 help](https://doc.sccode.org/Classes/XFade2.html), title SuperCollider 3.14.0 Help, Description / Arguments. It labels the crossfader equal-power and specifies pan −1 to +1; this is not a promise about every signal pair's output mean square or perceived loudness.
- Independently resolved official `Version-3.14.0` directly to commit `d263b8cc9905302bb6cfc26e8e68f22bb43092e9`; commit timestamp 2025-07-26T19:02:54Z, not inferred release date.
- [Fixed help source](https://github.com/supercollider/supercollider/blob/d263b8cc9905302bb6cfc26e8e68f22bb43092e9/HelpSource/Classes/XFade2.schelp#L1-L33).
- [PanUGens.cpp 425–475](https://github.com/supercollider/supercollider/blob/d263b8cc9905302bb6cfc26e8e68f22bb43092e9/server/plugins/PanUGens.cpp#L425-L475): constructor dispatches among rate/SIMD paths; paired sine indices and level-scaled gains, weighted addition; selected scalar control-rate path ramps amplitudes when parameters change. The inspected path does not derive gains from input correlation. Do not generalize its exact stepping to uninspected SIMD variants.
- [Samp.hpp 25–32](https://github.com/supercollider/supercollider/blob/d263b8cc9905302bb6cfc26e8e68f22bb43092e9/common/Samp.hpp#L25-L32), [Samp.cpp 61–70](https://github.com/supercollider/supercollider/blob/d263b8cc9905302bb6cfc26e8e68f22bb43092e9/common/Samp.cpp#L61-L70), [SC_World.cpp 193–196](https://github.com/supercollider/supercollider/blob/d263b8cc9905302bb6cfc26e8e68f22bb43092e9/server/scsynth/SC_World.cpp#L193-L196): independently traced table size, float32 sine construction and interface pointer wiring. A quarter-cycle is 2048 entries; paired indices give the sine/cosine design. No claim of exact transcendental values, unit-circle equality at every ramp sample, or actual executed output.

Read current music-state-transition and silent-stem article verification metadata and relevant scope passages. They cover lifecycle/virtualization and active-input/EOF normalization respectively, not this correlation cross term. Their experiments do not transfer to XFade2.

## Independent hand check

Expanding each `(a x_i+b y_i)^2` and averaging gives `a²P_x+b²P_y+2abC_xy`. Here `C_xy` is the uncentered cross moment with denominator n; covariance using that same denominator equals `C_xy−mean(x)mean(y)`. Only the zero-mean restriction permits substituting covariance directly. No n−1 sample-covariance convention is being invoked.

For ideal constant midpoint gains `a=b=1/√2`, the four entries of x+y in the orthogonal case are `h(2,0,0,−2)`; division by √2 gives `h(√2,0,0,−√2)`. Squares sum to `4h²`, hence mean square `h²`. Same-signal input gives `√2x`, mean square `2h²`; opposite input cancels, mean square zero. All inputs have zero mean and individual mean square `h²` for finite real nonzero h.

Thus equal individual input mean squares plus zero cross moment yield the individual level P, not the sum 2P. The three outcomes are exact mathematical constructions, not SuperCollider samples. The first construction's sample peak is `√2|h|` despite preserved mean square. No clipping follows without an explicit range/output rule, and none of these observations establishes loudness, true peak, acoustic power or listener preference.

## Publication scope

The finite music handoff is useful: specify actual pairing/alignment, shared content or polarity, extra gain and the quantity being accepted. Preserve the distinction between fixed-window constant-gain algebra and time-varying fades. Do not recommend universally replacing equal-power with linear fades, invent a studio defect, or describe these rows as generated audio/tests. No code, model, audio, playback, native or performance execution was performed in this review.
