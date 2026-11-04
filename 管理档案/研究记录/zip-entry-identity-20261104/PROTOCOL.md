# ZIP member identity: pre-execution specification

Written 2026-11-04 UTC, before constructing any ZIP or executing the probe or runner. Execution approval is determined by a matching reviewed FREEZE.json, not by this document's title. A separate reviewer must inspect this protocol, probe.py and run_probe.py before approval and creation of FREEZE.json; execution is prohibited until then. Any subsequent edit invalidates that freeze.

## Question and allowed scope

Does enumerating archive entries but selecting bytes by filename pair one entry’s metadata with another’s content, while reading the same unmodified ZipInfo retains entry selection? Separately, does an explicit uniqueness rule reject all exact-name duplicates, including identical bytes?

Exactly four fixtures, two small entries each, BytesIO only and ZIP_STORED. Original UTF-8 JSON bytes A = `{"damage":1}\n` (13 bytes) and B = `{"damage":2}\n` (13 bytes), where `\n` means one LF byte. Name N = weapons/rifle.json; unique control also uses M = weapons/pistol.json. No extraction, disk ZIP, network, compression benchmarking, malformed archive, normalization, engine execution or security conclusions. Metadata timestamp is fixed at 2020-01-01 for fixture consistency, not evidence of archive reproducibility.

## Source and environment distinction

Prior source gate used official CPython v3.12.0, not the installed binary. A read-only inspection of the available interpreter self-reported Python 3.12.14. Inspection of its actual imported zipfile methods confirms the relevant list/map, getinfo, read-to-open, direct-ZipInfo and header-offset mechanisms; other implementation details differ. This establishes only the inspected mechanism in this available installation, not binary provenance or equivalence to all 3.12 interpreters. No absolute source paths, build fingerprints, process IDs or private environment data belong in the public derivative. The runner checks the self-reported version triplet, not a cryptographic interpreter identity.

## Frozen predicted table

Each row below describes the two enumerated entries, in order. Payloads and sizes must match exactly, not merely compare equal to one another.

| Case | Entry names | Metadata sizes | read(name) | read(same info) | Name-selected ordinal | Write warnings | Project decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unique | N, M | 13, 13 | A, B | A, B | 0, 1 | none | accept |
| duplicate_ab | N, N | 13, 13 | B, B | A, B | 1, 1 | one duplicate warning | reject |
| duplicate_ba | N, N | 13, 13 | A, A | B, A | 1, 1 | one duplicate warning | reject |
| duplicate_aa | N, N | 13, 13 | A, A | A, A | 1, 1 | one duplicate warning | reject |

Each fixture must return exactly two distinct ZipInfo objects. Ordinals are report labels, not Python memory addresses. getinfo’s returned object is identified using `is` against the existing list. Entries remain unmodified. The rejection is an original project policy based on duplicate exact decoded names, not a Python acceptance rule. Identical-byte duplicates isolate uniqueness from content mismatch. A and B deliberately have equal lengths: matching size cannot establish matching content. Reversal isolates central-directory selection from semantic labels such as old/new.

Warnings are captured with a local `always` filter during construction, separately from read warnings. Each duplicate fixture expects one UserWarning with message `Duplicate name: 'weapons/rifle.json'`; unique expects none, and all reads expect none. This deliberately avoids a warnings-as-errors environment and does not claim all callers permit duplicate writes.

## Execution procedure after review and freeze only

The approving coordinator creates FREEZE.json with decision approved and SHA-256 values for exactly PROTOCOL.md, probe.py, run_probe.py. At the time this specification was written, that file did not exist. Missing/mismatched freeze prevents the subprocess and preserves prior results. Run the runner once with argument run1, then independently launch the same runner with run2. These are two fresh-process executions by the same operator, NOT independent native replication. Do not tune expectations after seeing results; revisions require a new reviewed freeze and preserve the original failure in a separately labeled record.

Each invocation launches the available executable in isolated mode with bytecode disabled, a fresh temporary current directory and HOME/XDG locations, no stdin, and a ten-second subprocess timeout. No inherited environment variables are passed. Temporary captures are checked against 64 KiB each before parsing; this is a post-capture limit, not an OS output quota. The probe is bounded by eight entries with tiny fixed payloads. Temporary directories and captures are removed at exit. The only intended persistent runtime artifacts are run1.json and run2.json beside these drafts.

After the freeze checks, a rerun discards only its same-label prior result and temporary output. JSON result replacement is atomic. Probe exceptions, subprocess failures, malformed output, environment mismatch, functional mismatch and timeout must not become a pass. The runner records a bounded status without arbitrary exception messages or stderr. If failure occurs before output is writable or before freeze validation, the invocation itself fails and there is no new observation; never present a stale file as this invocation’s result.

## Acceptance and interpretation

Run-level pass requires exact structural equality with the complete expected table and version triplet, including warning lists, entry selection, content strings, sizes and policy decisions. Runner/environment failures are inconclusive, not evidence against the ZIP mechanism. Functional mismatch is evidence requiring investigation; no publication as confirmed. Two passes must match on the complete observation payload, excluding only run label/status wrapper.

Every post-freeze result carries input_sha256 copied from the validated freeze: hashes of PROTOCOL.md, probe.py and run_probe.py. These identify original reviewed artifacts, not environment fingerprints. The post-run independent reviewer must verify that both results' complete input_sha256 mappings equal the approved freeze and the reviewed files' current hashes; a missing or mismatched binding is not an accepted result.

An independent reviewer must subsequently inspect source and both result files against this frozen protocol, especially the first duplicate row’s differing content despite equal sizes and the identical-byte rejection control. The reviewer’s work is independent review, not another execution. Report observed bytes and selection only; no performance measurement, real runtime loading, production incident or cross-engine conclusion is licensed.

Public output, if later authorized, should be a short optional support and host link with the smallest useful table, version limitation, references and diagnostic-versus-delivery distinction. Keep both sources’ total derivative budget under 200 words each across artifacts; do not copy library implementation. Local protocol, paths and environment inspection are not automatically public deliverables.
