# Independent pre-implementation literal oracle

2026-11-01 UTC. Read only the frozen protocol at `research-drafts/gltf-accessor-depth-gate/protocol.md` (SHA prefix `de8c9bd7`). No author decoder/runner/result was inspected. No fixture bytes were generated, decoded or parsed; no Python, engine, native library or numerical test was run. These files are hand-written expected evidence, not recorded execution output.

## Manual checks

The three displayed byte groups contain 16 + 8 + 20 = 44 bytes. The first four little-endian binary32 words correspond to hexadecimal bit patterns 41200000, 41a00000, 41f00000, 42200000. With positive sign and the IEEE binary32 significand/exponent interpretation these are 10, 20, 30, 40. The sparse value words have bit patterns 40e00000 and 41100000: respectively 1.75 × 2² = 7 and 1.125 × 2³ = 9. The little-endian uint16 index words 01 00 and 03 00 give 1 and 3.

Index addresses are 16 + 2 + 2j = 18, 20. Values addresses are 24 + 4 + 4j = 28, 32. Index span ends at view-local 6 (absolute 22); value span ends at view-local 12 (absolute 36). Padding is not an element. The index view offset16 and local offset2 are individually divisible by2; value view offset24 and local offset4 individually divisible by4. These are separate requirements, not merely an aligned combined address.

Sparse entries replace destinations1 and3; dense destinations0 and2 retain10 and30. Without a base view, those destinations remain initialized zero despite the unused dense bytes still present in the backing buffer. Addition would instead yield the explicitly wrong [10,27,30,49].

The short-view mutation requires bytes through local exclusive12 but declares length11; the overall 44-byte buffer still contains those bytes. It must reject at the view boundary. The five frozen negative cases contain four distinct error labels because duplicate and descending indices share the strict-increase category. No additional malformed case has been added or run.

`expected.json` can later be consumed by an independent read-only result checker. Its values must not be revised from author output. This oracle does not claim full glTF validation, floating-point metadata normalization, mesh/morph semantics, importer behavior, rendering or security.
