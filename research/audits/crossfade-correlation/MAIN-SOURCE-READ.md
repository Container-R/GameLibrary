# Main equal-power crossfade source and finite algebra check

2026-11-01 UTC. Read official XFade2 help and pinned SuperCollider `d263b8cc9905302bb6cfc26e8e68f22bb43092e9`: PanUGens.cpp 425–475; Samp.hpp 25–32; Samp.cpp 61–70; SC_World.cpp 193–196; and XFade2.schelp 1–33. The selected control-rate scalar path uses level-scaled paired sine-table amplitudes and weighted addition; a changing-parameter branch advances gains. Do not identify ideal continuous sine/cosine values with exact table outputs or all SIMD/ramp samples. Select overall level=1 for the mathematical comparison.

Independently expanded the finite average of squared sums. The cross term is the uncentered moment with denominator n, becoming the same-denominator covariance only for zero means. For the stated zero-mean four-entry vectors, the orthogonal, identical and opposite cases give midpoint mean squares h², 2h² and zero. The first case has sample peak sqrt(2)|h| despite unchanged mean square. These are hand-derived ideal values, not samples produced by the implementation.

A source-only note can use this to require explicit input pairing, alignment/window, gain and acceptance quantity. It cannot claim no clipping without a range/output rule, perceived equal loudness, true peak, acoustic power, native reproduction, or universal superiority of another curve. No code, audio, numerical model, device or middleware was run; no source body, help example or private execution metadata is reproduced.

Sources: [official help](https://doc.sccode.org/Classes/XFade2.html), [fixed implementation tree](https://github.com/supercollider/supercollider/tree/d263b8cc9905302bb6cfc26e8e68f22bb43092e9).
