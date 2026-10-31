# Baked clearance, avoidance radius and physical occupancy are different inputs

2026-10-31. Two original headless Godot processes actually baked and queried navigation plus stationary physics overlaps. First execution passed both cases; no failed probe or tuning run occurred. No character traversal or RVO output was executed.

## Frozen geometry and actual observations

contract.json SHA256 `9c296194fcb61c8193ac7c7169ad0edc4329a51aa02b45058c47bbe4fd1d3ec8` was frozen before implementation/execution. Original y=0 floor: left room x[-6,-2],z[-4,4], bridge x[-2,2],z[-1,1], right room x[2,6],z[-4,4]. Six triangles supplied through NavigationMeshSourceGeometryData3D.add_faces; no precomputed nav polygons or manual A*.

The faces follow Godot clockwise input convention. Inspected pinned add_faces implementation reverses indices; parsed source triangle cross products are +Y. The gate's earlier shorthand “upward triangles” is made precise here: input ordering and internally stored source indices are not identical. This was resolved from source before code, not after a failed bake.

Same geometry/settings, only NavigationMesh.agent_radius changes between fresh processes:

| Actual bake radius | Generated polygon/vertex counts (observation) | Agent radius0.2 | Agent radius1.2 |
|---|---|---|---|
|0.2|22 / 24|path reaches right-room goal|same path reaches goal|
|1.2|24 / 28|nonempty partial path ends at x=-2.5|same partial path|

Both agents have avoidance_enabled=false. The tested setter therefore does not establish actual avoidance performance or output. Each independent NavigationAgent3D node updates via get_next_path_position in a physics callback, and its actual get_current_navigation_path / final position are recorded; these are not radius-free map queries presented as agent behavior. Parent nodes remain stationary. Source inspection and this finite configuration support separation of agent avoidance radius from baked topology, not all settings/variants.

Projected start/goal are (-4,0.2,0)/(4,0.2,0) in this binary, with small floating differences in returned paths. Bake voxelization lifted the generated surface; this is observed rather than silently resetting Y to0. Expected acceptance uses endpoint tolerance0.01, not exact generated vertex/path count or a guessed polygon sequence. In each case both radius settings yield equal actual paths; mesh vertices/polygons before/after are identical. Large-bake goal still projects into the surviving right room, so this is not merely a target outside all navigation surfaces.

## Physical controls are stationary occupancy, not movement

Two StaticBody3D walls occupy x[-2,2],y[0,4],z[1,4] and[-4,-1], dedicated collision layer2. They align with the bridge's XZ side limits. Floor triangles, not wall colliders, are the bake source; free-edge erosion of the bridge supplies clearance. No claim that the baker parsed those physics bodies.

Actual PhysicsDirectSpaceState3D.intersect_shape at (0,1.5,0), margin0:
- Sphere radius0.2: no wall overlap.
- Sphere radius1.2: both named walls overlap.
- Positive control sphere radius0.2 at (0,1.5,2.5): WallPositive overlap.

Both bake processes return these same controls. Collider identities/shape indices and actual wall size/position/layer are logged. Sphere center Y is explicitly an elevated body-shape center, not the navigation point Y; only the corridor XZ cross-section is being compared. No simulated body was moved to this position, no collision response or sweep occurred. Small overlap-free occupancy does not prove the entire route is safe; large overlap shows that this stationary shape cannot occupy the corridor center without intersecting these walls. No floor collision, capsule, rotation, step height, skin, gravity or moving obstacles.

## Readiness and reproducibility

Run `python3 run.py` with existing `/usr/local/bin/godot`. Isolated HOME/XDG per process, headless/single-threaded-scene, project selects GodotPhysics3D; output retains backend setting and version. Explicit bake settings in contract include cell_size/cell_height0.1, height1, climb0.2, slope45, region_min_size/merge_size0, edge/detail parameters. Resource getters are compared against requested values. Bake completion callback plus nonempty polygons are required before upload.

Map/region use explicit non-async iteration, enabled layer1 and no inter-region edge connection; independent map RID, one region, no links/alternate routes created. Owned map_changed signal plus nonzero changed map iteration and nonzero region iteration gate queries; runner verifies actual ownership/layers/config. Physics positive control must become visible before proceeding. A240-physics-callback watchdog is a failure limit, not proof waiting any fixed number makes data ready. Actual readiness tick1 in these runs is not guaranteed. Agent queries occur in the next physics phase after creation/target setup; no force_update or sleep.

run.py records initial hashes of all five live sources in results/summary.json, records exact binary hash, Python/platform, commands and exits. SOURCE_JSON includes source faces and parsed arrays; BAKE_JSON contains generated polygons/vertices; RESULT_JSON records actual paths/settings/overlaps. Current invocation.json ID/state must agree with summary; old PASS removed before -O or optional engine work. Handled timeouts preserve partial output; spawn errors preserve receipt. Early-failure per-case artifacts may remain and are not proof of a completed current run. No generic filesystem/interpreter-startup atomicity claim.

Actual outer run exit0, empty stderr; both child processes exit0, empty stderr. Source freeze: main.gd a344ab34…, run.py baaeeee9…. Independent review accepted: a fresh same-binary copy repeated two bakes/four paths and independently checked literal floor geometry, winding, path endpoints/readiness and actual overlap membership. Three synthetic seeded-PASS startup failures (-O, missing engine path before spawn, /usr/bin/true with no records) were rejected with FAILED invocation/no summary; zero Godot executions in those negatives. [Independent review](review/REVIEW.md) retains its own copied fixture and outputs. No extra unique behavioral cases inferred from repeats. Exactly two bake processes with two agent paths each, not four separate bakes; physical controls within each process are not character traversal tests.

## Sources and installed identity

Official Godot4.6 pages read2026-10-31; navigation classes marked Experimental:
- [NavigationMesh.agent_radius](https://docs.godotengine.org/en/4.6/classes/class_navigationmesh.html#class-navigationmesh-property-agent-radius): erosion and cell-size rounding.
- [NavigationAgent3D.radius](https://docs.godotengine.org/en/4.6/classes/class_navigationagent3d.html#class-navigationagent3d-property-radius): avoidance footprint, not normal pathfinding radius.
- [Using NavigationAgents](https://docs.godotengine.org/en/4.6/tutorials/navigation/navigation_using_navigationagents.html): custom parent movement and avoidance output are separate responsibilities.
- [NavigationServer3D](https://docs.godotengine.org/en/4.6/classes/class_navigationserver3d.html): code-source bake APIs and asynchronous synchronization; avoidance ignores regions.
- [NavigationMeshSourceGeometryData3D.add_faces](https://docs.godotengine.org/en/4.6/classes/class_navigationmeshsourcegeometrydata3d.html#class-navigationmeshsourcegeometrydata3d-method-add-faces): clockwise triangle input.
- [PhysicsDirectSpaceState3D.intersect_shape](https://docs.godotengine.org/en/4.6/classes/class_physicsdirectspacestate3d.html#class-physicsdirectspacestate3d-method-intersect-shape): stationary overlap; motion ignored. Unlike cast_motion, not using a sweep that ignores initial overlaps.

Pinned official comparison35e80b3a8822a9df9be390814b62f44c0a9c69e8:
- [agent setter607–615](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/navigation/navigation_agent_3d.cpp#L607-L615).
- [baker radius353–372](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/navigation_3d/3d/nav_mesh_generator_3d.cpp#L353-L372) and [erosion480](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/navigation_3d/3d/nav_mesh_generator_3d.cpp#L461-L482).
- [source face-index reversal180–193](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/resources/3d/navigation_mesh_source_geometry_data_3d.cpp#L180-L193).

Actual binary SHA256 f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3, self-report4.6.3/7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3. Public tag comparison remains distinct; self-reported official is not authenticated origin. No GPU, device, general reachability/optimality guarantee, dynamic RVO, moving-body collision safety, performance or other build/platform claim.
