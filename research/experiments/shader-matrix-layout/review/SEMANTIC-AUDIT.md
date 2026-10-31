# Frozen assembly dataflow and mutation audit

2026-10-31. Separate additive audit; original author/reviewer sources and outputs unchanged. Executed `python3 research-drafts/deep-qa/shader-matrix-layout/semantic_audit.py`, exit0; stdout/stderr and semantic-audit-output.json preserved. Zero compiler/native/GPU runs. Two existing assemblies accepted, seven deliberate mutations each rejected (14 synthetic rejects, not14 shader tests).

## Actual dataflow inspected in both assemblies

Named Params type contains one mat3; named member0 is transform. `%params` is Uniform pointer to Params. Integer `%int_0` is0. `%18` accesses that variable's member0; `%19` loads mat3 through `%18`. `%23` is the vec3 constant composed from1,2,3. `%24` performs OpMatrixTimesVector with `%19` and `%23`. `%26` accesses member0 of `%output_data`, whose Uniform pointee is the named Output struct with value member0 of vec3 type; `OpStore %26 %24` stores that product. Actual block/member decorations distinguish row/column storage while the logical dataflow remains the same.

This closes the earlier reader's narrower “some OpMatrixTimesVector exists” witness for these two frozen outputs. It is not a general def-use analysis, SPIR-V validator, optimizer equivalence proof or GPU behavior observation. Exact identifier and line checks deliberately depend on this actual emitted assembly; harmless compiler renaming would reject and need a new reviewed oracle, not silently generalize.

## Mutations

Per assembly: flip major, change MatrixStride16→32, rename Params block, rename transform member, change first host float1→2, disconnect matrix load from member pointer, change output store from matrix product to vector constant. Each fails a specific independent literal-contract check; all details in JSON. The last two show an operation merely existing cannot satisfy the witnessed dataflow. Mutated text is synthetic corruption, not necessarily a valid compilable SPIR-V module; no claim these variants compiled or ran. Host mutation affects CPU interpretation only.

All offsets and expected logical rows/product are literal in the independent checker, not imported from author contract/reader. Original accepted host records still decode to rows(1,2,3),(4,5,6),(7,8,10), product14,32,53. No changes to accepted runtime conclusions; no material integration blocker.
