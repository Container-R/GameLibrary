# glTF accessor → actual Godot import data gate

2026-10-31. Source/protocol only; no import or new geometry fixture executed. Read recovered original modeling solution and mesh-attribute-contract geometry/asset. Original sources/results remain unchanged.

## Feasibility and exact existing input

Existing asset is a complete glTF2.0 scene with one mesh/primitive, embedded160-byte data URI, four interleaved POSITION/NORMAL records and six indices. No input wrapper amendment is needed. input-identity.json verifies JSON SHA256 `883939499a958e58d1fff1041345ca2b8819f2febf7a43f8447b2ec09d91d50b`; decoded buffer SHA256 `06572d2d89cac7d7dc8c9586ecde6325b82fe0615dfe0e5d4236d7e37a16f268`, identical to archived mesh.bin.base64.

Fresh isolated HOME/XDG version-only command `[本地可执行文件路径已省略] --headless --version` exited0, stderr empty. Self-report `4.6.3.stable.official.7d41c59c4`; actual binary SHA256 `[安装指纹已省略]`. Matches prior byte identity after workspace recovery, but does not authenticate official build provenance. The public source comparison tag still resolves to35e80b3a…, not the self-reported hash. version-probe.json is actual receipt; no executable installation.

The actual available engine plus documented GLTFDocument → GLTFState → GLTFMesh.mesh(ImporterMesh) → ArrayMesh route makes a useful bounded capability test feasible. Runtime import availability/readback under headless remains unexecuted and must be tested, not assumed. If dummy/headless mesh readback is unavailable, preserve that boundary rather than silently switching to a manual reader and calling it engine import.

## Sources actually read

Godot4.6 documentation accessed2026-10-31:
- [GLTFDocument](https://docs.godotengine.org/en/4.6/classes/class_gltfdocument.html), append_from_file / generate_scene: imports into supplied state, returns Error; state owns imported data, document otherwise processes it. Runtime API is not the editor .import pipeline.
- [GLTFState.get_meshes](https://docs.godotengine.org/en/4.6/classes/class_gltfstate.html#class-gltfstate-method-get-meshes) enumerates imported GLTFMesh records; get_nodes/root_nodes/scene generation are separate scene aspects.
- [GLTFMesh.mesh](https://docs.godotengine.org/en/4.6/classes/class_gltfmesh.html#class-gltfmesh-property-mesh) is ImporterMesh, not directly ArrayMesh.
- [ImporterMesh](https://docs.godotengine.org/en/4.6/classes/class_importermesh.html), get_surface_arrays / get_mesh: original importer surface arrays versus usable ArrayMesh conversion; get_mesh caches its output. No edits/LOD generation proposed.
- [ArrayMesh](https://docs.godotengine.org/en/4.6/classes/class_arraymesh.html), front-face clockwise convention; [Mesh](https://docs.godotengine.org/en/4.6/classes/class_mesh.html), arrays/primitive attributes. No renderer output follows from data inspection.

Pinned glTF spec59ecbdba704206bb656965ab4e202881806066f1 reread [accessor span/stride requirements](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#L1310-L1375): bufferView-relative accessor offset, per-element stride, final span offset+(count-1)*stride+element size; component alignment; shared interleaved vertex attributes require byteStride. Original fixture vertex view offset16/length112/stride28, accessor offsets4/16; indices in separate view128/12. Whole backing-buffer length is not a replacement for declared view bounds.

Pinned Godot source comparison35e80b3a8822a9df9be390814b62f44c0a9c69e8 actually inspected [gltf_document.cpp1469–1526](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/gltf/gltf_document.cpp#L1469-L1526): POSITION decode, index decode, triangle winding conversion swaps second/third indices, used-vertex mapping, POSITION/NORMAL decode. [1692–1698](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/gltf/gltf_document.cpp#L1692-L1698) remaps indices to used-vertex positions. This source comparison motivates a prospective winding oracle; it is not guaranteed exact installed implementation.

## One fixed actual-runtime protocol if approved

1. Copy the existing mesh.gltf byte-for-byte into an isolated new fixture; verify JSON and decoded160-byte hashes before execution and after. Do not regenerate or rewrite original input to satisfy an importer.
2. Fresh headless engine process, isolated HOME/XDG, no imported resources loaded through ResourceLoader or editor .godot cache. Call GLTFDocument.append_from_file on that copied file with fresh GLTFState, explicit flags0/base path. Record actual return code first; on failure emit available diagnostics/state counts and fail. A successful process exit alone is not import acceptance.
3. Enumerate actual state meshes/nodes/accessors/bufferViews/buffer lengths. Require exactly one GLTFMesh and its nonnull ImporterMesh; enumerate actual surface count/type and arrays. Call ImporterMesh.get_mesh once without custom base_mesh, record returned class/null and independently read its ArrayMesh surface arrays. This tests two data stages, not two independent importers. Scene generation is optional only if separately selected; no need to expand to scene rendering.
4. Freeze literal geometry before code: POSITION [(1,2,3),(5,2,3),(1,8,3),(5,8,3)], NORMAL all(0,0,1), four vertices, six indices, TRIANGLES. Proposed installed-engine index expectation is [0,2,1,2,3,1], deliberately different from source[0,1,2,2,1,3] because inspected import path reverses triangle winding. All vertices are used, so the inspected remap preserves their order. Preserve actual arrays; if reorder occurs, do not quietly sort to pass—classify the failed exact expectation, then decide whether a separate explicit semantic-topology comparison is warranted.
5. Require POSITION exact finite values (small representable integers), NORMAL within a predeclared1e-4 component tolerance at ArrayMesh stage, and exact expected indices/primitive. The normal tolerance is a bounded project oracle, not a glTF/Godot guarantee; raw numeric error remains visible. Check both reconstructed triangles use the intended vertex sets and that engine's clockwise index order yields negativeZ mathematical cross products while provided normals remain positiveZ. Do not call that convention change a corrupted asset or invert original NORMAL to make cross product agree.
6. Preserve raw import code, actual resource classes/counts, arrays/types/format flags and AABB; compare ImporterMesh and ArrayMesh stages, not only final summary. Original Python naive stride12 error remains historical model evidence; no need another invented wrong importer here. No malformed-asset importer rejection claim is planned.
7. Independent literal checker must not import original reader or derive expectations from actual engine output. Runner fresh-summary/-O/error/timeout controls as existing fixtures; preserve any surprising failure and input hashes. One actual original-input import process first, then independent reviewer same-input repeat; stop there unless a material failure requires separately approved diagnosis.

## Engineering value and limits

This would close the existing article's explicitly excluded engine-importer data boundary for one original interleaved indexed primitive and show why raw index equality across format conventions is not the right universal invariant. It does not prove editor import settings, DCC export, GPU rendering, tangents/materials/UV/skin/animation/compression, general glTF validity/security, performance, cross-version behavior or full scene assembly. No general parser or third-party model needed. Do not relabel source accessor bytes as ArrayMesh physical GPU layout.

> 公开衍生说明：本次仅省略安装位置、安装指纹或执行记录标识，并调整现址/固定历史链接；技术观察、失败、计数与原有证据范围保留。正文中的“本次”及身份相等陈述均属于原记录时点，本轮未重新检验，未运行旧实验，原始摘要声明不改写为新字节。文中描述性记录别名不是可执行目录名。
