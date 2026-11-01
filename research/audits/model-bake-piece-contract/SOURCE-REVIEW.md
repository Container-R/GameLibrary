# Independent source and final-note review

2026-11-01. **ACCEPT** the bounded source-only note; no material technical correction required.

Reviewed artifacts:

- `note.md`: SHA-256 `644fecd36020d02b82600ecc4248833bd6e1a2ed3148c815fdac2b1153d03dc6`.
- `AUTHOR-NOTES.md`: SHA-256 `d00aaa7d76475865ebc9f285fd8260ac2e631596df57ed16f2d15811c40a2a7e`.

## Original source independently read

[SideFX Bake Geometry Textures 2.0](https://www.sidefx.com/docs/houdini/nodes/cop/bakegeometrytextures-2.0), accessed 2026-11-01. Read page header, Mesh types / Cage mesh, Baking best practices, Match Pieces by Name, and relevant Ray Setup / Cage Attributes context. Decisive rendered-text locations: 76–81, 92–93, 117–123, 243–269; section names are the stable navigation labels. The current page distinguishes Houdini 22.0, node 2.0, and Since 21.0. No publication date or immutable source revision was established. No images inspected.

## Technical findings

- The original body/latch merge changes the partition used by the documented matching exclusion. The note correctly stops at eligibility: it does not infer an actual intersection, accepted hit, changed texel, or numerical AO result.
- Cross-input name correspondence is weaker than preservation of the original partition. The one-to-one rename comparison correctly requires unchanged effective Include/Exclude selection and does not promise byte-identical output.
- Include/Exclude are not promoted into an arbitrary pairwise permission mechanism. Separate cage validity is retained; matching labels do not prove topology or vertex correspondence.
- The proposed receiving procedure distinguishes independent component use from a deliberately assembled-state asset. It neither mandates isolation for every asset nor treats an unchanged configuration string as unchanged selection.
- The original example, prospective checks, and unverified outcomes are clearly separated from official documentation. Related tangent/simplification work supplies no transferred runtime evidence. The cited version labels are not an installed-version claim.

This review read the final note in full and checked its source mechanism and reasoning. It did not create geometry, run a baker, measure performance, inspect images, or establish visual correctness. No draft content was changed.

Locator verification: the referenced source-gate `main-read.md` exists. An initial review message incorrectly inferred a filename mismatch from the separately supplied MAIN-SOURCE-READ.md; that concern is withdrawn after checking the exact referenced directory. No author correction is needed.

## Final metadata closure

Read the revised metadata and author record, and confirmed the neutral wording “在实际验证阶段” without converting future checks into results. **ACCEPT** final `note.md` SHA-256 `caf10624424444810788fe4b8a8cf84658967a3c8612d522eda2095615fe669d` and `AUTHOR-NOTES.md` SHA-256 `b28bd3c453b450ddcd07935a44a7e8d49eb8c482390443079feb379fcf6fa9a3`. The source-backed classification and separate document/node/Since identities are accurate. No technical claim was broadened. Earlier hashes above identify the prior reviewed draft, not the publication selection.

## Publication-record closure

Inspected the final author-record-only revision: the reading locator now names the companion MAIN-SOURCE-READ.md, and the unavailable preparation-gate pointer is replaced by the two previously declared comparison-input hashes. These are archival navigation/identity changes, not new source or runtime claims. **ACCEPT** final AUTHOR-NOTES.md SHA-256 `cd23f26871d9d16d442e6553c4c931db6905fce8d8c53ecb3794b62dca3fff72`; note.md remains unchanged at `caf10624424444810788fe4b8a8cf84658967a3c8612d522eda2095615fe669d`. No additional substantive correction requested.
