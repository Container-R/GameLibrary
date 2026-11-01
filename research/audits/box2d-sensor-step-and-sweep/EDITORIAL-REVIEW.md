# Editorial review: Box2D sensor occupancy and traversal

2026-11-01. Accepted unchanged as a standalone source-only note.

Reviewed `research/source-notes/box2d-sensor-step-and-sweep.md`, SHA-256 `23e50a2eb011aea2f602466d5fdfcaf2161b3d6fb623d759fe2f306f94e5e0a7`, plus its source gate, independent source review and main reading. No linked runtime records were read, and no existing solution was edited.

## Independent source spot-check

Reopened official fixed v3.1.1 source at `8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3`: world.c 735–793, sensor.c 47–106, solver.c 212–245 and 425–450, and simulation.md Sensors and Ray-casts / Shape-casts sections. Reopened newer fixed source at `dd8bd3fb525f0f33f1079f8ca3c5770783c44a53`: simulation.md 1071–1103 and solver.c 138–215, 295–312 and 542–550. These checks support the selected control-flow, query and final-filter distinctions. Tag resolution, the newer fast-shape exclusion and broader context were also assessed through the separately recorded source reviews; this editorial pass did not repeat every source-gate lookup.

## Adversarial checks

- Historical scope is adjacent to the actual claim. The post-solve overlap pass and continuous-path exclusions support the limited v3.1.1 conclusion, not a present-day statement that all Box2D sensors lack continuous detection.
- The circular-object crossing is explicitly an assumed actual straight path, not an engine-generated trajectory or observed missed event. The note does not claim substeps leave every final pose unchanged. It expressly prevents reuse of this geometry as a counterexample to the newer static-sensor path.
- Newer support is acknowledged rather than obscured. Candidate filtering, bounded temporary storage and final strict fraction filtering do not become unlimited capture, nearest-result retention, blocking response or delivered begin/end ordering guarantees. The selected main commit is not called a released version or proven website deployment.
- The actionable decision is more specific than a general fixed-step caveat: identify occupancy versus traversal, select an available version-appropriate detection path, then define volume and interval coverage. Engine continuous detection remains an option where supported; the text does not prescribe redundant custom casts universally.
- The proposed checks remain unexecuted. Center rays are not equated with finite volume, finer world steps are not solver substeps, and freezing a moving target is not asserted to solve relative motion. Initial overlap, multiple results and ordering are explicit responsibilities rather than an implied complete trigger algorithm.

## Publication and evidence limits

The new note does not inherit model or Godot runtime evidence. Source summaries are compact, and links identify exact source revisions rather than copied code or bulk documentation. The proposed geometry and receiving decisions are distinguished from observed results. No private execution identifiers or host-specific runtime metadata occur in the reviewed note.

No build, physics run, model execution, trajectory generation, image/video analysis or private evidence inspection was performed. Acceptance covers only this note and its finite source-based choice of detection responsibility; it is not a certification of complete collision coverage or all Box2D event behavior. No correction is requested.
