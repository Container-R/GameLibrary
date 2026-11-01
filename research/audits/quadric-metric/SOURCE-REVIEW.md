# Plane quadric versus finite triangle — independent source/math review

2026-11-01 UTC. **ACCEPT as a compact mechanism addition**, not an algorithm failure example. Gate SHA256 `26e86b583f0cd9769817f78b25c76cdc3d838fdbcf456f4f7b319bd4e9817315`.

## Reading scope

Independently opened the [author's publication page](https://www.cs.cmu.edu/~garland/quadrics/) and [original eight-page paper](https://www.cs.cmu.edu/~garland/Papers/quadrics.pdf). Read extracted text on physical pages 3–5: §4, §5 equation (2), §5.1 and boundary discussion in §6. The unit-normal plane definition, quadratic form, additive rule and separate boundary constraints support the gate. A screenshot request for physical page 4 returned a reference without inspectable image content; this review does **not** claim visual equation/figure inspection. Algebra was checked independently against extracted equation structure and prose.

A useful optional locator is §6.1 on physical page 5: the paper itself distinguishes its heuristic from a separate sampled surface-distance evaluation used for assessment, not algorithm selection. This may support one short distinction; it is not a maximum-distance guarantee or a reason to reproduce the paper's results.

Independently fetched pinned [meshoptimizer simplifier.cpp](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/simplifier.cpp). Read quadricError 765–787, plane/point/triangle/edge construction 790–856, face/vertex/edge accumulation 1046–1141 and construction calls 2381–2386. Default vertex regularization is present (factor 1e-7 rather than the explicit Regularize option's 1e-1). Eligible border/seam edges receive additional contributions. Position-error normalization and the attribute overload are distinct. The isolated paper term is therefore not the library's full metric or reported result.

## Independent hand check

For the stated closed triangle, every point has z=0, x≥0, y≥0 and x+y≤1. The unit-normal plane vector p=(0,0,1,0) gives (pᵀv)²=z². At P=(2,0,0) this is zero. Since x≤1, (2−x)²+y²≥1, with equality at (1,0,0). Thus distance(P,T)=1 exactly. The nonnegative-weight sum of copies of this same plane still vanishes at P. No numerical computation or execution is needed for this finite proof.

## Interpretation requirements

Keep the omitted point and edge contributions prominent beside the example. P is not an asserted candidate collapse, original vertex, output vertex or reachable library result. No actual mesh error, boundary erosion, silhouette or rendering outcome follows. A finite-point-to-triangle distance is not by itself a comparison of two complete meshes. Conversely, adding boundary penalties is not proof of a Hausdorff or view-dependent error bound.

This adds real explanatory content to “approximate metric”: it identifies exactly which information the isolated supporting-plane term omits. Accept the small addition if these exclusions remain adjacent; reject any rewrite that presents it as meshoptimizer returning zero error for the example. No script, executable model, simplifier, asset generation, image analysis or native execution performed.
