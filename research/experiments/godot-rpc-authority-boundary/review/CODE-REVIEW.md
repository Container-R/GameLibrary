# Initial pre-native RPC code review — corrections pending

2026-11-01 00:20 UTC. Exact initial nine sources copied to initial-code/, pinned by INITIAL-SHA256.json. Reviewed full endpoint/main, runner, oracle, consumer and tests. No engine/version process, socket or bind was invoked. Six author pure methods independently pass normal and -O. Additional probe_finite.py control plus ten sender/capture/context/ownership/state/terminal/type mutations reject as intended in both modes.

The scene has passive finite receipt records, captured actual sender, deferred policy application, stop-and-wait requests and explicit parent STOP teardown guard. Literal per-request arithmetic and authority/sender distinctions agree with the protocol. Connection prerequisites are flags rather than assumed callback order. Full expected trace checks bind both sides' peer identity and command/outcome data. No generic security/prediction conclusion follows.

Corrections identified jointly before native authorization:

1. Runner cleanup finish() overwrites a previously observed version returned_utc; preserve first return observation (author self-review finding).
2. finish() marks RETURNED even when bounded cleanup leaves returncode None; record unresolved state, not completed/reaped (main and independent review).
3. Before parent STOP, validate complete raw EVENT trace against each terminal payload, not only the final payload's literal geometry. Current final-only check delays that association until after child exit (main finding).
4. Consumer allows a metadata interval where server returned before client launch. Independent probe_chronology.py reproduces this false acceptance with synthetic receipt timestamps. Require concurrent server/client interval consistency; this is metadata validation, not authenticated execution or distributed-clock proof.

Initial snapshots and raw pure probe outputs remain preserved. No initial checker failure is an engine/network failure. Await a single corrected frozen manifest and pure recheck; no native launch is approved by this document.
