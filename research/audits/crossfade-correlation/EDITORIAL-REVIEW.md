# Crossfade correlation note: independent editorial review

2026-11-01 UTC. Reviewed complete article SHA256 `0be6402f30fb151ad73379c310c3f1d2ac4f633b4ce3222cd7d0ac35ce03cb65`, source gate and SOURCE-REVIEW. No execution, audio generation/playback, author-file changes, legacy changes or remote writes.

## Verdict and precise changes requested

Accept the finite mathematical proof and bounded source interpretation, subject to two small clarifications:

1. Define covariance using the same denominator **n**, not the n−1 sample estimator. The stated decomposition of the uncentered cross moment otherwise depends on an unstated convention.
2. Attribute the block-wise gain-ramp observation explicitly to the selected scalar **XFade2_next_ak** path. Do not generalize it across constructor-selected rate/SIMD variants.

## Checks performed

Independently reopened official fixed `PanUGens.cpp` at `d263b8cc9905302bb6cfc26e8e68f22bb43092e9`, lines 425–475. Constructor lines 426–436 select different functions; scalar path starts at 448. Its amplitudes depend on table position and level and its parameter-change branch advances gains linearly; this is source inspection, not measured execution. The draft already selects ideal level=1 and disclaims sample-exact equivalence between transcendental curves and lookup/rounding/ramp implementation.

Independent hand expansion gives P_z=a²P_x+b²P_y+2abC_xy. With covariance defined using n, C_xy=cov_n+mean(x)mean(y). The draft distinguishes this cross moment from independence and does not equate equal-power labeling with arbitrary paired-signal conservation.

Recomputed the three original four-sample cases at a=b=1/sqrt(2): orthogonal inputs yield h(sqrt(2),0,0,−sqrt(2)), sum of squares 4h², mean square h²; identical inputs yield sqrt(2)x and 2h²; opposite inputs yield zero. Thus individual P is preserved under the stated equal-power/zero-cross-moment conditions, not the unattenuated sum 2P. In the first case sample peak sqrt(2)|h| is compatible with preserved mean square. These are exact hand derivations, not PCM results.

No measured loudness, true-peak, clipping, actual rendered sound, middleware compatibility or listening result is claimed. Floating intermediate values above one are correctly separated from output-range clipping. Source paraphrase is compact and attribution distinguishes historical immutable source from rolling help. The existing music lifecycle and silent-stem evidence is expressly not transferred to this correlation question. No private runtime metadata appears.

Pending exact final hash after the two clarifications; no further change requested.

## Final acceptance addendum

ACCEPT final article SHA256 `260aeec74df5dc5c49fe01a536cfe3106bc667ef23998031a8d87ae7d75668e2`. Independently read both clarifications. Reversing only the scalar-path qualification and covariance-denominator convention exactly reproduces initial reviewed SHA256 `0be6402f30fb151ad73379c310c3f1d2ac4f633b4ce3222cd7d0ac35ce03cb65`. Original math, cases and evidence scope are unchanged. No further correction requested.
