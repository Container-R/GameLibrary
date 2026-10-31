# Frozen fictional reporting contract — 2026-10-31

Original synthetic events only, not vendor implementation/player observation. Frozen before code. All times integer seconds relative to2026-10-01T00:00:00Z; event-time start cohort [0,100), outcome observation event-time [start,100), arrival as-of inclusive100 then200. Old starts retained for orphan distinction; future-event outcomes excluded even if arrival visible. Clock quality assumed fixture-perfect, not real clients.

Event identity is event_id; payload includes actor_id,attempt_id,kind,event_time,assistance. arrival_time is delivery metadata excluded from payload identity. Same-ID samepayload retries collapse; any differing payload among visible arrivals quarantines the WHOLE ID before event-time selection (no first/last wins). Distinct eventIDs are not automatically retries. Stable attempt identity globally unique within this fictional dataset; actor identity separate. Quarantining an outcome leaves its eligible attempt unresolved plus conflict-affected flag, not failed.

Literal row plan (missing assistance = unknown for completion):

|event_id|attempt|actor|kind|event_time|arrival_time|assistance|
|---|---|---|---|---:|---:|---|
|s-a1|a1|P|start|10|11|—|
|s-a1|a1|P|start|10|12|—|
|c-a1|a1|P|complete|20|21|unassisted|
|c-a1|a1|P|complete|20|22|unassisted|
|s-a2|a2|P|start|30|31|—|
|f-a2|a2|P|fail|40|41|—|
|s-b1|b1|Q|start|12|13|—|
|c-b1|b1|Q|complete|25|26|assisted|
|s-c1|c1|R|start|14|15|—|
|c-c1|c1|R|complete|50|150|unknown|
|s-d1|d1|S|start|16|17|—|
|x-d1|d1|S|complete|35|36|unknown|
|x-d1|d1|S|fail|35|37|—|
|c-z|z|U|complete|45|46|unknown|
|s-e1|e1|T|start|18|19|—|
|s-old|old|W|start|-10|1|—|
|c-old|old|W|complete|60|61|unknown|
|future-a2|a2|P|complete|110|111|unknown|

Expected by hand before implementation:
- asof100 visible16rows, asof200 visible18rows. In event window raw start rows7 both; raw complete rows6 then7 (deliberately naive diagnostic includes retries/conflict/orphan/out-of-cohort). Thus raw6/7 then7/7 not cohort success.
- both: clean eligible starts a1,a2,b1,c1,d1,e1 =6 attempts,5actors P/Q/R/S/T. Retry extra rows2; conflictIDx-d1 with2rows quarantined. Orphan c-z; observed old-cohort completion c-old distinguished, never added to numerator.
- asof100 completed[a1,b1],failed[a2],unresolved[c1,d1,e1]; completion/started=2/6; actorswithcompletion/actorswithstart=2/5. Completed assistance unassisted1,assisted1,unknown0.
- asof200 completed[a1,b1,c1],failed[a2],unresolved[d1,e1];3/6 and3/5; assistance1/1/1. future-a2 remains excluded by event-time cutoff; don't contaminate a2 fail with future complete.
- finished-only fraction2/3 then3/4 is another population, not our start-cohort completion metric. Unresolved are not inferred failures. No rates imply design improvement or player ability.

Finite policy: multiple distinct terminal IDs in observation window, multiple distinct start IDs, actor mismatch or before-start outcomes cause explicit error for this fixture implementation; no universal reconciliation recipe. Late arrivals produce a new as-of report, oldreport remains. Order tests cover complete input list reverse plus deterministic fixed shuffles, not streaming transitions/allpermutations.

Source read2026-10-31: Unity REST Important fields eventUUID/eventTimestamp and response receipt/processing distinction; GameAnalytics Metrics Progression(levels) explicitly defines win percentage over finished attempts, not started cohort; Sessions(playtime) distinguishes session/user populations. Event Types Detecting missing session end on game launch supports delivery gaps being possible, not proving why a given attempt lacks an outcome. These are rolling docs, no exact build/date asserted, no service calls or legal advice. Original source-notes.md retained unchanged.
