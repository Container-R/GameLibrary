# Independent fictional attempt metric review

2026-10-31 18:52 UTC. Accepted within finite original contract, no material issue. Read contract before own enumerated-membership oracle; no author report imports in check_raw.py. Frozen report `3e58e54713d0973d867f65a22fad8a092fe8ffcb61c707c65a14fe2769bad6ee`, runner `b7b43d29154f8580b439b44a9eeb90c5cd3e84bb709a75ffd7c20a01191c21c5`, contract `6cbafb1115b0173e3fd01f3ca0e621d3cacf73eb9283f2d2df7a2866650cc239`.

## Actual commands
```
python3 research-drafts/deep-qa/telemetry-attempt-contract/fixture/run.py > research-drafts/deep-qa/telemetry-attempt-contract/run-output.txt 2> research-drafts/deep-qa/telemetry-attempt-contract/run-stderr.txt
python3 research-drafts/deep-qa/telemetry-attempt-contract/check_raw.py research-drafts/deep-qa/telemetry-attempt-contract/fixture/results > research-drafts/deep-qa/telemetry-attempt-contract/independent-output.json
python3 research-drafts/deep-qa/telemetry-attempt-contract/adversarial.py > research-drafts/deep-qa/telemetry-attempt-contract/adversarial-output.txt 2> research-drafts/deep-qa/telemetry-attempt-contract/adversarial-stderr.txt
```
All exit0/stderr empty. Source hashes and raw single RESULT_JSON match summary. Eighteen input IDs/times match literal contract; independent full report object comparisons establish exact completed/failed/unresolved/cohort actors, orphan/out-of-cohort distinction, assistance and fraction populations at100/200. Twelve original complete-batch comparisons cover six fixed orders each, not streaming or allpermutations.

## Supplemental actual observations

Nine in-process probe groups plus two child runner-failure probes recorded separately in adversarial/observations.json:
- asof36 has completed a1,b1,d1; asof37 late conflicting x-d1 removes d1 from completed and leaves it unresolved. A later knowledge snapshot can reduce a completion count; no monotonic improvement inference.
- Additional same-ID/samepayload delivery with changed arrival increases retry count only.
- SameID changed assistance quarantines whole c-a1 ID; no first/last wins.
- SameID changed event_time120 still quarantines before event-window selection, rather than hiding conflict by filtering first.
- Arrival201 semantic conflict does not leak into asof200 report.
- Distinct extra start/terminal, mismatched actor, and before-start outcome each reject with exact declared errors.
- Isolated -O/priorPASS and report import failure each exit1/no old or new summary. Raw command/stdout/stderr retained. Old asof files remain evidence copies; consumers must use current invocation exit/summary, not treat retained files as new success. No universal atomic receipt/OS failure guarantee.

No future-event completion contaminates a2 fail in original report. Missing assistance is unknown, neither unassisted nor failed. Denominators six attempts/five actors vs finished-only three/four are intentionally different, not inconsistent rates. Whole-ID quarantine and global attempt-ID uniqueness are proposed fictional policy, not vendor behavior.

## Sources independently read

Accessed2026-10-31:
- https://docs.unity.com/en-us/analytics/rest-api/record-event-rest-api : Important fields eventUUID/eventTimestamp and Response codes. Event identity can support retry dedup; receipt acknowledgement differs from processed-event verification. No retention/exactly-once horizon established. Relative update label10months, no invented absolute date.
- https://docs.gameanalytics.com/events-metrics-and-filtering/metrics/ : Progression(levels) explicitly finished attempts denominator for win percentage; Sessions(playtime) distinguishes populations. Fictional started-cohort fractions are not claimed vendor outputs.
- https://docs.gameanalytics.com/event-tracking-and-integrations/sdks-and-collection-api/api/event-types/ : Detecting missing session end on game launch describes missing end/recovery possibility, not reason for any fixture unresolved attempt or attempt-outcome rule.

Only relevant documentation text read; no provider SDK/account/event submission, installation or legal assessment. No actual players, causal improvement or retention analysis. Main/original/remote untouched; copied fixture and reviewer artifacts only.

18:52 UTC supplemental empty cohort probe: `python3 research-drafts/deep-qa/telemetry-attempt-contract/empty_cohort.py research-drafts/deep-qa/telemetry-attempt-contract/fixture/report.py > research-drafts/deep-qa/telemetry-attempt-contract/empty-cohort-output.json` exit0. All three numerator/denominator fields return[0,0], no division performed; rates are undefined, not0%. One additional in-process case in a separate process, not part of original12order comparisons. No general ingestion/schema expansion.
