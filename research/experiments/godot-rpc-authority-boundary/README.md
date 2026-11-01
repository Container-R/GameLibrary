# Godot loopback RPC ingress and queued command authority

A finite original two-process observation, not prediction or network security certification. The endpoint permits three `any_peer` command calls; server-owned queued records preserve the actual sender for later application authorization. Every accepted exchange uses one server, one client and one unique three-command configuration.

## Observed result and exact counts

| Record | Version | Server | Client | Result |
|---|---:|---:|---:|---|
| Initial author `cee0c49d-8f19-4f76-aeee-76d302a255ca` | 1 | 1 | 0 | FAIL: four parse errors before READY; no accepted RPC behavior |
| Corrected author `27e538cb-7c1e-4feb-8e60-ddfb3960b6ad` | 1 | 1 | 1 | Accepted finite exchange |
| Independent repeat `58830003-76ab-4bab-a089-36d642139fb4` | 1 | 1 | 1 | Accepted same-source, same-binary exchange |
| Total actual processes | **3** | **3** | **2** | 8 processes; 2 accepted exchanges, not 8 scenarios |

The initial failure assigned the void result of Callable `method.rpc_id(...)` to a variable. It remains FAIL; the owned server was terminated with observed exit -9 and no client launched. Only four send expressions changed to the Error-returning Node `self.rpc_id(peer, "method", ...)`. Protocol, oracle, ports and timing were not relaxed. `historical-callable-return-failure/` preserves its exact nine-source snapshot and complete raw receipt; `CALLABLE-CORRECTION.md` explains the original API distinction.

Both accepted runs have empty stderr and exit 0 for every process. Author peer C is `817464963`; reviewer C is `1799021229`. Each run has 23 server events and 13 client events. For every request, the RPC context sender is C, the copied sender remains C, and the fresh deferred getter is 0.

| Request | Naive poststate A/B | Guarded decision | Guarded poststate A/B |
|---|---:|---|---:|
| A, +1 | 1 / 0 | accepted | 1 / 0 |
| B, +1 | 1 / 1 | ownership rejection | 1 / 0 |
| A, 10000 | 10001 / 1 | input-bound rejection | 1 / 0 |

The three inputs are ordinary integers. The fixture uses a fictional server-owned map A→C / B→1; it does not authenticate C as an account. It explicitly reads back `allow_object_decoding=false`, empty auth callback, node authority 1, matching endpoint path and actual nonzero local ports.

Per accepted exchange, three submit command handlers and five control handlers (welcome, three outcomes, finish) run remotely. Across two accepted exchanges this is six command and ten control deliveries, **not packet counts or six distinct scenarios**. Client sends each request after receiving the preceding outcome. Parent validates both complete raw terminal traces and server finish confirmation before creating STOP. Deferred processing is not assumed to wait an entire frame. Requested loopback plus actual port readback and source comparison is not an independent OS interface audit.

## Files and review

- `protocol.md` is frozen before implementation; its pending-at-freeze label is historical. Acceptance and execution authorization are separate records.
- `main.gd` / `endpoint.gd`: original Node-only scene and RPC callbacks. No physics or prediction code.
- `run.py`: one finite sequence, fresh UUID, readiness-gated client launch, strict streams, own-group bounded cleanup attempts, terminal barrier, manifests and receipts.
- `oracle.py` / `consumer.py`: explicit typed literal expectations, duplicate/nonfinite rejection and portable archive consistency checks. They do not invoke the engine or authenticate execution.
- `test_pure.py`: seven stdlib-only synthetic methods, run normal/-O. The synthetic receipt is deliberately manufactured test input, not an execution record.
- `historical-pre-native-review/`: initial code and successful pure checks before four receipt/barrier hardening changes. Independent review retained the chronology false-acceptance reproducer; current consumer rejects it.
- [`review/NATIVE-REVIEW.md`](review/NATIVE-REVIEW.md): independent actual repetition, literal raw checker and scoped evidence. `review/optimized-startup/` is a separate seeded synthetic PASS `-O` startup rejection on the exact pre-Callable-correction source snapshot: zero native processes. The runner bytes were unchanged by the four-call correction; this is not a corrected-endpoint runtime test.

The reviewer ran seven pure methods and ten independent finite payload mutations normal/-O, plus the chronology counterexample. These are not transport tests. Parent static consumer/checker combinations on both accepted archives normal/-O add no native calls. Timeout handling is inspected, not deliberately injected; the actual initial parse failure did exercise termination of the owned server. Failure cleanup attempts are bounded and can record UNRESOLVED, incomplete drain or cleanup errors; no universal descendant containment is claimed.

## Inspect or reproduce without overwriting the archive

For static checking, use the supplied current source directory and an accepted evidence UUID directory:

```sh
python consumer.py /path/to/experiment /path/to/experiment/evidence/27e538cb-7c1e-4feb-8e60-ddfb3960b6ad
python -O consumer.py /path/to/experiment /path/to/experiment/evidence/27e538cb-7c1e-4feb-8e60-ddfb3960b6ad
```

Reviewer evidence uses its exact `review/native-repeat/` source copy and nested `evidence/58830003-76ab-4bab-a089-36d642139fb4/`. Static validation needs no currently installed Godot or historical absolute directories. It checks recorded paths against receipt structure, local provided source hashes and raw files. Do not run the PASS-only consumer on the failed parse attempt and interpret rejection as missing evidence; that record is intentionally FAIL and retains its own snapshot.

Native reproduction is optional and separate from archive inspection. It opens two local UDP ports. First obtain permission for this exact local operation and make a **fresh external disposable directory**, copying only the nine files listed in `SOURCE-SHA256.json`; never run in this archived directory or its historical snapshots. Run `python test_pure.py` there before any authorized `python run.py`. The runner requires the exact recorded executable bytes and protocol/helper pins; no automatic install, binary replacement, alternate ports or retries. Fixed ports 32187/32188 may be unavailable: bind failure must end the attempt. The version query is bounded at 20 seconds; server/client share a 20-second deadline with 15-second internal watchdogs. Cleanup attempts have separate bounded waits. These bounds are not latency performance evidence.

The runner deletes its own stale summary before optimized rejection/local imports, records before/after source and binary hashes, and preserves failed receipts. The helper supplies only five selected writable locations with minimal base `PATH`, `LANG`, `LC_ALL`; it is not a sandbox or a full environment/loader security proof. Original recorded environment paths are descriptive metadata, not files required by the portable checker.

## Limits and provenance

Installed binary SHA256 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`, self-report `4.6.3.stable.official.7d41c59c4`. The self-reported “official” build string is not independently authenticated. Compared upstream commit `35e80b3a8822a9df9be390814b62f44c0a9c69e8` is not established as the build source of those bytes.

No WAN impairment, reconnect, ownership transfer, replay/dedup, authentication, encryption, rate limit, general anti-cheat, simulation tick, physics, movement, prediction, rollback, cross-platform or user-study result is established. Existing integer prediction tests and Unity source-only analysis keep their previous scope. See [source note](../../source-notes/godot-rpc-authority-boundary.md) and [article](../../../solutions/programming/client-prediction-authority-boundary.md).
