# Published source-note batch — bounded adversarial technical review

2026-11-01 UTC. **No material correction found in the four checked notes at the specified snapshot.** This is a negative result within an explicit source/math scope, not whole-repository clearance or runtime validation.

## Snapshot and reviewer overlap

Fetched and read all four complete remote files from `Container-R/GameLibrary` at commit **`5e0531d7f258099d4170ce9fd72e8e516d6bd35b`**, not merely local drafts. Paths below are relative to `research/source-notes/`; SHA256 hashes bind the fetched UTF-8 text.

| File | SHA256 |
|---|---|
| `mesh-simplification-request-result.md` | `edd71b9565b0f5697bd23284c3f4c2fdfcc4ccc132f31e3fb4c64a05712514e5` |
| `pso-precache-first-use-acceptance.md` | `ed0c121f64fb9eac67dbec0d704dbd797b50c489d16c4a7e4ebe904d84c89710` |
| `input-disable-teardown-callback.md` | `784a088cf0b652ab898ba23564020cb75437fe08bb6d8b5bef849963cd24050f` |
| `tangent-handedness-normal-transform.md` | `59b3b75a5c7f8a50fb24fe09293c69ea7ef50ce925e6bde0f69f740350e19615` |

This reviewer previously reviewed the simplification/QEM sources and helped author the PSO and tangent notes. Accordingly this is **not a wholly fresh, author-independent review** of those three topics. The present pass checks the published versions adversarially, reopens selected primary evidence, and separately traces the Unity callback mechanism. No articles or remote files were changed.

## Claims challenged and findings

### 1. Simplification request/result, including QEM

**Attempted counter-reading:** the smaller request might be presented as a guaranteed smaller output; isolated planar zero might masquerade as the library's returned error, or its point P as an actual collapse destination.

**Finding:** neither transfer occurs. Both request results remain unknown. The capacity and actual index-count distinction matches the [fixed v0.25 header](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/meshoptimizer.h#L432-L448). Reopened `simplifier.cpp` at the same pin: rescalePositions 546–599, quadricError/construction 765–819, default vertex and conditional edge terms 1046–1141, stop loop 2421–2465, return/wrapper 2554–2565. These support the stated full-array scale and stopping boundaries, not an output guarantee.

Independently rechecked the hand argument: x≤1 on the stated triangle makes `(2−x)²+y²≥1`, with equality at (1,0); z² is zero at P. The note explicitly excludes P as an established candidate and keeps default point/border terms prominent. Reopened [original Garland/Heckbert PDF](https://www.cs.cmu.edu/~garland/Papers/quadrics.pdf), physical page 6, §7 final paragraph: the infinite-plane/finite-face distinction is actually there. Earlier §5/§6 source review and the current exact algebra support the limited interpretation. PDF text, not new visual figure inspection. No surface/mesh/Hausdorff or silhouette measurement is claimed.

### 2. PSO first-use acceptance

**Attempted counter-reading:** all three responses could be invented enum values; a zero counter or shader-only result might be promoted into complete coverage; shipping diagnostics or cache retrieval could become a universal performance promise.

**Finding:** published prose correctly names strategy 0/1 and its prerequisite, while leaving blocking as the separately documented possibility. Reopened [Epic's 5.6 manual](https://dev.epicgames.com/documentation/en-us/unreal-engine/pso-precaching-for-unreal-engine?application_version=5.6), Component / Proxy Creation Delay Strategy, Loading screen, Memory and Validation and Tracking (full text previously read). TrackMinimalPSOs dependency, current outstanding scope, and the conditional shipping Untracked→Missed wording are retained. The proposed new combination is not declared missing or slow. The visual-policy table asks for component support rather than asserting universal fallback support. No implementation, atomic counter or benchmark claim is smuggled into the manual reading.

### 3. Input disable/teardown callback

**Attempted counter-reading:** cancellation could be deferred, enabled could already be false inside it, the application could release different objects, or the repair could promise exception-safe shutdown.

**Finding:** the explicit Started, default Value/no-interaction, same-preview, single-thread, no-other-mutator and normal-return premises make the double-release walkthrough valid. Reopened [official 1.11 API page](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.11/api/UnityEngine.InputSystem.InputAction.html#UnityEngine_InputSystem_InputAction_Disable), which identifies 1.11.2, and exact commit `c8518694c7fdd2c755755e028e2ec19cdceda19b`:

- [InputAction.cs](https://github.com/Unity-Technologies/InputSystem/blob/c8518694c7fdd2c755755e028e2ec19cdceda19b/Packages/com.unity.inputsystem/InputSystem/Actions/InputAction.cs#L916-L935), plus enabled 532 and Dispose 789–802.
- [InputActionState.cs](https://github.com/Unity-Technologies/InputSystem/blob/c8518694c7fdd2c755755e028e2ec19cdceda19b/Packages/com.unity.inputsystem/InputSystem/Actions/InputActionState.cs#L824-L881), also 1071–1082, 1958–1967, 2408–2416 and 2491–2569: cancellation/listener dispatch precedes Disabled under the selected premises. Destroy 227–265 has an assertion, not a general safe-rejection guarantee.
- [CallbackArray.cs 41–75](https://github.com/Unity-Technologies/InputSystem/blob/c8518694c7fdd2c755755e028e2ec19cdceda19b/Packages/com.unity.inputsystem/InputSystem/Utilities/CallbackArray.cs#L41-L75) and [DelegateHelpers.cs 36–59](https://github.com/Unity-Technologies/InputSystem/blob/c8518694c7fdd2c755755e028e2ec19cdceda19b/Packages/com.unity.inputsystem/InputSystem/Utilities/DelegateHelpers.cs#L36-L59) support deferred removal and caught listener exceptions.

The repair's neutralization operation is explicitly non-releasing/non-state-changing, and exceptions/destruction are explicitly excluded from its guarantee. The note does not mistake enabled for shutdown reason or claim a crash was reproduced. No material missing premise identified for the illustrated path.

### 4. Tangent handedness/normal transform

**Attempted counter-reading:** normalized vectors might be mistaken for correct directions; ordinary glTF instantiation might be excluded accidentally; the positive-scale example might imply a universal reflection fix or final normal-map validation.

**Finding:** the published version explicitly says only shader USE_INSTANCING is disabled, not ordinary node instantiation. Reopened [fixed spec Using Primitive Data](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#L1813-L1830) and [fixed vertex branch](https://github.com/KhronosGroup/glTF-Sample-Renderer/blob/6e8a3d1aaa6f07e9f1310a488453e21325677786/source/Renderer/shaders/primitive.vert#L120-L161); earlier directly read renderer.js 1835–1862 supplies the normal-matrix construction. No-morph/no-skin/no-normal-UV-transform supplied-attribute selection remains explicit.

Rechecked by hand: `(1,2,0)·(2,−1,0)/5=0`, wrong-normal product `(2,1,0)·(2,−1,0)/5=3/5`, each candidate unit length. The local sign loss is distinct from direction transport. Reflection and interpolated/material output remain expressly outside the proof. No exporter failure or rendered result is alleged.

## Review limits and disposition

This pass fetched the four exact published notes, reopened the decisive primary branches above, and manually challenged their examples. It did not rerun historical archives, execute code/model/audio/engines, inspect rendered figures, or certify other library content. Mutable Epic documentation remains version-labelled rather than commit-pinned; that limitation is disclosed in the note. Source inspection is not a substitute for runtime evidence.

**Disposition: retain these four notes as published for this checked scope.** No ceremonial rewrite, new experiment, or scope expansion is recommended solely to produce a finding. New claims about actual assets, first-use performance, callbacks in a different interaction, or full rendering would require evidence beyond this review.
