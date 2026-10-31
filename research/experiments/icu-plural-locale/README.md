# ICU plural coverage: a valid missing arm can select `other`

## Actual finite result

One author batch, `2f4f411a-b9d7-485e-b837-8d5d1ed5cfe0`, ran on 2026-10-31 after source/protocol/code reviews. It contains exactly three fresh Python children, with fixed configurations below. Each observed one version call, one open, six formats and one close: 9 ICU exported-function attempts and 9 returns per child, 27 total. Loader load records are separate, not counted as extra formatter calls. A separately authorized independent batch is accepted below; it is not included in these author-only counts.

Inputs in order: **0, 1, 2, 3, 11, 100**, each passed as one explicit positional `c_double`.

| Configuration | Locale / pattern | Actual markers in input order |
|---|---|---|
| `en_full` | en / six named arms | OTHER, ONE, OTHER, OTHER, OTHER, OTHER |
| `ar_full` | ar / same six named arms | ZERO, ONE, TWO, FEW, MANY, OTHER |
| `ar_omit_few` | ar / delete only few arm, retain other | ZERO, ONE, TWO, OTHER, MANY, OTHER |

All three opens returned status0/nonempty handle; first format (n0) returned warning status **-127**, remaining five formats status0. Every warning is retained. This run did not call `u_errorName`; numbers are the native status observations, not runtime-generated labels. The warning's resource cause is unresolved. All children exited0 with empty stderr, no timeout and no remaining observed owned process group.

At n3, `ar_omit_few` correctly formats OTHER according to the fallback rule. The separately declared full-pattern FEW intent is therefore **not met**. This is not an ICU parser failure or a claim that a real Arabic translation is wrong. ASCII branch markers are original diagnostic content, not localized UI. A syntactically accepted pattern and English smoke tests alone cannot certify this declared target-locale branch coverage.

## Evidence and identities

- Frozen [protocol](protocol.json): `e44d2d3a7463eeb2669ad1a3ad37d894611d792ee3221642b1d459dda32d377c`, including [source gate](source-gate.md) and independent review pins, literal expected markers, bounded calls and stopping conditions.
- `source-manifest.json`: exact executed child/runner/consumer/tests/helper/protocol bytes.
- `results/<batch UUID>/batch.json`: original batch and configuration identities, source-backed expected order, actual observed child receipts, no later unstarted configuration.
- Each configuration UUID contains `receipt.json`, raw `stdout.txt` / `stderr.txt`, and `consistency.json`. `author-observation.json` is a convenience extraction from these raw records, not the primary source.
- Child UUIDs: en `5f3aa989-086b-43da-99a4-10881748371a`; ar `172771b1-821c-4867-be5d-1a16b54963d6`; omitted few `31d1abc5-36d6-487a-8ad5-ef313e665ceb`.

Version call returned76.1.0.0 in each child. Three checked library paths resolve to `.76.1`; their exact SHA256 and before/after equality are recorded. Comparison source is ICU release-76-1 commit `8eca245c7484ac6cc179e3e5f7c1ea7680810f39`, whose supplemental data declares CLDR46. The source tree and runtime version agreement are **not authentication of the installed build, full dependency closure or actual data-resolution origin**.

The explicit minimal environment contains PATH/LANG/LC_ALL plus the five fresh HOME/XDG/TMP paths from the pinned helper. It does not inherit ICU_DATA, PYTHONPATH/PYTHONHOME or LD overrides. This reduces uncontrolled inputs but is not a sandbox, nor proof that all data and dependencies are sealed. Absolute recorded runtime paths are historical metadata; the temporary directories have been cleaned up.

## Read-only archive verification

From this directory, one example is:

```sh
python -B consume.py results/2f4f411a-b9d7-485e-b837-8d5d1ed5cfe0/5f3aa989-086b-43da-99a4-10881748371a 5f3aa989-086b-43da-99a4-10881748371a en_full --source .
```

Repeat only the static command for the other two recorded UUID/config pairs when checking the whole batch. `consume.py` imports no child/native module, loads no library, and validates pinned source identities, raw hashes, exact full stream order, typed ABI/configuration, lifecycle, bounded units/statuses and literal outputs. It establishes archive consistency, not authenticated execution. It is valid under normal or optimized Python because checks are explicit, not stripped assertions.

`run.py` and `child.py` are **native execution entry points**, not static verification commands. A future execution must use a new output root/invocation and be counted separately; it cannot replace these receipts. No additional run is needed to read this archive.

## ABI and failure boundaries

Linux x86_64 little-endian only; UParseError72 bytes/alignment4 and offsets0/4/8/40, 16 UTF16 units per context. Use uint16, not wchar_t. Fixed C signatures with one explicitly typed variadic double only. All functions are bound before the first version call; library bytes are checked before CDLL, and checked again after cleanup.

Each call flushes attempt before entry and scalar returned facts before the output oracle. Open logs only handle-nonnull, not addresses. Format output capacity64; positive error or out-of-range returned length prevents output-buffer reading. Strict decode and exact marker comparison follow bounded-unit capture. Every nonnull open result is closed in finally, including error paths; a crashed process cannot guarantee that cleanup.

The parent runs configurations serially and stops on the first unexpected failure. The source uses exclusive new UUID directories rather than reusing a summary. The functional batch did not inject startup or timeout failures; one separately counted optimized-startup check is recorded below. No seeded stale-PASS test was performed. Timeout20s bounds waiting, with bounded owned-group TERM/KILL attempts; no universal cleanup/reaping guarantee. An unresolved run_one exception yields an unknown batch spawn total plus the observed receipt lower bound, not a fabricated0. No timeout/crash/open-error path was exercised natively in this batch.

## Pre-native corrections and pure checks

`historical-pre-native-review/` preserves the initial implementation and six-method pure outputs. Source review caught bool/int field aliases, separated event-stream ordering, and possible batch spawn undercount after an exception. The final consumer uses typed fields/full ordering; parent records uncertainty. Direct uint16 construction replaced explicit memmove. See `pre-native-review.md`.

Final eight pure methods passed normal/-O with **zero subprocesses and zero native calls**. These tests inspect records/ABI layout only; they are not extra locale or engine coverage. The original earlier four-pattern `icu-message-boundary` experiment remains unchanged and separately scoped.

## Limits

No Unity/SmartFormat, arbitrary patterns, multiple arguments, fractional operands/lexical trailing zeros, offset or explicit-number precedence, ordinal rules, nested formats, display digits, font/shaping/RTL/layout, translation approval, LQA or players. A double1.0 is not a preserved textual `1.0`. Six finite integers cover these selected marker branches, not every number, regional locale, grammatical construction or game screen. Keep branch selection, semantic intent and actual rendered experience as separate acceptance stages.

## Separately counted startup rejection

The coordinator executed one `-O` parent invocation at 2026-10-31 23:08:03 UTC, UUID `9a6956ee-98c7-4c91-b1cb-08a3299a25b9`. It exited1 before spawning a child, retained a fresh FAILED_OR_INCOMPLETE batch receipt, and recorded all three configurations as not started, zero observed child receipts and zero native calls. Raw parent output/exit and test receipt are in `negative-startup/`. Source hashes in that test receipt were observed **after** the check, not asserted as a before/after capture. This is one startup rejection, not a seeded stale-PASS test, timeout injection or additional plural behavior case.

## Independent repeat closure

Independent reviewer batch `51693796-d462-4068-8d93-cf96d488eb99` completed the same three configurations without retry: three more children, 27 ICU calls including18 formats. A separate standard-library raw checker uses an independently literal table and imports neither this consumer nor native child. It checked both reviewer and author archives without another native invocation. The same outputs and first-format-only -127 warnings were observed.

Combined evidence is **two batches, six children, 54 ICU calls (6 versions, 6 opens, 36 formats, 6 closes)**, all observed attempted and returned. This repeats the same three configurations/six inputs; it is not six new locale cases. The separately counted -O rejection adds zero children/calls. Independent review artifacts are archived by the integrator separately; original author bytes/results are unchanged.
