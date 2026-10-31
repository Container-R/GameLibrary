# Independent actual-import review

Accepted 2026-10-31 21:09 UTC. Sources unchanged in independent fixture/: runner `a87e064e305b97da04a05eb555422461c12ebcf0879882beecfd9f455f6e0c96`, GDScript `4c3c41e3bc4fa282caecc69a7a24b04188c0a3e11ab66ad6685009b1ab5bbbaf`. Pre-code contract `c1e6f75c30861650ab0c65590ded2ba136f2aba1686f4677c3cd9b83c42e5f58` was read before reviewer execution; independent literal expectations saved in oracle-before-run.md.

## Actual repeat and independent acceptance

Executed `python fixture/run.py` using the full local path, retaining run.stdout/run.stderr and fixture/results. Exactly **one new actual Godot import process** passed. `python check.py` imports no author implementation: it parses the single raw RESULT_JSON and verifies association with parsed result and summary, exact state inventory, resource classes, one TRIANGLES surface at each stage, literal four positions, clockwise indices, mathematical triangle cross Z=-24, supplied normals near +Z within 1e-4 and absent UV. It separately decodes original buffer positions and source indices from literal offsets and verifies input/source/binary hashes. Full hashes/results in check.stdout.

Same binary SHA f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3; runtime identity is self-reported, not authenticated source/build provenance. ArrayMesh AABB observed depth 9.99999974737875e-06, diagnostic only. No scene generation, rendering, editor import, GPU layout or generic glTF correctness claim follows from these two data-read stages.

## Failure history and source comparison

Read historical-zero-depth-aabb/run-output.txt and diffed historical/current run.py. The only acceptance change removes the added exact zero-depth AABB assertion; frozen geometry/normal/index checks are unchanged. Initial full runner failure is retained, not rewritten as a pass or engine defect. Author history has two import processes, one current accepted case; this review adds one repeat, not another geometry case.

Independently fetched through GitHub connector the public source comparison pin `35e80b3a8822a9df9be390814b62f44c0a9c69e8`:
- modules/gltf/gltf_document.cpp, lines 1469–1518: source indices decoded, triangle second/third indices swapped, used vertices mapped in original order.
- servers/rendering/rendering_server.cpp, lines 451–458: points AABB size clamped with SMALL_VEC3.

These source branches support the bounded reasoning; they do not establish the installed binary was built from this pin. No source text copied into this archive.

## Bounded freshness probes

`python negative.py` uses three separate fixture copies, each seeded with an old PASS summary: optimized Python, missing binary, and a fake executable returning malformed RESULT_JSON. All three exit nonzero and remove old summary. Fake executable marker remains absent in first two, present only in malformed-result case. Raw command/exit/stdout/stderr are retained in negative/ and negative-results.json. **Zero Godot processes** ran in these probes; one synthetic executable ran. No timeout injection, startup parse-error coverage or universal cleanup guarantee claimed. Retained ancillary files alone are not terminal acceptance; current summary is required.

No material issue found. Author/main files and remote state untouched.
