# Fresh invocation receipts: additive legacy-runner boundary

2026-10-31. This is tooling/evidence hardening, not a new game-engine behavior claim. [Tool and commands](../../../scripts/evidence/fresh/README.md); [historical failure](../../source-notes/runner-invocation-freshness.md).

## What actually ran

| Scope | Recorded activity | Godot behavior scope |
|---|---|---|
| Author campaign | Six actual copied legacy `-O` rejections and one normal focus invocation | Three focus cases; source audits show two additional helper calls (`--version`, `--help`), not syscall-instrumented |
| Independent reviewer | Same six rejections and one fresh normal focus invocation | Three independent focus cases; raw identity/outcome oracle checked |
| Author unit suite | 15 methods, normal Python once | Three synthetic child processes and one additional copied focus `-O`; no Godot |
| Reviewer unit suites | 15 methods each under normal and optimized Python | Six synthetic child processes and two additional copied focus `-O`; no Godot |
| Integration unit suites | 15 methods each under normal and optimized Python from published tool layout | Six synthetic child processes and two additional copied focus `-O`; no Godot |
| Relocated consumer checks | Two archived positive receipts accepted; twelve campaign negatives rejected | No rerun of engine or runner |

Unit method counts include pure consumer checks and must not be counted as engine runs. Normal mode is enabled only for focus; other five adapters remain unavailable. Every original file and full file set in the six fixture trees (306 files) remains unchanged; integration preservation evidence is separate from author/reviewer checks.

## Archive and portability

- `author/` retains frozen protocol, original file hashes, campaign summaries, unit output and selected invocation evidence.
- `review/` retains independent review, exact reviewed tool copies, semantic check script/output and bounded synthetic process probes.
- `author/invocations/UUID` and `review/invocations/UUID` retain original UUID names, exact receipts, all receipt-bound artifacts and copied source pins. `public-invocations.json` in each side maps raw historical IDs to public paths.
- Generated HOME/XDG/TMPDIR runtime and font caches are intentionally omitted. Receipt-bound files are not omitted. No third-party asset/cache bulk is republished.
- Historical absolute command/repository paths are unchanged raw metadata, not current checkout locations. In particular historical `repeat.py` / `check_raw.py` expect author/reviewer workspace locations; they are archived executed scripts, not portable CLI promises. Use the production consumer and explicit `FRESH_POSITIVE_INVOCATION` override for a checkout.
- `integration/relocated-consumption.json` contains actual commands, exit codes and output for relocated consumer tests. `integration/tests*.stdout/stderr` retain the two integration suite outputs. A unit-test temporary sentinel directory is deleted by its test context; no claim that every temporary individual rejection was retained.
- `public-selection.json` records the selected public audit files and hashes, excluding itself. General archive registry checks cover fourteen receipts' artifact/source manifests and production tool hashes, plus six positive raw/parsed case associations. These are read-only consistency checks, not execution authenticity.

## Process-cleanup negative evidence

Reviewer ran two separate synthetic leader/child descendant probes, neither involving Godot. First probe: leader exited 0; harness detected unexpected descendants and conservatively rejected with group remaining after bounded termination. The child PID was not captured and later tool executions used different PID namespaces: final child state is **unknown**. No later probe resolves that earlier unknown state and no blind PID kill was attempted.

Second probe captured and inspected its own child in the same command namespace: wrapper still conservatively rejected; subsequent inspection found the child gone. Different observation times explain this narrower result. Neither probe establishes universal descendant reaping; escaped sessions, hostile filesystem races and OS failures are out of scope. Raw probes/results are retained under `review/descendant-probe/` and `review/descendant-state/`.

## Trust and limitations

Expected UUID, source/output hashes, registered adapter, terminal status and child exit jointly prevent the checked stale-summary misattribution. Unsigned receipts can still be forged by an actor able to rewrite trusted inputs and matching evidence. Atomic rename is not fsync/durable commit. Installed Godot binary bytes were measured, not authenticated to official release source; [shared provenance limitation](../../source-notes/godot-runtime-provenance.md) remains. No legacy source or historical missing binary hash was silently repaired.

## Version lifecycle

Current archive declarations intentionally compare receipt tool hashes to the production reviewed version. A later harness/registry update is not compatible merely because its CLI looks similar: old receipts fail the new consumer's trust check. Preserve the existing exact tool/registry pair (`review/tool/`), existing receipts and source pins. A future explicit versioned migration may bind historical archive declarations to that preserved version and use a separately reviewed new pair for new invocations; do not rewrite old receipt hashes to make drift disappear.

A new consumer rejecting an old tool version does not retroactively falsify the historical run. Historical consumption must explicitly select the preserved **reviewed** pair matching that receipt; never automatically execute arbitrary code selected by an untrusted receipt. Migration changes registry bindings and consumer selection, not historical receipts or tool bytes.
