# Two independent in-memory saves: REPLACE versus UPSERT

Status: frozen before execution, NOT EXECUTED. This file is a preparation record, never a receipt. Independent complete code/protocol review is required before execution.

## Purpose and evidence boundary

Observe whether successful saves with identical final parent rows have different child rows under foreign-key cascade. Existing support `保存后装备编号还在，为什么附加词条却没了.md` already derives these outcomes from SQLite documentation; this adds installed-library behavior, not a new mechanism, article, or generic certification. It is not arithmetic testing. No arbitrary UPSERT, ORM, trigger, concurrency, persistence, crash, backup, performance or production recovery claim.

Official documentation read on 2026-11-04; adopted scope:

- SQLite [ON CONFLICT](https://www.sqlite.org/lang_conflict.html): complete technical text; REPLACE uniqueness deletion and DELETE-trigger condition.
- SQLite [Foreign Key Support](https://www.sqlite.org/foreignkeys.html): §2, §4.3 and §6; enabling/readback, CASCADE and recursive_triggers boundary.
- SQLite [UPSERT](https://www.sqlite.org/lang_upsert.html): description, examples, limitations and history; targeted DO UPDATE and minimum version.
- Python [sqlite3](https://docs.python.org/3/library/sqlite3.html): connect, execute, in_transaction, isolation_level and Transaction control via the isolation_level attribute. These selected API/transaction sections were read, not the entire page.

Rolling documentation is separate from the installed runtime's provenance. No binary/source audit is claimed.

## Fixed installed binding and connection contract

Use existing Python 3.12 or newer with standard sqlite3, `LEGACY_TRANSACTION_CONTROL`, and SQLite >=3.24.0. Unsupported version or missing capability fails; no install, upgrade or fallback. Public output records Python technical version and sqlite3.sqlite_version, the linked SQLite version self-report. Neither authenticates official source or binary provenance. No source-id, executable/module path, binary fingerprint, host identity, PID, environment dump, user data, network or extension loading.

Exactly two branches, sequentially: replace, then upsert. Each independently calls:

    sqlite3.connect(':memory:', timeout=0, isolation_level=None,
                    autocommit=sqlite3.LEGACY_TRANSACTION_CONTROL)

Each is a fresh independent database with one connection, never a shared URI and never a branch continuing from previously damaged data. Verify legacy control, isolation_level None and no transaction. On EACH connection outside a transaction, execute and fully consume/close:

    PRAGMA foreign_keys=ON
    PRAGMA foreign_keys
    PRAGMA recursive_triggers=OFF
    PRAGMA recursive_triggers

Readbacks must be exactly [(1,)] and [(0,)]. Record both and the connection properties. No reliance on defaults or another connection. No user-defined triggers exist; OFF is a fixed observation condition, not a trigger-behavior matrix or workaround for cascade.

## Exact schema, data, statements and literal oracle

Each branch creates these two ordinary tables using individual execute calls:

    CREATE TABLE inventory_item(item_id INTEGER PRIMARY KEY,durability INTEGER NOT NULL)
    CREATE TABLE item_affix(item_id INTEGER NOT NULL REFERENCES inventory_item(item_id) ON DELETE CASCADE,affix TEXT NOT NULL)

Then the exact initialization:

    BEGIN
    INSERT INTO inventory_item(item_id,durability) VALUES(41,8)
    INSERT INTO item_affix(item_id,affix) VALUES(41,'frost')
    COMMIT

Every statement must finish execute/fetchall/cursor.close normally. After COMMIT require no transaction. Directly fetch the complete ordered rows:

    SELECT item_id,durability FROM inventory_item ORDER BY item_id
    SELECT item_id,affix FROM item_affix ORDER BY item_id,affix

Both baseline checkpoints must be parents [[41,8]], children [[41,"frost"]], in_transaction false.

The replace branch executes exactly one save statement:

    INSERT OR REPLACE INTO inventory_item(item_id,durability) VALUES(41,9)

The upsert branch, in its independently initialized database, executes exactly:

    INSERT INTO inventory_item(item_id,durability) VALUES(41,9) ON CONFLICT(item_id) DO UPDATE SET durability=excluded.durability

Each save runs outside an explicit transaction under the fixed control settings. Record save_completed only after execute, fetchall and cursor.close all succeed, with actual in_transaction false. Then issue the same two SELECTs again. Literal finals: replace parents [[41,9]], children []; upsert parents [[41,9]], children [[41,"frost"]]. Both transaction flags false. No rowcount, change count, returned cached Python state, RETURNING, hooks or lastrowid substitutes for queried rows. No executescript or connection-context auto-transaction behavior.

Close each connection before the next branch. A closed checkpoint appears only after close returns normally. The strict full oracle is expected.json, authored before execution, never generated or repaired from the observed output. Exactly ten ordered checkpoints: configured, baseline, save_completed, final, closed for each of two branches. Ten checkpoints are not ten independent experiments.

## Failure and artifact discipline

driver.py emits observed checkpoint prefix to stdout on ordinary failure, writes original exception/traceback to private stderr and exits nonzero. Statement and cursor-close errors, and branch and connection-close errors, are preserved together using exception groups rather than one replacing the other. A failed first branch stops before the second. Failed closure cannot pass. No failed statement completion is emitted. No SQLite retry, fault injection or result-dependent branch adjustment.

runner.py is adapted from the previously reviewed deferred-FK runner, not inherited execution evidence. It accepts a new --run-name, refuses existing run roots and symbolic-link inputs/ancestors, verifies four input SHA256 values against manifest, copies exact bytes to a fresh work directory, and verifies again. Source copies and manifest identity are rechecked after the child. This guards accidental changes, not adversarial concurrent substitution or provenance.

Before the only child launch, create and write/read/delete-test eleven separate 0700 directories for HOME, XDG_CACHE_HOME, XDG_CONFIG_HOME, XDG_DATA_HOME, XDG_STATE_HOME, XDG_RUNTIME_DIR, XDG_CONFIG_DIRS, XDG_DATA_DIRS, TMPDIR, TMP, TEMP. Child environment contains only these plus LANG=C, LC_ALL=C, TZ=UTC. Launch existing interpreter with -I -E -B, stdin DEVNULL, in its fresh work directory. This is selected directory/environment isolation, not an OS sandbox or claim that Python reads no standard-library files. No database files are created.

One child deadline is 15 seconds. On timeout/wait failure, kill its own process group and wait at most two more seconds. Record original launch/wait failure and cleanup failures separately. Unconfirmed termination fails and preserves the directory, never claims cleanup. Driver creates no descendants. Raw stdout and stderr go to private-logs, retaining what exists even if interrupted; abrupt termination may prevent driver prefix serialization. No diagnostic paths, process IDs or arbitrary traceback text go in the public-safe receipt.

PASS requires exit0, confirmed termination, no cleanup errors, empty stderr, unchanged inputs, exact allowed JSON fields, valid supported version strings, and all ten checkpoints equal to literal expected.json with identical types. Reject duplicate JSON keys, nonfinite constants, bool-as-int, omitted/extra/reordered checkpoints and extra object fields. A mismatch fails even if final parent rows look right. No source/expected-output edits to obtain success. Preparation failure before launch raises locally and does not create fictitious observation evidence.

Successful output.json and result.json are written through exclusive temporary files and replaced only after complete serialization. Failure has no accepted output.json. The receipt is not execution authenticity proof; raw private logs are not automatically public. No automatic deletion or publishing occurs.

## Allocation and stop

After independent code/protocol acceptance, author runs once with a fresh run name:

    python3 -I -B runner.py --run-name author-1

Independent reviewer reads final bytes and actual output, then runs once as independent-1 with its own new directory. This is same-environment repetition, not blind, cross-platform or another implementation. No rerun after failure without diagnosis and a recorded new execution plan. Stop after this bounded result and independent review; publication requires separate artifact/privacy and reader review. Existing native archives remain unchanged.
