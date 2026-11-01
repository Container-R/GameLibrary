# Color-space depth triage: correct alpha association does not select the working transfer function

2026-11-01. **Source/capability gate only. No Pillow/CMS import, native color-library call, transform, compositing operation, image generation, engine/GPU invocation, installation or new numerical experiment was performed.** Read-only work used stdlib file hashing/text inspection and `/usr/bin/readelf -d` on the existing CMS extension. No main/staging/remote files changed.

## 1. Exact existing evidence and the real gap

Current `gamelibrary-work/solutions/art2d/alpha-association-contract.md` SHA256:
`2fc2423598b2b040c7dadf6e304c575f0e27e37fcca48307f7c9949a78441b70`.

Verbatim verification metadata:

> 固定第一方源码与格式文档核对；原创数值 buffer 的 5 次模式转换和 6 次实际 CPU 合成；无图片作品、引擎或颜色管理验证

Exact existing fixture:

| File | SHA256 |
|---|---|
| `research/experiments/art2d-alpha-contract/run.py` | `7895e68073e93b09eacbd86879baec1d3be6e5bc5be22df65a7307f925e6f74f` |
| `contract.md` | `17537214fca5580d77cea7175472028ac2b26c828be4c9325fde9a4397b773e2` |
| `results/summary.json` | `d7555abc8477253a19c95cb4f68d53b8973bf623578de78eece79cfe94203799` |

The article and actual summary explicitly constrain five groups / five conversions / six composites to stored-channel-byte arithmetic. The selected RGBA↔RGBa examples and alpha 0/255 controls show association/relabeling mistakes and lost hidden RGB. The independent repeat uses the same Pillow. Neither run executes sRGB decoding, linear-light arithmetic, ICC transforms, display measurement or PNG handling. Thus there is **no stale overclaim to repair**. The missing handoff is independent: even when both parties agree on straight RGB and the same alpha, they may perform source-over in different transfer domains.

Useful concrete question: **For an explicitly chosen linear-light working contract, can a correctly straight-encoded sRGB sample be multiplied by alpha directly in stored sRGB coordinates and still match decode → composite → encode?** This is not another premultiplication/relabeling case. The association, source, backdrop and alpha stay fixed; only transfer-domain handling changes.

## 2. Original sources actually read

All access dates 2026-11-01. No publication date is inferred from crawler time.

| Original source | Version/date and exact section | Supported boundary / caution |
|---|---|---|
| [W3C SVG 2 painting](https://www.w3.org/TR/2018/CR-SVG2-20181004/painting.html#ColorInterpolation) | Fixed Candidate Recommendation, 2018-10-04; §13.9, page lines 973–1008 | Separates sRGB and linearRGB operation spaces and provides the piecewise conversion. Its initial `color-interpolation` value is sRGB: **do not turn linear-light arithmetic into a universal requirement for every authored UI or SVG workflow.** No browser/SVG test proposed. |
| [CSS Color 4](https://www.w3.org/TR/2024/CRD-css-color-4-20240213/#color-conversion-code) | Fixed Candidate Recommendation Draft, 2024-02-13; §17 lines 2995–3052, `lin_sRGB` / `gam_sRGB` | The conversion examples are explicitly non-normative. They provide an independent comparison route for bounded nonnegative sRGB values, not an executable claim or a substitute for arbitrary ICC profile behavior. |
| [Compositing and Blending Level 1](https://www.w3.org/TR/2024/CRD-compositing-1-20240321/#simplealphacompositing) | Fixed CRD, 2024-03-21; §5.1 | Existing source-over / straight-associated relationship. It does not by itself choose this project's working color encoding. Avoid repeating the old article's lengthy explanation. |
| [PNG second edition](https://www.w3.org/TR/2003/REC-PNG-20031110/#4Concepts.ColourSpaces) | Fixed Recommendation, 2003-11-10; §4.2 lines 403–412 and §12.2 line 1316 | Historical format distinction: gamma processing concerns color samples, not alpha. No PNG file will be created or parsed, and this historical edition is not represented as the newest PNG specification. |
| [Pillow ImageCms](https://pillow.readthedocs.io/en/stable/reference/ImageCms.html) | Page currently identifies Pillow 13.0.0; `createProfile`, lines 520–536; build-transform profile/mode/intent arguments | Profile creation offers LAB, XYZ and sRGB, not a named linear-sRGB option. A mode name or an sRGB→sRGB transform is not a proof of linear-light compositing. This is a moving stable URL; a later implementation must pin relevant source. |
| [LittleCMS author's color engine page](https://www.littlecms.com/color-engine/) | Undated current product/documentation page; lines 16–26, 61–75 | Establishes official CMM/API documentation and repository route. It is not the API ABI specification and does not establish the installed library's version or provenance. No marketing speed/accuracy numbers are adopted. |

Global scope here is standards + original maintainers, not artificial regional quotas. Further sources should resolve API/ICC semantics, not add unrelated color-management surveys.

## 3. Installed capability: file presence is not runtime validation

`file-inspection.json`, `extra-file-inspection.json` and `imagingcms-dynamic.txt` preserve read-only observations and hashes.

- Existing Pillow `_version.py` declares `13.0.0`; prior accepted fixture self-reported the same version. Current `_imaging` hash still equals the old fixture's `d898ef14…`. This gate did not import Pillow or obtain a new runtime version report.
- `ImageCms.py` exists, SHA `9e161faa0807179b599d8fd7fa1de1078010ba34087201e092a77d7c9194b1fc`; installed source lines 736–780 confirm the same three createProfile choices.
- `_imagingcms.cpython-312-x86_64-linux-gnu.so` exists, SHA `e04cff5147dd848945d2151f7102da62d01cb7ce0021dbc8255fc3047df25a7c`.
- ELF dynamic metadata declares RPATH `$ORIGIN/../pillow.libs` and NEEDED `liblcms2-88eaba2f.so.2.0.19`. The matching vendored file exists, SHA `4cf9f69016c7804bcb4fa56f5bbc55640cb1b7196ac7b93ba29ed9df9bd9ff4d`.
- A **different** system `/lib/x86_64-linux-gnu/liblcms2.so.2` resolves to `.2.0.16`, SHA `a0afaac586186b4e6b06c157e48c49480fde35d671052ee1309f36881a4508e7`. Do not mix its identity with Pillow's declared dependency. Filenames alone do not authenticate releases or prove which bytes a future process loads.
- `/usr/include/lcms2.h` was not present at the checked location. No exhaustive header/profile search or compiler test was performed. No selected, verified linear-sRGB ICC profile is currently part of this proposed fixture.

This is sufficient to justify a **next source/ABI gate**, not to announce an available tested ICC pipeline. The standard ImageCms constructor alone does not close the linear-working-profile gap.

## 4. Recommended bounded experiment direction — not yet a protocol

Recommend one narrow numerical-buffer extension, conditional on source review of a finite LittleCMS path. No artwork, PNG, arbitrary imported profile or general ICC parser.

Prospective original inputs: one nonendpoint neutral straight sRGB tuple `(128,128,128)` with alpha `128/255` over opaque black, plus the same color at alpha 1 as an endpoint control. Keep alpha outside the RGB transfer transform. These are candidate inputs, **not frozen numeric output claims**. Freeze exact profiles, buffer types, rounding, tolerances and literal expected outputs before any code/native call.

Hypotheses to distinguish:

1. In the semi-transparent case, direct encoded-domain multiplication and linear decode → source-over → encode produce different encoded RGB under a declared linear-light contract, despite identical correct alpha association.
2. The alpha-1 control returns the original color within the separately frozen conversion tolerance; it cannot by itself discriminate the domain error.
3. Every branch has the same opaque output alpha; checking alpha or channel count alone cannot establish color-domain agreement.

The valuable native path would create a known sRGB profile and a same-primaries/white-point linear RGB profile using **official, pinned, reviewed LittleCMS C API signatures**, transform only a tiny finite RGB double buffer forward/backward, and compare to an independent piecewise numerical oracle. Ordinary arithmetic remains original host code; the CMM performs color conversion, not alpha compositing. No byte reinterpretation or profile-label change should be called conversion.

Before selecting this path, inspect/pin the official header and relevant profile-creation/transform source; verify pointer lifecycle, structs, pixel-format enums, rendering intent, optimization flags, profile identity/white-point treatment and output precision. Determine how to bind the actually loaded vendored library without accidentally substituting the system copy. No ad-hoc varargs or guessed ABI. If this cannot be safely specified with already installed bytes, stop at source-only analysis instead of installing a tool or claiming a hand-written transfer calculator is an ICC run.

A simpler Pillow direct `alpha_composite` vs explicit arithmetic comparison could be useful pedagogically, but by itself adds no actual ICC evidence and largely repeats the old raw-byte API. **Do not choose that merely to add execution count.**

## 5. Acceptance and stopping boundary

Next decision is source/ABI feasibility, then a separately reviewed finite protocol; no runtime is authorized by this gate. The future protocol must specify whether the target product intentionally preserves encoded-space appearance or requests linear-light behavior. “Different” is not automatically “wrong,” and neither numeric result certifies perceived brightness or image quality.

If approved later: preserve all creation/transform errors, actual library identity, before/after source hashes and native outputs; reject unestablished profiles/ABI rather than widening tolerances after observing a result. Expected ICC-vs-piecewise differences require an a priori justified tolerance and no uncontrolled color adaptation/gamut conversion. Keep the prior alpha fixture bytes unchanged.

Explicitly excluded: GPU blend state, sRGB texture/view setup, engine imports, browser rendering, HDR, wide-gamut gamut mapping, premultiplied filtering, resize/mips/atlas, compositor parity, calibrated display, visual perception, performance or certification. An eventual result would establish only this fixed profile/precision conversion-and-composite contract on identified local bytes.

**Decision:** worthwhile distinct handoff gap, but native feasibility remains conditional. Proceed to the narrow LittleCMS source/ABI gate only if the coordinator selects it; do not write a new article or execute a transformation yet.
