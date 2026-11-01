# Main source inspection: Detour synchronous path result

Read 2026-11-01. The main integrator independently read these original files at `recastnavigation/recastnavigation` commit `6dc1667f580357e8a2154c28b7867bea7e8ad3a7`:

| File and range | Returned Git blob |
|---|---|
| `Detour/Include/DetourStatus.h` 22–63 | `8e1bb44b9dc9525efbac1d0b34fa98a99254b591` |
| `Detour/Include/DetourNavMeshQuery.h` 162–201 | `101b3c852257d9c968982dd7ad751c8ae151518b` |
| `Detour/Source/DetourNavMeshQuery.cpp` 171–223, 973–1204 | `cebe26b5d0363c5131dfdd7026227344714594f7` |
| `Detour/Source/DetourNode.cpp` 121–151 | `48abbba6b5b256e0b03c97c35cee780b379e8c8a` |

Original [tag reference](https://api.github.com/repos/recastnavigation/recastnavigation/git/ref/tags/v1.6.0) identified annotated tag object `b4554541b658630816dba41466eb1cefb624519e`; its object was separately opened and resolves to the pinned commit. Commit metadata was separately read: author/committer date 2023-05-21. This is a historical selected version, not a latest-version assertion.

The prospective note's distinctive question is output-buffer truncation versus search-node exhaustion. The main pass followed the complete selected synchronous `findPath` body through result extraction, rather than inferring its behavior from enum names. It also traced the hypothetical three-node parent chain through the extraction loop symbolically; no Detour query or compiled model was run.

A prepublication precision check added the documented positive, bounded initial node capacity and valid reference/position pairing as preconditions. An initialization return value alone is not permission to ignore documented parameter limits. The planned caller policy is deliberately conservative and separate from a claim of geometric reachability, physical arrival or cost optimality.

No navigation mesh, engine wrapper, sliced query, crowd simulation, straight-path query or prior runtime archive was inspected or executed. Existing navigation articles remain unchanged; their runtime results are not evidence for this new note.
