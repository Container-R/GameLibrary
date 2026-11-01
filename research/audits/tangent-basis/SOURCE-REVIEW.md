# Tangent basis — independent source and algebra review

2026-11-01 UTC. **ACCEPT the narrow positive-scale mechanism**, not a universal reflection correction. Reviewed gate SHA256 `3185ac748a2aa95a215ac372732d679393e1f300b7cc0c74f7ba5977f7e54bca`.

## Original sources checked

Independently fetched the official fixed files and commit identities:

- Khronos glTF `59ecbdba704206bb656965ab4e202881806066f1`, committer timestamp 2026-10-30T15:21:59Z: Specification.adoc 1661–1662, 1813–1829, 2196–2203. Normalized N/T.xyz and signed tangent.w, local bitangent reconstruction, and instantiated winding are distinct contracts. The same-triangle equal-w statement is SHOULD; differing w makes its tangent space undefined.
- Khronos glTF-Sample-Renderer `6e8a3d1aaa6f07e9f1310a488453e21325677786`, committer timestamp 2026-10-26T13:36:59Z: renderer.js 1835–1862; primitive.vert 83–114 and 120–161. The selected static, non-morphing, non-skinned path uses inverse-transpose for normal and model matrix for tangent; bitangent is cross(normalW,tangentW) times input w, then normalized. Front-face winding is separately selected. Commit timestamps identify revisions, not a universal renderer-release contract.
- Additionally read [material_info.glsl getNormalInfo, 124–192](https://github.com/KhronosGroup/glTF-Sample-Renderer/blob/6e8a3d1aaa6f07e9f1310a488453e21325677786/source/Renderer/shaders/material_info.glsl#L124-L192): the supplied-TBN branch normalizes interpolated columns; back-facing triangle handling negates all three; a sampled tangent-space normal is remapped/scaled/normalized and multiplied by that basis. This supports distinguishing basis transport from the later reconstruction chain. It does not establish visual correctness of every shader variant. A guessed separate normal.glsl path returned 404; the actual reconstruction inspected is in material_info.glsl.

The current MODEL article's verification metadata was read directly. Its existing format/import and sparse evidence does not test this tangent-frame question. No old native evidence is inherited.

## Independent exact hand derivation

For N=(1,1,0)/sqrt(2), T=(1,-1,0)/sqrt(2), w=1, cross(N,T)=(0,0,-1). With A=diag(2,1,1), inverse-transpose N before normalization is (1/2,1,0)/sqrt(2), and AT=(2,-1,0)/sqrt(2). Hence normalized N'=(1,2,0)/sqrt(5), T'=(2,-1,0)/sqrt(5), dot=0 and cross=-Z. In contrast normalized AN=(2,1,0)/sqrt(5) has dot(T')=(4-1)/5=3/5. Both candidate normals have unit length, so a length-only acceptance check cannot distinguish the wrong transformation in this example. This is exact algebra, not executed numerical or rendering evidence.

For R=diag(-2,1,1), normalized inverse-transpose N=(-1,2,0)/sqrt(5), normalized RT=(-2,-1,0)/sqrt(5), cross=+Z while RB=-Z. The stated mismatch is correct **only as a comparison of two specified constructions**. It is not evidence that the reference renderer is defective or that every receiver must multiply w by determinant sign. A transported-bitangent objective and a reconstructed frame convention must first be specified; full material, reflection and face-orientation behavior is not proved here.

## Publication constraints

Prefer the positive diag(2,1,1) counterexample as the substantive result, with local w preservation and world-space normal/tangent contracts stated separately. Keep reflection a scope boundary, not a repair recipe. Select the branch without morphing, skinning or normal-UV transformation; interpolated bases, shear, singular/near-degenerate cases and rendered normal-map appearance remain outside the hand proof. No Gram–Schmidt or universal implementation recommendation follows automatically.

A standalone safe note is useful and non-duplicative. It should not rewrite legacy articles, reproduce figures/source bodies, claim measured artifacts, or include runtime/private metadata. No code/model/shader/renderer execution occurred; no material correction to the bounded algebra is required.
