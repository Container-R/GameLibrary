# Frozen original geometry and source gate — 2026-10-31

Before implementation: two triangles on z=3 plane. POSITION literal [(1,2,3),(5,2,3),(1,8,3),(5,8,3)], NORMAL all(0,0,1), indices[0,1,2,2,1,3]; both triangles point +Z. Bounds min[1,2,3], max[5,8,3]. No DCC export or GPU rendering.

Binary layout:16-byte prefix; vertex view offset16,length112,stride28. Four records each padding float99, POSITION3f, NORMAL3f. Position accessor offset4; normal offset16; count4. Index view offset128,length12,ushort SCALAR count6,no stride. Backing buffer total160bytes,20trailing bytes. Thus POSITION last end100relative and NORMAL last end112relative. View shortage can be rejected despite large backing buffer.

Naive example uses correct first POSITION address20 but tight12-byte increment rather than28; its reads stay inside declared vertex view, yet recover normals/padding mixed with positions. This is misinterpretation of a valid fixture, not evidence that the original asset is invalid.

Khronos glTF official repository immutable commit59ecbdba704206bb656965ab4e202881806066f1 (committer2026-10-30T15:21:59Z), read2026-10-31 via GitHub plugin. Specification.adoc lines1109–1129 buffer span/stride;1310–1375 accessor addressing/span/alignment;1701–1747 finite attributes,POSITION bounds,equal counts,unsigned SCALAR indices,range and forbidden maximal index. Schemas accessor.schema.json and bufferView.schema.json read at samecommit; constrained reader is not a full schema validator.

https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc
https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/schema/accessor.schema.json
https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/schema/bufferView.schema.json

Limited subset: one supplied binary buffer, one mesh/primitive TRIANGLES, FLOAT VEC3 POSITION/NORMAL, UNSIGNED_SHORT SCALAR indices, no extensions/sparse/normalized/matrices/skin/animation/externalURI resolution. Checks selected semantics and finite bounds, not generic adversarial parser or official-validator certification. Exact byte validation plus intended numeric geometry/topology are separate checks.
