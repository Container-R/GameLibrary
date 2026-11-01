# Frozen sparse-accessor CPU protocol

2026-11-01 UTC. Protocol only: no decoder, binary generation, execution or native calls. Gate SHA256 `505821cc5c2e00f56958126afcff9d11ca65810eb2e165d17e1cceca492b65c0`; normative source fixed to Khronos glTF `59ecbdba704206bb656965ab4e202881806066f1`.

## Exact original backing bytes

44 bytes, little endian. Spaces/newlines below are presentation only. This is the intended immutable hexadecimal fixture, not a recorded output:

```
00 00 20 41 00 00 a0 41 00 00 f0 41 00 00 20 42
ab cd 01 00 03 00 ef 12
aa bb cc dd 00 00 e0 40 00 00 10 41 11 22 33 44 55 66 77 88
```

Address contract:
- base view0: offset0 length16, FLOAT SCALAR count4; addresses0/4/8/12 → 10/20/30/40.
- index view1: offset16 length8, no target/stride; sparse index offset2, componentType5123; addresses18/20 → 1/3. Padding16–17 and22–23 is not decoded.
- values view2: offset24 length20, no target/stride; sparse values offset4; addresses28/32 → FLOAT7/9. Padding24–27 and36–43 is not decoded.

## Exact two configurations

Shared JSON members:

```
{
  "asset": {"version": "2.0"},
  "buffers": [{"byteLength": 44}],
  "bufferViews": [
    {"buffer": 0, "byteOffset": 0, "byteLength": 16},
    {"buffer": 0, "byteOffset": 16, "byteLength": 8},
    {"buffer": 0, "byteOffset": 24, "byteLength": 20}
  ],
  "accessors": [{
    "componentType": 5126, "count": 4, "type": "SCALAR",
    "sparse": {
      "count": 2,
      "indices": {"bufferView": 1, "byteOffset": 2, "componentType": 5123},
      "values": {"bufferView": 2, "byteOffset": 4}
    }
  }]
}
```

Dense configuration adds accessor `bufferView:0, byteOffset:0`. Zero-base configuration adds neither field. Both remain without extensions, meshes or normalized encoding. During eventual serialization, buffer.uri will be the data URI embedding exactly the frozen44 bytes; this member is omitted above solely to keep pre-code hexadecimal readable. Only this local self-authored data URI will be decoded; no arbitrary URI/network/file fetch.

Independent expected output:
- dense: `[10,7,30,9]`;
- zero-base: `[0,7,0,9]`.

Both sparse maps are destination1←value-address28 and destination3←value-address32. Unselected dense indices0/2 retain addresses0/8 values10/30. Unselected zero-base indices0/2 are initialized zero, not fetched from unused dense bytes. Replacement is not addition. The deliberately wrong additive dense result `[10,27,30,49]` is a counterexample, not an allowed alternative. No mesh POSITION or morph evaluation is performed.

## Five required rejection probes

Each changes only a private copy of the dense configuration/input; exact error category must be recorded separately from successful decoding.

1. Replace uint16 index at20 with1: duplicate `[1,1]` → `sparse_indices_not_strictly_increasing`.
2. Replace indices at18/20 with3/1: descending → same category.
3. Replace index at20 with4: `[1,4]` → `sparse_index_out_of_range`.
4. Change values-view byteLength20→11: last4-byte value at relative8 ends12, exceeds view11 even though backing buffer44 remains → `sparse_values_view_bounds`.
5. Add `byteStride:4` to index view1 → `sparse_view_layout_forbidden`.

These are five planned negative cases, not an exhaustive malformed-input suite. No runtime counts exist yet.

## Selected metadata policy and checks

Normative integer-valued JSON numbers need not have integer lexical spelling. **This fixture adopts a deliberately narrower strict-Python-int metadata subset**, rejecting bool and float values even when a float represents an exact integer. Such float rejection must be labelled `unsupported_metadata_number_encoding`, never “invalid glTF”. For example `4.0` or `4e0` may be valid glTF integer-valued JSON encodings but are outside this reader. This policy avoids pretending safe generic numeric normalization has been implemented.

Selected metadata bounds: one buffer44 bytes, three views, one accessor; no extensions/mesh; FLOAT SCALAR only; accessor count1..4, sparse count1..accessor count; only uint16 sparse indices. Require nonnegative strict-int offsets and view indices, buffer index0, views contained in actual buffer, separate alignment of each bufferView byteOffset AND its sparse-local byteOffset to the indices/values component size2/4 (an aligned sum alone is insufficient), sufficient per-view spans, finite FLOAT data, tightly packed sparse views with no target/stride, increasing in-range sparse indices. Dense base offset/component alignment and span checked; absent-base accessor must omit byteOffset under this subset. Sparse values share accessor component type/dimension. Optional unsupported fields should fail explicitly rather than silently change interpretation.

These are intended code invariants to inspect, **not additional individually executed tests** or a schema/validator-completeness claim. If additional probes are later proposed, freeze and count them separately. Existing old reader's policies/results remain untouched.

## Planned execution and receipts, only after authorization

New isolated fixture directory, preserving old dense and Godot evidence byte-identically. Freeze implementation source hashes before any run. One bounded standard-library runner serializes/reloads the two self-authored configurations and embedded bytes, decodes with the new finite reader, checks literal values/addresses, then runs the five mutations. Independent reviewer uses literal oracle without author decoder imports for expected values. Public evidence text-only: JSON, hex/base64, sources, stdout/stderr, exit and summary hashes.

Clear prior terminal summary before imports/work and reject optimized execution before decoder import. Unexpected output or exception retains raw failure, emits no successful summary and stops; no expected-value revision to match output. No installs, native libraries, engine, GPU, arbitrary glTF security, production throughput or rendering claims. CPU acceptance establishes only this finite representation contract. Protocol review precedes implementation; implementation review precedes any execution.
