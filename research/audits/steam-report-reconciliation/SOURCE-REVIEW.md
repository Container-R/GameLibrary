# Independent Steam report-reconciliation source review

2026-11-01. **Accept the narrowed source-only premise; final draft pending.** This verdict covers reconciling two visit totals, not the broader causal-attribution proposal in the initial gate.

## Exact input and primary reads

Initial gate: `research-drafts/steam-attribution-source-gate/gate.md`, SHA-256 `32dbfba23a123ae96de310dc0abb2691cd553ef95ba460c9d42a38543a59d4d6`.

Independently opened and read the following public English documentation, without an account:

- [Steamworks UTM Analytics](https://partner.steamgames.com/doc/marketing/utm_analytics), specifically Tracked Visits and Discrepancies Between UTM Analytics and Traffic Breakdown. UTM Total concerns visits with a UTM code. The discrepancy section attributes differences to traffic coverage and separate cookie preferences; either report may have the greater number. This does not furnish a cross-report event matching or deduplication algorithm.
- [Store and Platform Traffic Reporting](https://partner.steamgames.com/doc/marketing/traffic_reporting), specifically Understanding the reports / Visits and Notes on Data collection date ranges. Visits are described as unique page loads, not unique people. The page expressly notes repeat customer visits and applicable-cookie opt-out exclusion for impression/visit reports since March 23, 2021.

Both pages are rolling documentation, not fixed software implementations. The reading date is not their revision date. No example image, video, partner report, download or account data was inspected.

## Independent adversarial assessment

The narrow thesis is supported: a numerical difference is not automatically a population remainder. Naming two fields “Total Visits” does not establish a shared observation universe, unit identity or subset relation. A positive difference is not stronger evidence of containment than a negative one; it merely avoids an immediately conspicuous negative count.

A finite invented set example can demonstrate this logical insufficiency, provided its sets are explicitly hypothetical observations, not Steam's actual internal records or a claimed reconstruction of missing traffic. Even common units and matching report filters would not alone establish the subset relation. Conversely, failure to establish it does not mean reconciliation is impossible in every future controlled dataset; the claim should remain about what these two totals and published definitions justify.

A non-UTM category, even if validly established somewhere, does not by definition mean unpaid, organic or unaffected by marketing. Those are additional classifications, not consequences of absent URL parameters. The article should not infer any actual campaign composition from this distinction.

Required final-draft checks:

1. Keep the original field names and visibility conditions separate; do not rename unique page loads as unique visitors.
2. Do not interpret the difference as a count of cookie opt-outs, bots, lost conversions or hidden people.
3. Do not prescribe fabricated deduplication, attribution-touch or correction-factor algorithms.
4. Label invented sets and arithmetic as a logical example, not downloaded data, measured mismatch or a Steam implementation model.
5. Offer a concrete acceptance action: retain two independently defined metrics and decline an unsupported derived “organic” column unless its measurement contract is separately established.

No runtime, browser-path experiment or analytics query was executed. This is an independent documentation and inference review, not the prior author's verification. Final-note acceptance and hash binding remain pending; no remote or staging change was made.

## Final candidate binding and verdict

Independently read both complete candidate files and recomputed their SHA-256 values:

- `research-drafts/steam-report-reconciliation/note.md`: `5f982759040d785cb467a7d9dabac34797213642f76c341fdfd8337081ae10d2`.
- `research-drafts/steam-report-reconciliation/AUTHOR-NOTES.md`: `f2ae60ee1d515461fa283d8f7fbed65dcbba29e8f2a6e189deaa4c572ff357ac`.

**ACCEPT at these exact hashes for source-only publication; no blocking source or mathematical correction.** The primary-source read also covered Privacy and Testing a link on the UTM page, and Accessing Reports on Traffic Reporting, which the final note cites. Threshold suppression, hourly visit refresh and separate conversion finalization are accurately bounded; the latter is not imposed on visits.

The first invented pair has intersection {b}, leaving one T-only and two U-only records; the difference is -1. The second has intersection {c}, leaving two T-only and one U-only records; the difference is +1. Both rows and the finite-set identity are correct. These are independent hand checks, not executed simulations or actual report observations.

The strongest distinction is retained: even an established T-only observation need not be an actually untagged visit; and even an established untagged visit need not be organic. The counterexample of an untagged paid link proves a classification distinction without asserting how Steam labels a specific row. The stronger common-record-unit premise is plainly hypothetical, not an inferred platform implementation.

The concrete acceptance table preserves original report identity, scope, measurement unit, filters, timing and unknown visibility. Its business recommendation is to withhold unsupported derived labels while keeping the original metrics. It neither requires personal identification nor proposes reconstructing hidden records. Broader attribution-versus-causality material from the original gate has appropriately been left out.

Optional presentation polish only: the table uses doubled backslashes for set difference, while other paragraphs use single backslashes or LaTeX. Consistent `T minus U` wording or verified renderer-supported set notation would be clearer. This does not change the correct arithmetic or acceptance verdict.

No registry uniqueness, link target deployment, remote publication or subsequent edit is certified here. No account access, engine/runtime work, experiment or private data was used. AUTHOR-NOTES statements about the author's broader reading are attestations, not additional independent review evidence.

## Formatting revision: superseding final binding

Re-read the complete revised note and AUTHOR-NOTES after the notation correction, and recomputed both hashes. The table now uses single-backslash code notation; equations use dollar-delimited math. Title/date spacing was improved. No substantive scope or inference changed.

**ACCEPT superseding final bytes:**

- `note.md`: `d04fb350402ea71ce6b5e2bcd96f34df8e0c57a922f8827f054fa38703ff0da2`.
- `AUTHOR-NOTES.md`: `e3adb6a01e8bab6f2b024fa4ce5805b9db1dc18e59b3ecaef59e3900b6e1bd9f`.

The optional notation finding is resolved at source-text level. Actual deployed-page rendering has not been inspected by this reviewer. All prior finite source/logic limitations remain.
