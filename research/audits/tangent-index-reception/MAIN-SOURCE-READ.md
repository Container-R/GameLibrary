# Main original-source reading: corner output versus vertex sharing

2026-11-01. Main directly read Morten S. Mikkelsen's fixed author repository `mmikk/MikkTSpace` at `3e895b49d05ea07e4c2133156cfa94369e19e409`:

- `mikktspace.h` lines 1–130, including license, version label, input and output callbacks. Git blob `52c44a713c60ebff71133a41e0711bbf7199fc5e`.
- `mikktspace.c` lines 390–420, 965–1007 and 1144–1185: per-corner output, derivative/orientation calculation and orientation-aware grouping. Git blob `0342ae0146f1e14854ad8d3309bbbc3d27adc9bc`.
- Khronos glTF specification at `59ecbdba704206bb656965ab4e202881806066f1`, `specification/2.0/Specification.adoc` lines 1800–1840: conditional tangent generation, same-triangle W guidance and bitangent convention. Git blob `e5088cdc9a4e344e836568f57e2db6726f5a6740`.

The author header's unindexed output warning is directly relevant to reception; it does not forbid resolving input face corners through an existing index list. The requested draft must keep this distinction. The C sections establish the relevant output/orientation/grouping branches, not a proof of every algorithm path. Degenerate geometry and quad triangulation are outside the finite example.

The main integrator independently checked the proposed two faces: both geometric windings point +Z, while their UV signed areas have opposite signs. Their stated local parameterizations have the same +X tangent and opposite bitangents. With N=+Z and B=(N cross T)w this requires different signs to preserve those two frames. It proves a representation conflict at shared old slots, not observed generator bytes, a rendered seam or an exporter defect. A six-record reconstruction is one explicit finite remap, not a universal vertex count or welding tolerance.

Existing `tangent-handedness-normal-transform.md` was read in full; it concerns transformation of an already supplied basis. The new reception problem occurs before that phase. A future source-only cross-link must leave all prior analysis unchanged and must not inherit any neighboring model/import evidence.

No generator, model, exporter, engine, shader, render or GPU was executed. No source bulk or assets are proposed for redistribution.

Main read the full draft and requested one prepublication wording refinement: the glTF clause addresses a conditional case, rather than prohibiting generation in other cases. Final note `76c1f632fed1b78f4dd70c19534d12c88f4aee2bacdeed3cc02aafd17de03da8` differs from `216eff076d5570c94433fcc0fdacdfe0605a779b9b4476fa8ba2c9d9eca9d937` only by that clause; the inverse patch was verified. Geometry and explicit six-record mapping were checked by direct reasoning, not execution.
