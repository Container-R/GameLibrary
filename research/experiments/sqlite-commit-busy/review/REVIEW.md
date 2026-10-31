# Independent post-reset SQLite COMMIT BUSY review

Accepted 2026-10-31 20:58 UTC, within the frozen finite scope. Prior review files and outputs are unavailable after the environment reset; this is a **new** source review and new execution, not reconstructed historical evidence. See RECOVERY-NOTE.md.

## Current evidence

Copied run.py, worker.py and protocol.md into fixture/ without changes. Ran `python -B fixture/run.py <absolute review-directory>/evidence` (from workspace using full paths); run.stdout records the new UUID `09655ed4-1da6-452e-a086-97a8960926cc`. Exactly two child processes ran: one scenario process holding two connections with overlapping transactions, then a fresh read-only observer. Outer and child stderr are empty. No negative injection or optimized run was performed.

`python check.py` independently accepted literal raw event ordering, both DELETE/EXTRA/busy_timeout configurations, complete account/receipt snapshots and active transaction states, SQLITE_BUSY code 5, reader release, and fresh-reader integrity result. Its literal non-SELECT SQL list requires one BEGIN IMMEDIATE, one UPDATE, one INSERT and two COMMIT attempts. It imports no author implementation. It also checks raw/parsed equality, source/interpreter/output hashes and the 16384-byte decoded database archive. Exact source hashes and self-reported SQLite identity are in check.stdout. Author's new archive was separately decoded and checked against its own bytes/hash in author-archive-check.json; no author/reviewer byte identity is required. Decoded database was not written or reopened by this checker.

## Source and implementation boundaries

Independently re-read [SQLite Transaction §2.3 and §3](https://www.sqlite.org/lang_transaction.html) and [lockingv3 §3](https://www.sqlite.org/lockingv3.html) on 2026-10-31 after reset. The former supports retrying COMMIT while this reader-blocked transaction remains active, while distinguishing other errors which can roll back; the latter is rollback-mode lock guidance, not WAL. These rolling pages do not authenticate the installed library build.

Reviewed code uses explicit SQL transaction control; fetched cursors close while the reader transaction remains open. The writer trace is enabled after initialization. COMMIT-only retry does not reapply the reward. Python in_transaction is observed; C autocommit and OS lock states are not directly instrumented. The two connections execute sequential calls, not a two-worker concurrency stress test.

Checks use explicit exceptions rather than assert. Each new UUID starts with STARTED, and process errors or timeout cannot produce PASS through the handled paths; timeout partial outputs are retained. Per-child timeout is 10 seconds, not a universal OS cancellation guarantee. Failed temporary databases are not preserved; final closed database packaging is not a crash snapshot. No additional failure cases were executed during this review, and no power-loss, WAL, fairness, performance, game integration or general retry-system guarantee is inferred.

No material issue found. Main tree, original author outputs and remote repository were not modified.
