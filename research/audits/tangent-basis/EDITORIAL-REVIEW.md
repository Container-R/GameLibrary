# Tangent-basis note: independent editorial review

2026-11-01 UTC. Reviewed complete `research-drafts/tangent-basis-article/source-note.md`, SHA256 `9c3151cbc493bf06d361aa6bd6c21dfc2b1e20f9fdc51ddfa7cbcbc228dd9ec7`, together with the gate and independent SOURCE-REVIEW. No author/staging/legacy changes, numerical execution, rendering or remote writes.

## Verdict

Accept the exact algebra and source/evidence boundaries. Request one narrow scope clarification before final acceptance: replace **非实例化** with an explicit statement that shader **USE_INSTANCING is not enabled**, not that glTF node instantiation is absent. Optional notation **应（SHOULD）一致** preserves the exact normative strength of the same-triangle w condition.

## Independently checked

Reopened the official immutable glTF specification at `59ecbdba704206bb656965ab4e202881806066f1`, lines 1810–1832. The equal-w clause at 1823 is SHOULD, followed by undefined tangent space for differing w; reconstruction follows at 1825–1829. Existing Chinese 应 is not presented as MUST, so this is not a mandatory second correction.

Reopened official immutable glTF-Sample-Renderer `primitive.vert` at `6e8a3d1aaa6f07e9f1310a488453e21325677786`, lines 83–163. Lines 123–129 select the instancing shader branch versus uniform model/normal matrices. Lines 142–159 support the chosen N/T path and separate UV-transform exclusion. Therefore the shader selection must not be phrased as a universal absence of node instantiation.

Independently recomputed by exact hand algebra: the stated local N and T have cross −Z; reversing w reverses B without changing XYZ. For A=diag(2,1,1), normalized inverse-transpose N is (1,2,0)/sqrt(5), transformed T is (2,−1,0)/sqrt(5), dot zero and cross −Z. The normalized direct-transform alternative (2,1,0)/sqrt(5) has dot 3/5 with that T. Both candidate normals are unit vectors. The finite counterexample is correct; no execution is claimed.

The article keeps local attribute specification separate from one renderer implementation and from original mathematical analysis. Positive determinant is explicit; no universal reflected-w fix, negative-scale defect, normal-map appearance result, or complete tangent pipeline correctness is inferred. Source paraphrase remains compact; the central derivation and handoff table are original. Links to older format/import and matrix-layout evidence are framed as non-transferable, not as supporting a tested tangent-frame implementation. No private runtime identifiers or machine provenance appear.

Pending only the precise USE_INSTANCING wording and final content hash.

## Final acceptance addendum

ACCEPT final article SHA256 `59b3b75a5c7f8a50fb24fe09293c69ea7ef50ce925e6bde0f69f740350e19615`. Independently read the revised wording. Reversing only the explicit USE_INSTANCING scope, the ordinary-node-instantiation clarification, and SHOULD parenthesis exactly reproduces the initially reviewed hash `9c3151cbc493bf06d361aa6bd6c21dfc2b1e20f9fdc51ddfa7cbcbc228dd9ec7`. No mathematical, source, evidence or execution claim changed. No further correction requested.
