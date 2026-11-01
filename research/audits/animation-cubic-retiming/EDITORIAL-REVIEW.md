# Animator uniform-retiming integration — editorial and mathematical acceptance

2026-11-01 UTC. **ACCEPT unchanged** full role SHA256 `0b207e6ecacf78e014bf3ac167665309182ce681fd768839e49742b744547999` and source-note SHA256 `9943714653911fe7d79ef1f1157b74e687018c2bb424d0f84ae9cfad33219d0f`.

Read integrated role and source record, independent source review and the selected subsection in context. Independently reopened fixed Khronos specification `59ecbdba704206bb656965ab4e202881806066f1`, Cubic Spline Interpolation 4047–4077. No asset construction, numerical program, shader, engine or playback ran; no runtime archive, stage or remote changes.

## Independent mathematical check

The four Hermite basis polynomials and their association with endpoint values, starting outgoing tangent and ending incoming tangent match the pinned specification. Both participating tangent terms contain the segment duration. Holding endpoints fixed and multiplying duration by positive s while dividing each participating tangent by s preserves every normalized-progress value in ideal arithmetic.

This is not merely a sufficient midpoint trick: for equality of the entire segment polynomial, the h10 and h11 coefficients must agree. They are linearly independent (their derivatives at opposite endpoints isolate the two coefficients), so each participating duration–tangent product must be preserved. The prose correctly limits necessity to those products/used tangents, not every unused tangent in a complete asset.

At u=1/2 the basis values are 1/2,1/8,1/2,−1/8. The stated original, duration-only and compensated cases evaluate exactly to 3/4,1,3/4. The comparison uses equal normalized progress, with absolute times 0.5 seconds versus 1 second, not repeated measurement at the same absolute time. Other translation components are explicitly zero.

The source's unused first incoming/last outgoing tangent advice does not need a new article caveat: no complete encoded keyframe payload is supplied and the text refers to corresponding segment tangents. It would matter if a future asset were emitted; no such asset is claimed here.

## Evidence and role scope

The example concerns rewriting stored glTF translation CUBICSPLINE data, distinct from slowing a runtime clock. Full pose, rotation, nonuniform time warp, events, root-motion consumption and artistic quality remain excluded. Float32 representability, finite output, increasing encoded times and accessor metadata are expressly unverified, so the ideal proof is not promoted to an asset-validity guarantee.

The practical animator/technical-animator handoff is clear: decide whether same-progress translation shape is to be preserved or redesigned before selecting the data transform. It does not require the animator to own the importer. Existing role practice attributions and initial reading dates are preserved, and new fixed-specification evidence is separately dated. No draft instructions or private execution metadata appear. Source paraphrase is compact; no further correction requested.

## Single-sampler scope refinement

ACCEPT final role SHA256 `28eb64ee55cf6c71881aceb211fe1a840e28dabccaeafcf90d2cba6231237f6c`; source-note hash remains `9943714653911fe7d79ef1f1157b74e687018c2bb424d0f84ae9cfad33219d0f`. Reversing only the explicit single-translation-sampler phrase reproduces prior accepted `0b207e6ecacf78e014bf3ac167665309182ce681fd768839e49742b744547999`. Time-origin offset does not change the equal-normalized-progress segment proof; the refinement names its object more precisely and adds no multichannel-phase or whole-clip preservation claim. No additional formula or runtime evidence is required.
