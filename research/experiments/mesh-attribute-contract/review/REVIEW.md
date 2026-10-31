# Independent mesh attribute contract review

2026-10-31 18:46 UTC. No material code failure within stated supplied-buffer subset. Frozen reader b9b5709b6730c3acaf662112169a28f50e9330ee05bf8208ca1692515d7d3e36; runner499ba210218426691e50597d067e69d2aea39a8bd3bc124d2d2a71041004b8f0; geometry6f5c5009cb93cd875e7919a1becd8f39ceefcbd92ffe0162252766592b3fa329.

Read geometry-contract before deriving check_raw.py. Oracle imports no author reader: literal byte addresses20/48/76/104 for positions,32/60/88/116 for normals,128 for six ushort indices. Each triangle cross product[0,0,24] independently establishes+Z orientation, not rendering or unit normal magnitude. Exact160bytes, embedded/base64 equality, padding99 and trailing/prefix zeros verified. Naive12-byte steps recover[(1,2,3),(0,0,1),(99,5,2),(3,0,0)] entirely in view, not intended positions.

## Executed commands
```
python3 research-drafts/deep-qa/mesh-attribute-contract/fixture/run.py > research-drafts/deep-qa/mesh-attribute-contract/run-output.txt 2> research-drafts/deep-qa/mesh-attribute-contract/run-stderr.txt
python3 research-drafts/deep-qa/mesh-attribute-contract/check_raw.py research-drafts/deep-qa/mesh-attribute-contract/fixture/results > research-drafts/deep-qa/mesh-attribute-contract/independent-output.json
python3 research-drafts/deep-qa/mesh-attribute-contract/negative.py > research-drafts/deep-qa/mesh-attribute-contract/negative-output.txt 2> research-drafts/deep-qa/mesh-attribute-contract/negative-stderr.txt
```
All exit0, stderr empty. Original nine rejection cases repeat with exact expected reasons. Supplemental probe executes two isolated child runner failures (-O and replaced reader import): both actualexit1/no old or new summary; commands/rawstdout/stderr saved under negatives/. Six additional in-process rejection probes: absent view, invalid view index, short view with large buffer, incorrect bounds, nonunit normal, mismatched attribute count. One intentionally accepted structure case redirects POSITION to NORMAL values and updates bounds consistently: structural reader returns different degenerate geometry, independent intended-position expectation disagrees. This is a semantic handoff distinction, not an assertion that such glTF must be rejected universally.

## Source scope independently verified

Fetched via GitHub plugin at immutable Khronos commit59ecbdba704206bb656965ab4e202881806066f1:
- specification/2.0/Specification.adoc:1109–1129 view span/stride;1310–1375 element address/span/alignment;1661 normalized NORMAL semantics;1701–1747 finite attributes, POSITION bounds, equal counts and indices limits.
- specification/2.0/schema/accessor.schema.json and bufferView.schema.json: required fields, bounds, stride restrictions, optional bufferView behavior.

Source URLs use https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/ followed by paths above. Read2026-10-31. Float attributes finite, NORMAL normalized, unsigned scalar index range and forbidden maximal value align with checked clauses. Reader1e-6 norm tolerance is original policy, not specification epsilon. Strict exact float bounds comparison is scoped to authored literal data, not general export-tool numeric robustness.

One documentation qualification sent author: missing accessor.bufferView is not universally malformed glTF; schema permits implicit-zero initialization. This reader requires supplied view-backed data and fails absent field with KeyError. Explicitly exclude implicit-zero accessors when describing subset/missing-view probe; do not call this a format-invalid negative. Invalid numeric view reference and view overrun remain distinct invalid cases. No generic parser/security or official Validator certification.

No GPU/DCC/export/API execution. Historical sourcehash command-size tool failure is separate from successful fixture. Only independent copied fixture/reviewer outputs changed, no main/original/remote writes.

18:46 UTC author README clarification read: explicit view-backed subset and absent-bufferView implicit-zero exclusion now present; KeyError is unsupported subset, not proof of globally invalid glTF. No source/geometry change or rerun required. Accepted for bounded integration.
