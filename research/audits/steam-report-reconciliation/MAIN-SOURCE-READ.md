# Main source inspection: Steam report reconciliation

2026-11-01. Source-only review; no account, report export, user identifiers or execution evidence accessed.

## Read scope

- Valve, [UTM Analytics](https://partner.steamgames.com/doc/marketing/utm_analytics): public English body, Privacy, visit categories, conversion timeframe, testing/finalization, Known Challenges, Discrepancies, FAQ. Main inspection covered the body and FAQ; examples/screenshots and video were not inspected. Rolling documentation, no fixed revision established. The page's 2025-04-22 sale-page date does not date the whole document.
- Valve, [Store and Platform Traffic Reporting](https://partner.steamgames.com/doc/marketing/traffic_reporting): introduction, app/partner report scope, Impressions, Visits, Click-Thru Rate, collection dates and FAQ. Main read the complete textual body. The screenshot was not inspected. The obsolete `/doc/c/marketing/traffic_reporting` route redirected to the documentation home; the ordinary canonical documentation route above returned the relevant body. No account login or access-control workaround was attempted.

## Claim boundary

The direct support is the UTM page's Discrepancies section: the two reports count differently, including cookie preferences, and UTM may exceed the other report. The traffic page defines visits as page loads rather than unique people, permits per-app or partner summaries, and notes applicable cookie opt-outs. These facts justify rejecting an unproved common-population/subset premise. They do not identify the intersection, exact deduplication rules, missing users, or true untagged traffic.

The proposed worked sets are deliberately invented. Their purpose is to show that a difference of cardinalities is not generally a set difference and that a positive result alone does not prove containment. They are not a reconstruction of Steam ingestion, privacy filtering, or actual report data. A separate classification error remains even if an untagged count is known: absence of a tag is not a paid/organic label.

## Scope decision

Narrowed the initial broader attribution gate to report reconciliation. The library already covers causal interpretation and event denominators; repeating an attribution-versus-incrementality slogan would add little. New work should offer a finite receiving decision and preserve definitions, report scope, period, extraction time and unknown overlap rather than a guessed correction factor. No financial recommendation or ad-spend operation is proposed.

Main source inspection is not acceptance of an unseen final draft. Independent exact-artifact review remains required. No prior runtime archive is used as evidence.

## Algebra checked before drafting

Under an intentionally stronger hypothetical assumption that both observations can be represented by sets over the same event universe, let B be observations in the broad report and U be observations in the tagged report. Partitioning each set gives `|B|-|U| = |B\U|-|U\B|`. With intersection 60 and U size 100, B size 80 yields -20 while B-only is20; B size120 yields20 while B-only is60. Thus sign alone is not the missing containment premise. Moreover B-only is not necessarily genuinely untagged: an event might have a tag yet be outside U's observation rule. These hand calculations are not software tests and do not establish actual Steam event identities or counting implementation.
