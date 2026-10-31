# ART2D production gap gate: alpha representation at sprite handoff

2026-10-31 19:18 UTC. Discovery/source gate only; **no fixture, compositing call, PNG creation, image edit, engine import or visual result executed**. Recommend one bounded numeric/format experiment after coordinator acceptance, not a broad rendering article or taxonomy-completion exercise.

## Coverage and decision

Read current `gamelibrary-publish-liveops/solutions/rendering/block-compressed-mip-budget.md` and `roles/technical-art/technical-artist.md`; searched existing solution/role text for straight/premultiplied/预乘. No existing matching alpha-representation treatment found in that bounded search. Texture article distinguishes payload/container/upload/allocation/residence and explicitly lacks visual-quality data. TA role supplies asset/material handoff responsibilities, not per-pixel alpha contracts. Proposed work is distinct: **the same byte count, dimensions and alpha channel can survive a transfer while RGB meaning changes**.

Narrow question: a sprite/overlay has premultiplied RGB values, but a receiving RGBA compositor interprets them as straight. The source contribution is multiplied by alpha again. An offline numerical counterexample can identify this contract failure; it cannot establish a real game's visible dark fringe or tell artists all edge artifacts share this cause. Scaling/filtering, atlas bleed and color management are plausible adjacent issues but deliberately excluded from first unit.

Original proposed handoff fields: RGB association (straight/associated), alpha channel, stored color encoding, file format vs working-buffer representation, conversion stage ownership, consuming blend operation and expected probe pixels. Do not label every four-channel byte buffer simply RGBA and infer semantics from that label.

## Read pinned primary evidence

1. W3C **Compositing and Blending Level1**, dated Candidate Recommendation Draft2024-03-21 (not a final Recommendation): https://www.w3.org/TR/2024/CRD-compositing-1-20240321/ §5.1 simple alpha compositing, premultiplied formula and output alpha. Supports algebraic distinction of straight color and alpha-weighted color, not a particular engine setup. Dated version retained for exact reference; not claiming latest normative status.
2. W3C **PNG second edition**, Recommendation2003-11-10, §6.2 alpha representation: https://www.w3.org/TR/2003/REC-PNG-20031110/#6AlphaRepresentation . PNG color values are unassociated. A runtime premultiplied buffer is not the file's declared alpha representation. This is a historical pinned specification edition; no assertion that the edition is current or that every exporter/importer preserves desired semantics. No copied diagrams.
3. Pillow tag13.0.0 resolved through GitHub plugin to commit **293218ad059d994baf1777d882911bed6a49704a**. Read exact files:
   - https://github.com/python-pillow/Pillow/blob/293218ad059d994baf1777d882911bed6a49704a/docs/handbook/concepts.rst lines56–66: RGBA versus RGBa premultiplied mode.
   - https://github.com/python-pillow/Pillow/blob/293218ad059d994baf1777d882911bed6a49704a/src/libImaging/Convert.c lines406–435 and conversion table1499/1505: alpha multiplication and division are conversions, not relabeling bytes. Internal function names alone are misleading; table direction was checked.
   - https://github.com/python-pillow/Pillow/blob/293218ad059d994baf1777d882911bed6a49704a/src/libImaging/AlphaComposite.c : supported modes and integer rounding in source-over implementation. It is not a generic RGBa consumer and not a floating-point color-managed renderer.
   Current public Concepts page also read: https://pillow.readthedocs.io/en/stable/handbook/concepts.html . Page reports13.0.0 today; use commit above for reproducibility rather than stable alias.

All read2026-10-31. Initial unnecessary12.0.0 tag lookup succeeded but is not selected baseline; no retry/access blocker. Installed import-only capability probe reports Pillow13.0.0 and Image.alpha_composite present. No proof installed native module was built from tagged source; archive installed module/interpreter hashes if experiment approved.

## Proposed finite independent oracle, not results

Freeze numeric contract before code, use original tiny raw pixel arrays only (no third-party/user art):
- Straight foreground byte tuple(240,120,60,85), alpha85/255=1/3; corresponding associated tuple(80,40,20,85). Background opaque black(0,0,0,255).
- Correct straight source-over black expected(80,40,20,255). Independent rational algebra, not implementation helper, derives this exact case.
- Deliberately relabel associated bytes as straight RGBA then composite: expected rounded(27,13,7,255), a second attenuation. Verify against separately frozen integer rounding policy/actual implementation; retain mismatch if observed, do not rewrite expected blindly.
- Correctly interpret bytes as RGBa and explicitly convert to RGBA before same compositor: this specially divisible tuple should recover exact foreground(240,120,60,85) and correct output. Do not generalize exact roundtrip to all8-bit low-alpha pixels.
- Controls: opaque input unaffected by association; fully transparent source contributes nothing regardless of hidden straight RGB. Alpha0 cannot be inverted to recover meaningful hidden color after premultiplication; don't divide byzero or claim lossless conversion.
- Optionally one exact synthetic PNG encode/decode to demonstrate stored straight tuple survives and file bytes are separate from runtime RGBa buffer. This is format-test output, not artwork editing. Do not claim PNG records importer blend configuration. Core test can remain raw tuples if format step adds no evidence.

Independent reviewer must read frozen tuples first, derive rational expected values without author helper, compare every output channel and mode, and preserve stdout/versions/source hashes. Limit to a few predeclared cases, plus -O/import-failure freshness. No need thousands of randomized images or new abstraction framework.

## Critical limits / stop rule

Stored8-bit channel arithmetic is not a claim of physically correct linear-light or sRGB compositing. Explicitly keep color-space conversion/ICC/gamma/HDR outside experiment; declare numeric domain. No GPU blend-state, engine importer, mipmapping/filtering, edge dilation, atlas padding, DCC, visibility/perception or platform-performance guarantee. No claim every dark edge is caused by double alpha. No claim premultiplication is universally preferable or automatically fixes all assets.

Proceed only if coordinator wants this representation-boundary evidence. Stop after original finite tuple contract, actual installed Pillow calls, independent oracle and clear negative misinterpretation. If unable to establish actual mode/conversion semantics without widening scope, archive source gate only and deepen existing asset-import acceptance instead. No main/remote edits or executable fixture yet.
