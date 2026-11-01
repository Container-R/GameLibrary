# Main tangent-basis source and exact algebra read

2026-11-01 UTC. Read pinned Khronos glTF Specification.adoc at `59ecbdba704206bb656965ab4e202881806066f1`, lines 1660–1665, 1813–1830 and 2195–2204. Local tangent sign and bitangent reconstruction are distinct from instantiated triangle winding. The same-triangle equal-w wording is SHOULD, with differing signs making tangent space undefined; do not silently promote SHOULD to MUST.

Read Khronos glTF-Sample-Renderer `6e8a3d1aaa6f07e9f1310a488453e21325677786`: renderer.js 1835–1862; primitive.vert 83–114 and 120–161; material_info.glsl 124–192. Chosen branch has supplied normals/tangents and no skinning, morphing, instancing or normal-UV transformation. Normal and tangent transforms differ. Fragment reconstruction normalizes interpolated columns and separately handles facing and sampled normals; no rendered outcome follows from inspecting one vertex expression.

Hand-checked positive diagonal example: normalized inverse-transpose normal (1,2,0)/sqrt(5) is perpendicular to transformed tangent (2,-1,0)/sqrt(5); transforming the normal with the same forward matrix instead produces normalized (2,1,0)/sqrt(5), whose tangent dot product is 3/5. The counterexample is exact independent algebra, not an executable model or shader test. Local w sign changes the reconstructed local bitangent direction.

Recommend this positive-scale proof as the core, without converting the separate negative-scale construction into a universal determinant correction or a claim that the reference renderer is defective. No figure, asset, renderer, importer, numerical code or visual inspection was used. Existing format/import evidence is not tangent-frame evidence.

Sources: [fixed specification](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc), [fixed renderer source](https://github.com/KhronosGroup/glTF-Sample-Renderer/tree/6e8a3d1aaa6f07e9f1310a488453e21325677786). No implementation body or private execution metadata is reproduced.
