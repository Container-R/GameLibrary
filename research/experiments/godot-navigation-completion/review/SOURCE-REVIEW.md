# Independent navigation-agent path-consumption gate

2026-11-01 01:10 UTC. Source gate accepted for a bounded protocol, not execution. No Godot/version call, fixture implementation, model or test run.

## Sources directly read

- Godot4.6 NavigationAgent3D class description, methods and signal definitions: https://docs.godotengine.org/en/4.6/classes/class_navigationagent3d.html . Experimental status and recursive-update warning retained.
- Godot4.6 Using NavigationAgents, Pathfollowing: https://docs.godotengine.org/en/4.6/tutorials/navigation/navigation_using_navigationagents.html . User code moves the parent; an agent is not a collision locomotion controller.
- Public comparison commit35e80b3a8822a9df9be390814b62f44c0a9c69e8, scene/3d/navigation/navigation_agent_3d.cpp, lines705–923,984–1000 and internal physics notification near313, fetched through GitHub connector: https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/navigation/navigation_agent_3d.cpp .

Pinned code confirms that several getters call the navigation updater; no per-frame guard appears in that path. It samples parent position on each applicable call. Target distance and waypoint distance use strict less-than; reachable endpoint comparison uses less-than-or-equal. The reachable branch emits target transition before finish; an unreachable final waypoint can finish without target transition. Finish clears submitted-target state. Internal physics notification handles avoidance/velocity bookkeeping rather than independently consuming path positions.

## Baseline and distinct value

Read current SOL-AI-001 metadata and inspected old radius main.gd position/query sites. The existing article's verification_method explicitly excludes character movement; stationary Node3D parents and static shape overlaps do not establish consuming a route or receiving terminal signals. The proposed controlled parent position assignments would add actual path-following state observations while remaining distinct from CharacterBody3D, collision response, physical arrival or mission success.

## Requirements before freezing the protocol

1. Treat every updating getter as a possible state transition, not a passive same-frame snapshot. Do not rely on tutorial wording about physics cadence as proof of a code-level once-per-frame guard. Call the movement-driving getter in the named pre-assignment phase; never add an updating getter after assignment in the same frame unless a separate observation phase is explicitly frozen. Passive path/index/target-reached accessors can be distinguished by source; no updating getters in signal callbacks.
2. Callbacks record identity/name/frame/position only and do not move parents, reset targets or query state recursively. The target callback occurs before the finish transition, so do not assume its navigation-finished state already equals the eventual post-call state.
3. Freeze original polygon winding, map up vector, edge/link configuration, layers, height offset, distances, fixed maximum displacement, readiness predicate and callback/deadline bounds. Read back actual map/region/agent membership and settings. Initial path geometry and disconnected endpoint are runtime gates, not invented waypoints; fail rather than repair topology or widen tolerances after observing it.
4. Stay strictly inside or outside threshold boundaries. Trace pre-call position, returned next point, passive path/index state, assignment and next callback. The driver must move only toward returned path points. Stop active updates using terminal signal latches; a finite final window supports only bounded signal counts, not eternal nonduplication.
5. Freeze both-route expectations independently of the observed result: reachable target signal then finish; disconnected route finish without target signal while far from requested target. Mission-level success remains a separate original policy choice, not an engine guarantee.

The two isolated rectangles with avoidance off are a feasible source-grounded candidate, not proven installed behavior. Preserve installed-binary/source identity caveat; matching self-report does not authenticate comparison-source correspondence. First unsupported readiness/topology/parse/error/oracle result must be retained and stop this branch without automatic variants. Separate protocol/code acceptance and native authorization remain required.
