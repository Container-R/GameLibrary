# Main source and algebra check: quaternion signs in cubic animation

2026-11-01. Main integrator directly read Khronos glTF specification at commit `59ecbdba704206bb656965ab4e202881806066f1`, `specification/2.0/Specification.adoc`, lines 879–895 and 3979–4077. Returned source blob: `e5088cdc9a4e344e836568f57e2db6726f5a6740`.

The TRS formula establishes XYZW order, a scalar W, unit rotation values and quadratic rotation-matrix terms. Appendix C separates rotation LINEAR from componentwise cubic Hermite interpolation, scales derivatives by the segment duration, and requires normalization of interpolated rotation quaternions. It warns against producing the zero quaternion. The short implementation note is not adopted as a complete arbitrary-tangent validity test.

The original gate's identity-to-180-degree example is algebraically valid, but the integrator proposed an identity-to-120-degree replacement to avoid making the illustration depend on a shortest-direction tie. With zero tangents, the midpoint normalized outputs are +60 degrees and -120 degrees about Z when only the final quaternion representative is negated. This is a cubic-only calculation, not a claimed LINEAR output or an exporter observation.

For the proposed 120-degree endpoints, let the two value weights be a and b. On the segment a,b are nonnegative and a+b=1. Their quaternion dot products are respectively +1/2 and -1/2; unnormalized squared norms are a²+b²+ab and a²+b²-ab. The latter is 1-3ab and at least 1/4. Neither path reaches zero. At the midpoint, the resulting rotation matrices map the X axis to (1/2,√3/2,0) and (-1/2,-√3/2,0), respectively. This is an exact real-arithmetic derivation, not executed code, a serialized asset or an engine result.

A common global negation of all values and tangents changes the entire unnormalized Hermite curve's sign, preserving the represented rotation wherever normalization is defined. The counterexample refutes unrestricted per-key sign replacement, not every possible safe local transformation, and provides no universal sampling count or repair algorithm.

Publication requires final-draft inspection and an independent source/algebra review bound to the actual chosen example. Existing scalar, translation-retiming and runtime evidence is not inherited.

The public GitHub commit endpoint was also read: the exact specification commit reports committer time 2026-10-30T15:21:59Z and message “Minor editorial updates (#2691)”. This is the selected snapshot's commit metadata, not a glTF release date or proof that the cited interpolation clauses originated in that commit. The three gate input body hashes were independently recomputed and matched. Targeted text search of the source-note and animation-role folders found no existing per-key quaternion-sign mechanism; this is a bounded duplication check, not a semantic search of every archive.

A supplementary direct read of lines 3257–3298 confirmed sampler interpolation selection, relative input time and rotation VEC4 representation. It also distinguishes the format's finite numeric storage constraints from the exact symbolic calculation here. No asset accessor, serialization or representation validity was tested; the derivation's square roots must not be described as exact stored float32 samples.
