# TASK134 independent source review

2026-11-01. Gate verdict: **ACCEPT for a bounded source-only draft; final-note review pending.**

## Inputs and actual reading

- Gate `research-drafts/valve-dialogue-source-gate/gate.md`: SHA-256 `4ada94a5579efa1d62e899f798a1265bcea472df126664e11501f193eda02e87`.
- Official source PDF, locally inspected: SHA-256 `b78f5d89f5b47eee49ae01f3f5e4a269eff9670746d40001b437e5c2547ac436`.
- Extracted text: SHA-256 `ae224196f749bfaa89c0f51af92e883a6cc2772c5343c39a98a4894873352a6a`.
- Independently read physical pages 48–59 and 62–69, counting from 1 using formfeeds; visually inspected rendered physical pages 62 and 64 (printed 63 and 65). No full-deck or video review claimed.
- Independently opened [Valve's official publications listing](https://www.valvesoftware.com/en/publications): March 2012, Elan Ruskin, *Rule Databases for Contextual Dialog and Game Logic*, GDC. Its linked [official PDF](https://cdn.fastly.steamstatic.com/apps/valve/2012/GDC2012_Ruskin_Elan_DynamicDialog.pdf) is the attributed source. Conference date range visible in slide headers does not establish a particular talk day or revision date.

## Fact versus inference

**Direct source facts:** physical 62 requires every criterion to pass and rejects a missing fact; its visible slide explicitly identifies matched-criterion count as the scoring method used. Physical 64 scores only rules that passed. Physical 57 includes character history in the query. Physical 67–68 illustrates a not-previously-said condition and fact writeback; 65 separately describes variation inside a response.

**Valid original inference:** with only eligible A and B, each initially having three true criteria, adding one true history guard to A changes the count comparison from 3/3 to 4/3. This is a change in competition as well as eligibility. After that guard becomes false, A is excluded before scoring. If its fact is absent, A is likewise excluded, but absence and false are distinct inputs. Neither state can be inferred merely from a newly authored rule or an uninitialized store.

This is not a demonstrated Valve content bug, an actual tie-break trace, evidence about present-day Source, or proof that criterion count is the best semantic priority. The slide's mention of random selection among suitable equal-score rules must not be inflated into a complete deterministic implementation contract.

## Adversarial acceptance checks

1. The counterexample must explicitly hold all other criteria true and hold the competing-rule set fixed. Otherwise a 4/3 arithmetic comparison alone cannot establish the selected response.
2. Eligibility must precede ranking. A rejected four-criterion rule does not beat a valid three-criterion rule, nor should the note give it a partial-match score.
3. The initial history fact must be present with an appropriate value. Missing history is not automatically a valid “never said” guard in the described system.
4. A written “said” fact must not become proof of completed audible playback or a transaction guarantee. The source example is not a save-system, interruption, concurrency or output-device protocol.
5. The production choice to use criterion counting is source-backed; the particular two-rule editing scenario and its acceptance recommendation are original deductions. Keep those evidence labels separate.

## Distinctness from existing coverage

Independently read the narrative role's semantic handoff/priority example and the two ink source notes; compared their bytes to the gate hashes:

- Narrative role: `a90c5a22b4ad41dfd46e3f21b196292b705ddc0b2b645ccc14307e23d9c31e67`.
- ink content compatibility: `a662d26f2deb2c2c58c8a3f5cdb6ad655a5919dac92c1780bad0a2b8f7a20465`.
- ink host boundary: `c65e0cbddc7e20e4c6fbfdedcf2bdd36feb7b101664063d600fc713d4eadd6db`.

The new mechanism is not simply “remember dialogue history” or “specify priority”: a specific anti-repeat content edit alters a published selection function before it excludes anything. Existing ink material concerns speculative external effects and content/checkpoint restoration, not this count-based ranking dependency. Those notes cannot certify the Valve model, but neither do they duplicate this narrow editing decision.

No engine or model was executed. No linked execution archive was opened. The PDF, extracted deck text and rendered slides are review inputs only, not proposed public repository payloads. No remote or staging changes were made. Final note and publication/index edits are not yet approved by this review.

## Final draft review and exact binding

Independently read all three final candidate files and recomputed their hashes:

| Candidate | SHA-256 |
|---|---|
| `article.md` | `cc29892f51c0047ccdbddb1d9437910d87b3545178b58b446f64ab62b38deba9` |
| `source-note.md` | `40dafc5eb052a0f004f4438a59cc2553ad19f8e0917d34c09c2b79f9cefd94c3` |
| `AUTHOR-NOTES.md` | `6d381a85ddf0d3081dec515eae4b33a2c7b34630796e5f692b4e6db2b0ad7cb5` |

**ACCEPT at these exact hashes for bounded source-only publication. No blocking technical correction.** The final article satisfies the gate's substantive conditions:

- Concrete A/B criteria define an actual hand-checkable comparison rather than unspecified counts. The four non-history query facts remain fixed; only two candidates exist.
- The history key is explicitly supplied as Boolean. True/false guard evaluation and absent-key rejection are separately explained. The absent-key case is not silently initialized.
- The three rows correctly separate candidate eligibility from ranking: tied 3/3, eligible 4/3, then A excluded. No specific tie winner is manufactured.
- The selected next-query history value is an assumption, not a claim about when a response writes state or becomes audible. The text expressly excludes player-heard, transaction and interruption guarantees.
- The reference mechanism is attributed to the 2012 presentation, and the anti-repeat-edit consequence is labeled original inference. No source-code execution, present-day Source contract or actual Valve defect is asserted.
- The recommendation identifies an actionable first-selection competition review, beyond merely testing repeat suppression. Response variation remains a different authoring decision.

The source note maintains physical versus printed page numbering and separates the writer's text reading from others' visual inspection. The reviewer directly verified only the reading and visual scope recorded above; claims about other reviewers' actions remain their attestations, not new independent evidence. No full-deck redistribution or copied dialogue appears in these three candidates.

This acceptance does not approve uninspected navigation edits, metadata registry uniqueness, remote publication or later file changes. It is a source/logic review, not an engine test, behavioral compatibility certification or copyright clearance for additional third-party assets.
