# Independent finite texture payload review

2026-10-31 16:16 UTC. No material issue in declared scope. Read proposal, README, model and runner. Copied frozen model/run to fixture/ and ran `PYTHONDONTWRITEBYTECODE=1 python3 research-drafts/deep-qa/texture-block-budget/fixture/run.py > research-drafts/deep-qa/texture-block-budget/run-output.txt 2> research-drafts/deep-qa/texture-block-budget/run-stderr.txt`; exit0. Actual 14 numeric cases, six input guards, six wrapped BC1 CPU decodes and one strict length-negative, not GPU/compressor/BC7 decoding. Proposal remains historical unimplemented plan; README explicitly limits implemented interface to full chains.

Source hashes: model `cea6af8ac132485f7492ee60ab1019daaf9f690257bafc62d989fcfdc5697544`; runner `d821626c603c48c4b02c21e1384a6fd0f808c034172e11e61aff9a0435637c64`. Raw stdout has exactly one RESULT_JSON matching saved summary; source hashes match copied files. Runtime self-reports Python3.12.14/Pillow13.0.0; original getdata deprecation warning retained verbatim in run-stderr.txt, not suppressed.

## Independent oracle

Ran `python3 research-drafts/deep-qa/texture-block-budget/check_raw.py research-drafts/deep-qa/texture-block-budget/fixture/results > research-drafts/deep-qa/texture-block-budget/independent-output.json` successfully. Checker imports no author module. Literal byte offsets, lengths and RGB565 block endpoint bytes independently match full file and six wrappers; each wrapper payload equals the corresponding full-file slice. Actual Pillow load plus complete RGB byte comparison checks every logical pixel using fixed expected colors, not model.MARKERS or summary PASS. This adds six independent CPU decode calls, not another GPU/API test. Same decoder dependency is not independent codec implementation.

Strict base64 decode matches full binary1792bytes and pinned SHA `1e8f263dbf5aafe04b26626ba7b17ef9ec455337d2f8fed3ddcdbcf145e2f20f`; payload1664+legacyheader128. Six wrappers match recorded SHA; truncated artifact exactly omits last8bytes. Independent literal sizes and prefix offsets check all14 numeric records. 17x17 BC1 is200+32+8+8+8=256, less than200*4/3; 4x4 full24 is greater than8*4/3. Neither constant direction universal. Truncation rejection is bespoke checker length validation, not evidence of decoder rejection or generic DDS parsing.

## Primary-source comparison

Independently fetched exact GitHub commit `ec66b78b37389e8373a8e14ccc3cd29be94146b3` files via plugin:
- https://github.com/microsoft/DirectXTex/blob/ec66b78b37389e8373a8e14ccc3cd29be94146b3/DirectXTex/DirectXTexUtil.cpp#L908-L973 : ordinary BC branches round block counts upward and multiply8/16, distinct legacy bad-tail mode. Model agrees with normal branch; Python integers do not validate C++ overflow behavior.
- https://github.com/microsoft/DirectXTex/blob/ec66b78b37389e8373a8e14ccc3cd29be94146b3/DirectXTex/DirectXTexImage.cpp#L47-L72 : accumulated slice pitches and per-axis floor-halving above1. Source comparison only, no DirectXTex execution or runtime-source authentication.

Independently read https://learn.microsoft.com/en-us/windows/win32/direct3ddds/dx-graphics-dds-pguide (DDS File Layout/Variants) and https://learn.microsoft.com/en-us/windows/win32/direct3d10/d3d10-graphics-programming-guide-resources-block-compression (creation condition/Virtual Size versus Physical Size), accessed2026-10-31. Supports legacy128 vs DX10-extended148 description, block-rounded pitch versus runtime pitch, and base creation restrictions versus small mip logical dimensions. No claim that17x17 numeric-only example creates a D3D resource. Did not repeat all other source-gate pages; this audit does not represent independently reading them.

No evidence for GPU allocation, upload footprint, residence, streaming savings, visual quality or general-purpose compression. Header128 applies to this BC1 legacy artifact, not a BC7 DDS promise. Main/original fixture and remote untouched; reviewer outputs only.

## Full article editorial acceptance — 2026-10-31 16:36 UTC

Read `research-drafts/texture-block-budget/solution.md`, SHA256 `031f59d632d3d2cfe6b085b87465209632eb4c6b1f6a8b93bafb7de9e0e972aa`. No material issues; no runtime repeat. Six-level table has208 blocks,1664 payload bytes,128-byte description and1792 total, with reviewed offsets/colors. Numeric-only17x17 high-estimate counterexample and4x4 low-estimate counterexample are correctly scoped; not GPU-created artifacts.

Five measurement layers distinguish tight payload, container/package, upload footprint, resource allocation and observed residence. Package compression is excluded from implemented evidence, despite being a useful proposed budget category. Runtime/API facts are source-backed definitions and requirements for future measurements, not invented device observations. Base-resource legality is not inferred from CPU decoder success or small mip wrappers. BC7 remains arithmetic-only; header128 is confined to legacy BC1 artifact.

Counts and provenance match reviewed final fixture, including14 numeric cases,6 invalid guards,6 author wrapped decodes, strict truncated length rejection, same-decoder independent repeat, warnings and historical six-pair stage. No new GPU, compressor, image-quality or frame-time evidence. Proposed cross-role acceptance is labeled original.

From intended `solutions/rendering/block-compressed-mip-budget.md`, three existing article/role links normalize to existing main-tree targets. The experiment README link is correctly shaped but awaits copying the approved fixture to `research/experiments/texture-block-budget/`; it is not presently available in main staging. This expected integration dependency is not represented as an already-published link. Integrator should resolve before publication. Main staging and remote untouched.
