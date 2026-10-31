# Original interleaved glTF → Godot runtime mesh data

2026-10-31. One original 160-byte embedded buffer, four vertices, two indexed triangles. This extends the manual accessor experiment with an actual `GLTFDocument.append_from_file` call and readback from `ImporterMesh` and its converted `ArrayMesh`. It does not execute the editor import pipeline or render a scene.

## Reproduce and inspect

Create a fresh external disposable directory and copy **only** `run.py`, `main.gd`, `project.godot`, `contract.json`, and `mesh.gltf` into it. Run `python /path/to/fresh-copy/run.py` with the recorded Godot binary available. The runner writes beside its copied source: do not run it inside the archived original or historical directories, because it replaces their result files. Preserve the archive before reproduction. `GODOT_BINARY` may select another executable, but a different binary is a new environment, not reproduction of the archived byte identity. Only Python standard library is required. The runner isolates HOME/XDG, bounds the child to 30 seconds, saves raw stdout/stderr and process status, requires exactly one result payload, and writes `results/summary.json` only after all acceptance checks. It removes previous summary before the optimized-invocation guard and binary inspection. Interpreter startup, parse errors, permissions, or failed cleanup itself are not covered by that freshness guarantee. Timeout retains partial child output. Source hashes are recorded before execution and checked again after the child; `SHA256SUMS` is an archival receipt, not a signed provenance guarantee.

`contract.json` was frozen before code with SHA256 `c1e6f75c30861650ab0c65590ded2ba136f2aba1686f4677c3cd9b83c42e5f58`. `mesh.gltf` is a byte-identical copy of the earlier original fixture, whose files remain unchanged. The runner separately verifies the exact JSON and decoded-buffer hashes, source attribute set and original index bytes. No downloaded model, installation, mesh edit, or replacement geometry was used.

## Actual current result

- Runtime import return code 0; one GLTFMesh, one node, three accessors, two buffer views, one 160-byte buffer.
- One TRIANGLES surface at each stage, actual classes ImporterMesh and ArrayMesh.
- Positions exactly `(1,2,3), (5,2,3), (1,8,3), (5,8,3)` at both stages.
- Source indices `[0,1,2,2,1,3]`; both imported stages `[0,2,1,2,3,1]`, matching the literal pre-run winding-conversion expectation. Mathematical triangle cross-product Z is -24, while supplied normals remain near +Z. These are distinct winding and normal conventions, not a requirement to invert source normals.
- ImporterMesh normals exactly +Z; ArrayMesh readback contains approximately `(3.66e-10,-3.05e-5,1)` for each vertex. The frozen component tolerance of 1e-4 accepts this finite numerical difference. This is not bit-identical normal storage, nor a measured visual error.
- UV channel absent in original and both stages; no UV correctness coverage.
- Observed ArrayMesh format is retained as a string to avoid precision ambiguity. Observed AABB position `(1,2,3)`, size approximately `(4,6,1e-5)` is diagnostic, not an exact geometry-storage oracle.

## Preserved first failure and correction

`historical-zero-depth-aabb/` preserves the first source version, frozen contract/input, raw process result and failing runner output. That engine process exited 0 and produced the expected imported arrays, but the first runner added an unfrozen assertion that a planar ArrayMesh AABB must have exactly zero depth. Actual depth was approximately 1e-5, so the **full first runner failed**. No first-run PASS receipt existed.

The original source gate promised to record AABB, not require zero depth. After preserving and reporting the failure, the corrected runner removed only this extra assertion; the frozen positions, normals/tolerance, winding, primitive and absent-UV checks did not change. One fresh actual import with corrected runner passed. Counts: two author import processes across history, one current accepted case; the separate version probe is not an import case. No claim that the initial failure was an engine defect.

A subsequently inspected [pinned source comparison](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/servers/rendering/rendering_server.cpp#L451-L458) computes a points AABB then clamps its size with SMALL_VEC3. This supports why exact zero depth is an inappropriate universal assumption; it does not authenticate the installed build. Initial lookup at the old `servers/rendering_server.cpp` path returned 404; directory inspection located the actual `servers/rendering/rendering_server.cpp` path. No fallback branch/source was substituted.

## Identity, sources and scope

Binary SHA256 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`; version-only self-report `4.6.3.stable.official.7d41c59c4`. Runtime full hash differs from the public source comparison tag `35e80b3a8822a9df9be390814b62f44c0a9c69e8`. Installed build provenance remains unverified; “official” is self-reported, not independently authenticated. See `version-probe.json` and current summary.

See [source gate](source-gate.md) for exact Godot 4.6 API sections, pinned glTF span/stride requirements and pinned importer winding/remapping lines. This result closes one actual runtime data-read boundary, not generic glTF conformance, malformed-input security, editor `.import` settings, DCC exports, UV/tangent/material/skin/animation support, GPU upload layout, rendering correctness or performance. Two readback stages are not two independent importers. No scene generation or physical traversal was tested. Independent review repeated one actual import on the same binary and checked raw payloads with a separate literal geometry/hash oracle. Three seeded-PASS startup/receipt negatives (optimized Python, missing binary, malformed synthetic result) rejected without any Godot import. These are receipt-integrity checks, not additional asset cases. See `review/REVIEW.md` in the integrated archive; locally the review is retained separately under `research-drafts/deep-qa/godot-gltf-import-boundary/`.
