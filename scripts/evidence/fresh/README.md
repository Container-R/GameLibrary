# Fresh invocation wrapper for six unchanged legacy Godot runners

Additive Linux tooling, 2026-10-31. The frozen protocol was saved before implementation; see the [archived protocol](../../../research/audits/fresh-invocation-harness/author/protocol.json) and [integration audit](../../../research/audits/fresh-invocation-harness/README.md). The six original runner files and their historical results are unchanged. This wrapper does not repair their cleanup ordering: it constructs fresh source-only copies and makes consumers require a new invocation receipt.

## Trusted input and acceptance boundary

`harness.py` and adjacent `registry.json` are the trusted reviewed consumer/allowlist. The registry pins exact sources for six fixtures. It copies only listed original files, never archived results/history/reviews/cache. Symlink components and non-normalized/traversing/absolute artifact paths are rejected. Every invocation gets a new UUID directory outside the inspected repository; the caller must retain the ID it requested, not guess which old result is latest.

Receipt states are STARTED, REJECTED and ACCEPTED. Acceptance requires current child exit 0, no timeout/unexpected surviving descendant group, the registered unchanged source set, a newly created summary matching the approved fixture adapter, and hashes binding stdout/stderr/summary/results. The consumer checks expected UUID, current harness/registry hashes, source pins, output containment/hashes and the adapter again. An optimized child can never be accepted even if it hypothetically exited with code 0.

Five legacy summaries have no top-level PASS. The focus adapter validates gate/naive/guarded entries, zero exits and checks=passed; it compares raw RESULT_JSON to parsed records without requiring a nonexistent status. It does not duplicate the entire focus semantic oracle: legacy source pins and its checks remain part of the acceptance basis. Independent semantic review is separate.

**Normal mode is deliberately enabled only for godot-focus-boundary.** The other five are registered for the checked early-rejection path, not silently advertised as normal adapters already validated.

## Author campaign results (relative evidence names below are in the audit author directory)

- Six real copied legacy runners invoked with -O: all exit 1, terminal REJECTED, no archived summary copied. `rejections.json` identifies the exact invocation directories/receipts and raw stderr.
- One actual normal focus runner: ACCEPTED; its three behavior cases gate/naive/guarded passed and the separate consumer accepted the expected UUID. `positive.json` points to this call.
- The pinned focus runner source invokes Godot `--version`, `--help`, then three behavior cases: **five source-audited Godot subprocess calls, three behavior cases**. The wrapper observes the outer Python child; it does not claim independent syscall instrumentation of all five. Legacy evidence has `version.txt` and three case logs, but no separately archived raw help response.
- Fifteen isolated unittest methods passed, including changed ID, source, output or registry, STARTED, nonzero exit with a summary, zero exit missing summary, an optimized-child receipt, non-normalized paths and symlink escapes, and a copied-origin historical PASS that was not transported to its new work directory. The latter invokes one additional copied focus -O rejection with no engine; do not count it as another normal focus run.
- Synthetic timeout child printed PARTIAL then was terminated in its own session; actual receipt exit -15, timed_out=true, group_remaining=false, partial stdout preserved. Other actual synthetic children cover exit 7 with a PASS summary and exit 0 without a summary. They are not Godot runs.
- Original six fixture trees: 306 files, all hashes and full file set unchanged (`original-before.json`, `original-after-check.json`). Registry/source snapshots remain exact.

No actual failures were discarded. Synthetic negatives are expected rejections, not successful engine behavior observations. Raw test output and synthetic process outputs are retained.

## Commands and publication layout

Publish tool bytes unchanged at `scripts/evidence/fresh/harness.py`, `scripts/evidence/fresh/registry.json`, and `test_harness.py`. Archive this run's protocol/results under `research/audits/fresh-invocation-harness/`; historical absolute paths in receipts remain raw metadata, not claimed current locations.

From a checkout, choose a **new external output directory**:

```sh
python -B scripts/evidence/fresh/harness.py invoke . /tmp/new-fresh-runs godot-focus-boundary
python -B scripts/evidence/fresh/harness.py consume /tmp/new-fresh-runs/UUID --expected-id UUID
python -B scripts/evidence/fresh/harness.py invoke . /tmp/new-fresh-runs godot-pause-input --optimize-child
```

The last command intentionally returns code 1 with a REJECTED receipt. The first prints the real UUID/directory; use that value for consume. No arbitrary shell command or unregistered fixture CLI is available. Do not rerun inside the archived evidence folder or overwrite prior logs. Registry source changes require review and new pins, not blind acceptance.

Portable isolated tests can consume a copied accepted invocation with its original UUID directory name:

```sh
FRESH_POSITIVE_INVOCATION=/path/to/accepted/UUID FRESH_TEST_OUTPUT=/tmp/new-fresh-test-results python -B scripts/evidence/fresh/test_harness.py
```

Without an override, the author-local test reads positive.json beside the tool; that file contains the actual author workspace path. Archive consumers should pass the explicit environment path. Tests execute small synthetic children and one copied -O rejection, **not a normal engine run**.

## Process and filesystem limits

Linux Popen uses a new session; timeout handling signals only its own process group (TERM then KILL). Normal parent exit also checks for leftover group members and rejects the invocation if unexpected descendants are detected. It makes bounded termination attempts; it does not guarantee that every descendant is reaped. No global process kill or shared engine cleanup. Child stdout/stderr are direct files, preserving partial output.

Only a complete final receipt is consumable. Receipt publication uses a same-directory temporary file rename, not fsync or crash durability. Directory permission errors, disk full, forced harness termination, uninterruptible OS operations or failures during final receipt write can leave STARTED/missing/incomplete evidence. Such conditions are not accepted; cancellation cannot be guaranteed for every OS failure. Cleanup does not delete original archives; this bounded version preserves its new work/runtime directories for diagnosis rather than promise universal cleanup.

Consumer checks are integrity/freshness consistency, not tamper-proof signatures or execution authenticity. Someone able to rewrite trusted tool or registry or manufacture consistent receipts can forge evidence; this is not an adversarial sandbox. The binary SHA-256 is measured by the wrapper; self-reported official version is not authenticated source identity. A new hash measurement must not be retroactively inserted into historical fixed-step results.

No new knowledge article, no source hash rewrite, no six normal positive rerun claim, no installs or third-party assets.
