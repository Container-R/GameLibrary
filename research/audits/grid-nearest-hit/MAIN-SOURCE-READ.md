# Main source gate: grid traversal and closest-hit termination

2026-11-01. Read the textual NVIDIA GPU Gems3 Chapter22 by Diogo Teixeira / Move Interactive, including projection/cage, uniform-grid discussion, data layouts, displayed shader listings, multipass and antialiasing sections. No figures or performance charts inspected, no timings adopted. The displayed intersection helper is missing; a complete-application defect cannot be inferred from the fragment.

The official chapter links a CD directory that returned404 and a public ZIP at `https://http.download.nvidia.com/developer/GPU_Gems_3/CD/GPU_Gems_3_code.zip`. The ZIP server advertised372950317bytes and ordinary byte ranges. Main fetched only the final65557bytes and168031byte central directory, verified206responses/ranges, parsed1181directory entries. Its content directories include01,02,03,04,06,08,10,12,13,14,16,17,18,20,21,26,29,30,31,33,36,37; no22or bake-named entry appeared. This checked package does not provide a chapter22 implementation path. No full archive or executable was downloaded, extracted or run. Directory absence does not prove no code exists elsewhere.

A stronger positive source chain is the author-host PBRT second-edition Chapter4 PDF, linked directly from pbrt.org, plus author repository pbrt-v2 fixed commit `e6f6334f3c26ca29eba2b27af4e60fec9fdc7a8d`. Main read complete grid.cpp and primitive.cpp, with Triangle::Intersect interval check read separately. The original book directly explains the multi-voxel primitive issue and the next-boundary comparison. Main read extracted text at physical4/printed186,23/205,25/207; web screenshot cache failed, so downloaded the public PDF and locally rendered/viewed physical23and25. No page images or source archive will be published.

The fixed source identifies a historical pbrt-v2 implementation, not current pbrt or an installed binary. Commit author date2014-10-18 and committer date2019-01-05 identify its history, not a release date or the introduction of this grid algorithm.

Accept further drafting of a finite nearest-hit versus any-hit decision, with original exact geometry and explicit complete-overlap/full-triangle intersection assumptions. The NVIDIA chapter motivates the question; PBRT supplies the positively inspected termination mechanism. No allegation against NVIDIA's uninspected full implementation, no general renderer certification, no runtime result, and no copying of full listings or PDF pages.

## Exact final article review

Read the complete article with SHA-256 `da1e8e8de357dc6ad5b30320e1f2632d0eed9e066467e0f1c4f5de86ddc2ee56`. Main accepts the strict sufficient termination proof under conservative complete lists, complete candidate handling and ordered ray intervals, and independently verifies both nonboundary intersections. The article expressly separates a historical PBRT source mechanism from the uninspected complete NVIDIA implementation; it does not claim either application was run or a bug reproduced. The five receiving checks remain proposed, not passed. Opaque/unmasked two-sided assumptions close the winding ambiguity identified during drafting.

Fixed source blob identities: `grid.cpp`=`a84a451a5df86c89155edb42358cbc78e0e5e6c2`; `primitive.cpp`=`5195f60944cb70c827f6f32b8d6b8c6d21176819`; `trianglemesh.cpp`=`a8ca79142f6bc84df80616948286903cf8c695e9` at the recorded commit. These identify original source artifacts, not binaries or executed tests.

PDF source identity: SHA-256 `430d5d019e9ffe731df2b3fcf7911992097ac0b10faa26fc675d45f259fb00d6`. This is the downloaded public source document, not an execution binary.

Main independently checked the geometry: A's centroid is(5/2,1/2,1/2), with t=9/4. The combination0.9A0+0.05A1+0.05A2=(0.8,0.84,0.5) is strictly inside the first unit cell. B's weights(1/4,1/4,1/2) give(3/2,1/2,1/2), t=5/4. Neither hit lies on a triangle edge or cell boundary. Requested explicit unmasked, opaque, two-sided intersections because the two triangles have opposing windings; no real baker culling policy is inferred. This is exact hand reasoning, not a ray tracing run.

## Exact final article review

Read the complete article with SHA-256 `da1e8e8de357dc6ad5b30320e1f2632d0eed9e066467e0f1c4f5de86ddc2ee56`. Main accepts the strict sufficient termination proof under conservative complete lists, complete candidate handling and ordered ray intervals, and independently verifies both nonboundary intersections. The article expressly separates a historical PBRT source mechanism from the uninspected complete NVIDIA implementation; it does not claim either application was run or a bug reproduced. The five receiving checks remain proposed, not passed. Opaque/unmasked two-sided assumptions close the winding ambiguity identified during drafting.

Fixed source blob identities: `grid.cpp`=`a84a451a5df86c89155edb42358cbc78e0e5e6c2`; `primitive.cpp`=`5195f60944cb70c827f6f32b8d6b8c6d21176819`; `trianglemesh.cpp`=`a8ca79142f6bc84df80616948286903cf8c695e9` at the recorded commit. These identify original source artifacts, not binaries or executed tests.
