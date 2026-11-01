# Main source read: simplification request and returned result

2026-11-01 UTC. Directly read official meshoptimizer commit `6daea4695c48338363b08022d2fb15deaef6ac09`: README Basic simplification; meshopt_simplify and meshopt_simplifyScale declarations/comments; rescalePositions; error/collapse stopping clauses; outer simplify loop; result-error conversion and return; ordinary wrapper and scale implementation.

The source supports the important receiving distinction: destination capacity must cover original index_count, the return supplies actual count, and topology/error/no-collapse conditions can terminate before the requested target. Requested ratio is not an output receipt. The inspected ordinary wrapper passes no attribute metric; the example's options zero and valid input premises matter.

rescalePositions chooses the largest axis extent, not a bounding-box diagonal. The inspected scale helper returns that extent. Unit conversion is only an arithmetic interpretation within the declared relative metric, with finite nonzero scale; it is not measured maximum surface displacement, screen-space error or visual/deformation acceptance. Absolute/sparse/attribute variants are outside the bounded example.

The 300-index input and targets 150/75 are hypothetical requests, not generated geometry or returned results. No count or monotonic improvement should be invented. Reusing original vertices also means fewer output indices is not automatically fewer allocated vertex bytes or lower observed GPU cost.

No simplifier, fixture, model, assets, renderer, visual inspection or benchmark was run. These selected branches are not a full algorithm proof or a diagnosis of any actual asset's stopping cause.
