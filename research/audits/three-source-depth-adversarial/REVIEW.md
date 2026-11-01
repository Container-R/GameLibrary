# Three source-only notes: bounded adversarial review

Reviewed 2026-11-01 at content commit **`b0ddb66f1c12793b18ae41b40d4f09f804deb2ec`**. Verdict: **no material correction required within the claims and exclusions below**. This is not whole-repository validation or a runtime pass.

The reviewer was not the author or final reviewer of these three additions. All three complete published bodies were reopened at the exact commit. Their remote Git blobs match the separately inspected local snapshot blobs; SHA-256 identities below bind the complete local bodies. Existing audit conclusions were not used in place of original-source reading.

## Artifact bindings

All paths are under `research/source-notes/`.

| File | Remote and local Git blob | Body SHA-256 |
|---|---|---|
| `game-experiment-assignment-and-session-exposure.md` | `c0a975c2ce995f667a8540d02c228bb2a765d801` | `cb15a8f7a436a56fff6386100cc69400c33feea55d3460f4783ca0b9aa5b215d` |
| `lag-compensation-target-and-history-sample.md` | `7221ef84245a3069b07836bd2be91c60d7d58033` | `99e12a7cdb9605a4f6908b698689557274024d6963f601a6a6c0bff6d1ed921f` |
| `tangent-corner-output-and-reindexing.md` | `53c08b10e96dea060d212684de10d02709d543e2` | `76c1f632fed1b78f4dd70c19534d12c88f4aee2bacdeed3cc02aafd17de03da8` |

## 1. Assignment versus session exposure

Independently reopened [arXiv:2402.05336v1](https://arxiv.org/html/2402.05336v1), especially §2, §3.1–3.2, the conflicting direction wording in §4, §5.1/5.3, and §6. The paper separates initial assignment from team-triggered treatment and adds exposure-mapping and joint-unconfoundedness assumptions. Random assignment alone does not establish those assumptions. Its direction inconsistency is real; the note appropriately avoids selecting a universal bias direction.

Adversarial checks of the note's original example: B remains assigned control in both sessions but has exposure `[1,0]`. Relabeling B changes assignment history; removing B conditions inclusion on subsequent experience. Neither operation restores the original randomized comparison merely by producing an unexposed control subset. Equal exposure counts do not reconstruct order, but that information loss alone does not establish an order effect.

The policy paragraph is a question-selection instruction, not a claim that an arm contrast identifies universal rollout impact. It expressly declines estimator validity. Zero-session inclusion and non-independent session records are also acknowledged. **No correction required.** An estimator or rollout recommendation would require a separate, specified estimand and design; richer logging is not causal identification.

## 2. Accepted lag-compensation target versus history sample

Independently reopened Valve's fixed commit `be57e3d01ac7d7aa6a2cacbfef187c0b46616db0`:

- [player_lagcompensation.cpp](https://github.com/ValveSoftware/source-sdk-2013/blob/be57e3d01ac7d7aa6a2cacbfef187c0b46616db0/src/game/server/player_lagcompensation.cpp): inspected history insertion/pruning 245–338, target selection 345–438, search/interpolation/optional collision handling 440–602, field application 599–700, and portions of animation/restoration 726–850. This review does not claim a full-file behavioral audit.
- [shareddefs.h 14–19](https://github.com/ValveSoftware/source-sdk-2013/blob/be57e3d01ac7d7aa6a2cacbfef187c0b46616db0/src/game/shared/shareddefs.h#L14-L19): tick conversion macros.
- [hl2mp_player.cpp 640–659](https://github.com/ValveSoftware/source-sdk-2013/blob/be57e3d01ac7d7aa6a2cacbfef187c0b46616db0/src/game/server/hl2mp/hl2mp_player.cpp#L640-L659): actual Start/base-call/Finish wrapper, not the base hit-query implementation.

Attempted falsification and result:

1. **Could the older command still necessarily select older history?** No. With the note's assumed interval and unclamped correction, the first target is 990 with discrepancy −0.02 seconds; the second initial target 968 has discrepancy −0.24 and is replaced by 992. The strict comparison and rounding macro support the ideal arithmetic. The note explicitly avoids claiming exact floating-point execution or measurements.
2. **Does accepted time guarantee an exact or bracketed history sample?** No. Newer records go to the head only when simulation time increases. The scan stops at a record at/before target, or exhausts history. If all records are newer, its retained oldest record cannot satisfy the interpolation test and is copied. Thus the note correctly rejects universal bracketing rather than inventing a rejection on exhaustion.
3. **Does the worked sample confuse position with pose/hit outcome?** No. Interpolation of the supplied two positions gives x=4 for 9.90; equality at 9.92 selects x=6. Additional pose handling and placement thresholds exist in the source, so the note's term “position candidate” is important. It does not promise all fields share that interpolation or assert a hit result.
4. **Are only outer-loop-selected players ever processed?** No. The enabled fixstuck branch can recursively backtrack a hit player without the outer selection predicate, subject to its current-player and restoration-bit checks. The note says this is optional and disables it in the hand example. It does not claim unconditional recursion or whole-world rollback.

**No correction required.** The hypothetical player's validity and movement checks are assumptions, not experimentally established facts. The inaccessible Valve paper was not retried. No conclusion about commercial releases, dynamic doors, fairness, final hits, or complete restoration correctness was inferred.

## 3. Tangent corner output and complete-attribute reindexing

Independently reopened:

- Author repository [mikktspace.h](https://github.com/mmikk/MikkTSpace/blob/3e895b49d05ea07e4c2133156cfa94369e19e409/mikktspace.h), including input callbacks, output callbacks 79–107, sign convention, and surrounding scope commentary.
- Same fixed [mikktspace.c](https://github.com/mmikk/MikkTSpace/blob/3e895b49d05ea07e4c2133156cfa94369e19e409/mikktspace.c): output loop 401–413, derivative/orientation computation 965–1007, grouping 1144–1183. Healthy triangles retain orientation distinctions; degenerate/group-with-any behavior cannot be generalized from this example.
- Khronos [glTF specification](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#L1808-L1830), fixed `59ecbdba704206bb656965ab4e202881806066f1`, 1790–1840: conditional missing-tangent generation and bitangent reconstruction.

Independent hand inspection of the construction:

- F0's geometric edges are +X,+Y. F1's ordered edges are −Y,+X; both cross products point +Z. The UV determinants are respectively +1 and −1, not a geometric winding reversal accidentally substituted for mirrored UVs.
- The two parameterizations give the same tangent +X but opposite bitangents. With N=+Z, the reconstructed bitangents require opposite w. Matching position/normal/UV or T.xyz is therefore insufficient for sharing a complete tangent-bearing record.
- The six-record table reconstructs F0 as O,X,Y and F1 as O,D,X. Old 0 maps to new 0/3; old 1 maps to new 1/5. No corner is dropped or reordered, and each face receives uniform sign. The second face's D record is correctly new 4, not a duplicate of Y merely because their UVs coincide.
- A single-valued old-index-to-new-index map cannot encode those two splits. Conversely, six separate records are only a sufficient representation for this input, not a universal minimum or a requirement to fully expand every mesh. The note explicitly conditions later sharing on complete required attributes and their representation, including attributes absent from the example.

The source's per-corner callbacks and group checks support the reception hazard. The table is carefully labeled a parameterization-based derivation, **not observed MikkTSpace output**. The glTF applicability condition is retained; it does not require every asset to store tangents. **No correction required.** No exporter, normal-map sampling, rendered seams, or arbitrary quantized deduplication was validated.

## Overall outcome and limits

The examples survive the attempted falsifications because their assumptions are explicit and the conclusions remain narrower than actual experiment, hit evaluation, or renderer behavior. No edits to the three source files are requested by this review. The explicit exclusions are necessary to that finding; deleting them would change the reviewed claims.

Work was limited to prose/source reading, hand reasoning, and artifact identity checks. No example code, estimator, engine, networking, tangent generator, exporter, or test suite was executed. No linked runtime archives, raw participant data, or legacy execution records were inspected. The only new file is this review; no remote writes or existing-stage edits were made.
