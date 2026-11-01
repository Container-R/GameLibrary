# Clear endpoint versus actual obstructed motion

Original finite CharacterBody3D experiment,2026-11-01. Protocol193a8a05 was frozen before code/native execution. Eight current sources are bound by SOURCE-SHA256.json. No navigation agent, collision controller stack or slide algorithm is tested.

## Geometry and calls

Wall: StaticBody3D center(2,0,0), BoxShape3D size(1,4,2). Two separate CharacterBody3D sphere shapes radius0.5 start at(0,0,0) and(0,0,4). Identity bases, no floor/rotation/gravity integration, unlocked axes, actor layer1/mask2 and wall layer2/mask1; all shapes enabled. A separate sphere query resource uses mask2 and excludes both actor RIDs.

A positive overlap query at wall center establishes actual geometry visibility. Four subsequent stationary queries check both starts and both requested endpoints; all must be empty before any move. On that same actual Node._physics_process callback, each actor calls move_and_collide((4,0,0),false,0.001,false,1) exactly once, Blocked then Open. Blocked acceptance gates Open's call. No test_only, test_move, cast_motion, direct post-call teleport, remainder reapplication or post-move overlap query.

The method argument is a displacement, not velocity. The CharacterBody safe_margin property is recorded independently from the explicit method argument. No slide-specific position_delta/real_velocity getter is used.

## Author observation

UUID44ce134f-f0fc-4316-9097-d99cbd8745f9: first native attempt passed one version query and one behavior process, both exit0 with empty stderr. One readiness attempt, five stationary queries and two actual move calls. Source/binary before-after digests agree.

Blocked actual displacement/travel=(0.9765625,0,0), remainder=(3.0234375,0,0); contact point(1.5,0,0), normal(-1,0,0), recorded depth0.000999927520751953. Open actual displacement=(4,0,0), collision=null. The requested endpoint for Blocked was clear but actual motion stopped before the wall. Returned travel and actual transform delta agree within the frozen tolerance.

The blocked center passes the prospective [0.95,1.05] finite acceptance interval, not an engine precision/error bound. It is not relabeled as ideal1−margin, and no internal cause of the precise fraction is asserted. No post-move occupancy query was performed, so final zero-overlap is not an independently measured result.

Collision object/ID/RID and shape index identify the actual Wall. get_local_shape/get_collider_shape identify the corresponding CollisionShape3D owner nodes, not SphereShape3D/BoxShape3D resource IDs. The actual owner→node/resource mapping and shape indices are recorded. Some observed resource instance IDs are negative signed integers; they are matched as opaque nonzero identities, not assumed positive.

Independent repeat UUID `24fbda1c-b719-4fea-a8de-5d3448c538fe` was accepted with the same finite values. Combined author/reviewer: **2 behavior processes + 2 version queries = 4 Godot processes**, **10 stationary queries and 4 actual move calls**, repeating the same two lanes/configuration, not four unique scenarios. The original independent reader imports no author validator. Both readers pass both archives under normal Python and `-O` (8 main static commands, zero new native calls). Same-binary replication does not establish cross-backend equivalence.

## Review history and archive interpretation

Initial code review added explicit recursive finite checks before configuration comparisons and native queries, and finite post-transform/final-config checks. The accepted intermediate source then received explicit concrete subtype casts at property reads to remove typing ambiguity. Both exact source histories are preserved. No initial native run, parser failure or injected native NaN result is claimed for these source-only revisions.

Seven pure methods cover synthetic motion/shape-owner/query-phase cases, a complete fabricated archive and receipt mutations. Normal/-O suites pass. Each suite launches two guarded Python startup children testing optimized invocation and missing local import; these do not invoke Godot. Author pure logs predate the final cast-only source; main's copied final eight sources and final pure logs separately bind that last revision.

The consumer binds exact sources, commands, environment paths, process status, raw stdout/stderr and parsed payload; its oracle validates actual query parameter/count/visibility phases and both move records, shape-owner identities, transforms and numerical intervals. It does not merely trust the child result. A successful trace does not test native timeout, cleanup failures, arbitrary backend conditions or every malformed schema.

## Read archived evidence without native execution

```sh
python consumer.py . evidence/44ce134f-f0fc-4316-9097-d99cbd8745f9
python -O consumer.py . evidence/44ce134f-f0fc-4316-9097-d99cbd8745f9
```

Static inspection requires archived source/evidence bytes, not the historical absolute paths or installed engine. Independent review documents its own exact source/evidence arguments.

Do not run run.py inside the archive: it removes summary.json and creates a new UUID. A separately authorized native repeat must copy exactly the eight SOURCE-SHA256 names into a fresh disposable directory and preserve bytes, then invoke Python run.py there using the pinned binary. No install, backend/tolerance sweep or automatic retry. Minimal base environment plus the unchanged five-location isolation helper is recorded. Timeout handling attempts bounded owned-process-group cleanup; no universal containment or successful failure-path test is claimed.

## Identity and limits

Binary SHA256 f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3; local self-report4.6.3.stable.official.7d41c59c4. Comparison source35e80b3a8822a9df9be390814b62f44c0a9c69e8 is not authenticated as installed source. Project explicitly selects and reads back GodotPhysics3D; observed singleton classPhysicsServer3D is diagnostic, not independent provider attestation. Hash/raw self-consistency is not execution authentication.

No general CCD/contact-precision theorem, speed/performance benchmark, post-move zero-overlap proof, navigation-to-controller integration, mission arrival, move_and_slide, slopes/stairs/rotations, root motion, dynamic pushing, moving platforms or RVO. The evidence is two finite actual motions against one static geometry configuration.
