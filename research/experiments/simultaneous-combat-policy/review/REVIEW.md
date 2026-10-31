# Independent simultaneous combat policy review

2026-10-31. Accepted finite supplemental model, no material issue. Read pre-frozen contract509e8144 before execution. Reviewer literal oracle never imports model helpers. Main/original files unchanged.

Actual independent copied commands all exit0:

- `python fixture/run.py > normal.json 2> normal-stderr.txt`
- `python -O fixture/run.py > optimized.json 2> optimized-stderr.txt`
- `python fixture/test_model.py > test-stdout.txt 2> test-stderr.txt`
- `python check.py > check-output.json`

Paths relative to this directory. Twelve unique inputs checked:3initialHP ×2actor insertion ×2command ordering. All simultaneous results match independent literal events/HP; four both-alive inputs kill both under selected policy. Ordered immediate variants disagree on those four; canonical sorting produces stable A winner, showing deterministic order does not imply simultaneous rule compliance. Eight initially-dead controls agree; four next-tick checks are exercised by source runner, not extra unique initialcases. Five unittest methods pass. Normal and -O parsed traces match except optimization flag; no assert-only runner acceptance. Canonical event list comparison is not evidence of actual publication ordering.

One isolated synthetic mutant replaces simultaneous function with canonical-immediate result. Same frozen contract runner rejects with simultaneous oracle mismatch,exit1; rawstderr/command/receipt under mutant-sorted-immediate/. This checks a concrete policy substitution,not genericmutationcoverage. Runner writes JSON only tostdout,not an archived summary; no claim it invalidates caller-owned old output files.

Implementation review: tick-start snapshot eligibility reads both attacker and target alive; accumulated damage commits once within this invocation; death events reflect alive→dead transition. Caller HP copied; no stateful idempotency/duplicate-delivery guarantee. Validation deliberately limits2actors/HP0or1/onecommandperactor; arbitrary multi-hit,heal,resurrection,invulnerability,network,physics or engine scheduling outside scope. Sequential policy is valid for games that intentionally choose it; this is not a universal fairness prescription. Existing SOL-PROG-001 supplement is appropriate; no new article needed solely for model count.
