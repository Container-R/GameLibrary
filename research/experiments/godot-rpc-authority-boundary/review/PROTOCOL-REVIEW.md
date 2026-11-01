# Independent RPC authority protocol review

2026-11-01 00:12 UTC. Accepted protocol SHA256 `86323211989a29ef3a8cdb008fe9789100e2235c5929af979d2743c940c80e6e` for implementation review only. Read the complete candidate against SOURCE-REVIEW and the independently read official source paths. Current source gate `9730e2a9…` resolves the former handler/deferred stage ambiguity. No fixture code, native/version process, socket or port probe was executed.

## Supported finite contract

- One version process plus one concurrent server/client pair; both explicit loopback addresses and distinct nonzero fixed ports. Client's nonzero local_port takes the inspected bound-host branch. No availability assumption, scan, interface fallback or retry. Port readback remains API-level evidence, not independent OS interface authentication.
- Actual server readiness precedes client launch. Endpoint path and authority are identical and read back. Welcome binds the client's actual peer ID to server-owned A; B belongs to server1, not an invented second client/account.
- Exactly three stop-and-wait command samples. Handler captures sender and finite scalar request, schedules one deferred callback, then logs end without applying either accumulator. Deferred validation checks saved C versus current getter0 and applies the literal before/after table. Naive A10001/B1 versus guarded A1/B0 is correct for the stated sequence and range; this remains application arithmetic, not prediction or movement.
- Captured sender is not recovered from client data; current contextual getter0 is not used as actor identity. Outside-context zero is source-supported provided no nested polling/RPC execution is introduced into that callback. Deferred does not mean a full frame.
- Three outcomes are actual client receipts. Client sends finish only after outcome3; server finish confirmation is separately required. Parent waits for both final payloads before a fresh UUID-scoped STOP barrier, avoiding immediate quit after queued final send. STOP carries no game/identity result and does not substitute for remote delivery.
- Counts are coherent: three submit handlers and five control handlers (one welcome, three outcomes, one finish), eight remote deliveries in one sequence. RPC send success is not remote execution proof. Identity/index/stage association, not wall-clock comparison alone, establishes causality.

## Implementation review checkpoints

The exact implementation must preserve each request's immutable copied fields, enforce pending/index state on both sides, and fail before further submissions when a stage is invalid. A welcome arriving near connected notification should be handled by explicit readiness state, not a guessed event-order or arbitrary delay. The parent collector must handle fragmented pipe lines while preserving raw bytes, validate READY before launching client, and reject invalid/duplicate terminal events before creating STOP.

Bounded cleanup wording must remain operational rather than absolute: on failure, attempt owned-group termination/wait, record any inability to confirm exit, and never publish PASS with an unresolved child. The instruction not to leave a listener is a required cleanup objective, not proof that every OS failure can be contained. Successful completion requires both real process exits. Watchdogs, per-attempt deadline and output bounds must be explicit in code and cannot be extended silently after a failure.

JSON/type guards, exact source and binary before/after pins, argv/minimal per-process environment and raw/parsed associations need code-level adversarial checks before launch. Endpoint shutdown guards may close the already-declared measurement window but must not mask stderr or unexpected active-stage events. Historical failure records remain distinct.

No material protocol correction requested. Acceptance does not authorize implementation execution: exact code review and coordinator native authorization remain required. Existing prediction/model/Unity evidence is not upgraded by this planned ingress sequence; no security, authentication, transport resilience, physics or general anti-cheat conclusion follows.
