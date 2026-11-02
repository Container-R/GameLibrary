# Proposed protocol: WAL reader-to-writer upgrade after another connection commits

Status: pre-execution review candidate. No database observations yet. Purpose: distinguish an obsolete read snapshot from a blocked COMMIT, using two connections and one predetermined, same-thread interleaving. No threads, server, network, crash, power-loss or timing study.

## Scope and prerequisites

Use the already available Python standard-library sqlite3 binding, no install or upgrade. Require Python 3.12 or newer and explicit support for autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL; if unavailable, stop at the capability gate rather than changing connection semantics. Capture public technical Python/SQLite version strings, not executable locations, local binary fingerprints, PIDs or the full environment. Require structured sqlite_errorcode/sqlite_errorname for the observed exception; absence is unsupported, not accepted by message guessing. Do not infer official binary/source identity from a self-reported version.

A parent creates an exclusively owned fresh temporary directory. Before each child launch explicitly prepare and validate HOME, XDG_CACHE_HOME, XDG_CONFIG_HOME, XDG_DATA_HOME and TMPDIR using the existing reviewed helper or exact equivalent. Own cleanup and partial failure. This checks selected writable locations, not a sandbox. Use isolated Python mode, a fixed child timeout of 15 seconds and capture finite stdout/stderr. Raw unexpected traces remain internal until privacy review; do not publish paths verbatim. No shell in the child command, extension loading, attachment of other databases or URI shared cache. Each execution uses a new regular file database in the owned root; no user data.

Open distinct A and B connections with autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL and isolation_level=None so SQL BEGIN/COMMIT/ROLLBACK are explicit; timeout=0 and PRAGMA busy_timeout=0. Read back and require journal_mode=WAL, read_uncommitted=0 and busy_timeout=0 separately on A and B; fully consume/close every SELECT cursor. Initialization is committed before the sequence. Minimal tables: balance(account PRIMARY KEY, amount), operations(account, request_id, result_amount, PRIMARY KEY(account, request_id)); initial account player-one balance100 and no operation for reward-one. One reward adds12. No real account or network identity is used.

## Frozen ordered sequence and observations

1. A BEGIN DEFERRED; select reward-one result => absent, balance100, in_transaction true.
2. B BEGIN IMMEDIATE; select same request => absent; update balance +12 and insert operation result112 in the same transaction; COMMIT. Observe B in_transaction false and a B query sees balance112 plus exactly one operation.
3. A repeats the same queries without ending its transaction: still absent and balance100. Fully finish cursors. This shows the retained view, not an assertion that B failed.
4. A attempts UPDATE balance SET amount=amount+12. Expected structured exception code517 SQLITE_BUSY_SNAPSHOT, primary code5. Record actual code/name and require A.in_transaction is true. Do not infer a successful mutation from the statement being attempted. If a different result occurs, preserve it and fail the gate; no fallback from517 to arbitrary BUSY.
5. A tries that same UPDATE once more without ending its transaction. Expected same517 and A.in_transaction is true; this finite retry shows that this particular unchanged snapshot did not become writable. It is not a waiting-duration experiment and has no sleep or infinite loop.
6. A ROLLBACK; observe in_transaction false. A BEGIN DEFERRED; query same operation and balance => stored result112, current balance112, exactly one operation. Choose the duplicate-result branch; deliberately perform no new increment. Require A.in_transaction true after the new read, then A COMMIT and require it false.
7. Close A/B; reopen the same file as a fresh connection and observe final balance112 and one operation result112. This tests visibility after close/reopen, not crash or power-loss durability. Close cleanly before removing the owned temporary directory.

Check actual journal mode and relevant transaction flags at the stated steps. Every JSON observation must contain named step and values, with no private path. Never generate PASS before all conditions and cleanup outcomes are known. Failure produces nonzero status and retained diagnostic, not a success record copied from an earlier run.

## Repeats and independent check

After protocol and harness review, the author may perform two invocations with separate fresh roots. A separate reviewer is allocated exactly two invocations of the same frozen fixture in separate fresh roots after inspecting source and initial results; any additional invocation requires a separately recorded reason and revised execution allocation before launch. Distinguish author repeats from independent execution. Do not count preliminary capability failure as a successful invocation or a new semantic condition. Stop after this bounded observation and review; no matrix of modes/platforms or invented performance measurements.

A result consumer must fail closed for wrong step/order/value/code/name, missing or duplicated steps, altered fixture identity, missing final result, false mode and failure status. The consumer must reject duplicate JSON keys, non-finite numbers and booleans presented as integer values; it must check the recorded per-connection configuration and transaction flags. Pure mutation tests of the consumer are not native observations. Keep fixture/public-output identities, but do not export installed-binary or private execution-receipt fingerprints. Full public package gets an independent privacy/identity review before publishing.

## Reader claim boundary

If observed, the result illustrates this installed SQLite binding and precise WAL sequence. It supports starting from a new transaction and re-reading the business decision after discarding an obsolete snapshot, rather than treating every BUSY as permission to replay a reward or merely retry COMMIT. The general mechanism comes from SQLite's official isolation and error documentation. It does not implement an online reward service, prove exactly-once semantics, validate cross-service effects or establish a universal retry policy.

This is additive evidence: the existing three historical SQLite DELETE-mode experiments remain unchanged and their original limits remain intact. Article placement is decided after the actual result; no extra book is promised merely for running this fixture.
