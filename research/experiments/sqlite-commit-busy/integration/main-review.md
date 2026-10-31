# Main integration acceptance

2026-10-31. Read the actual reconstructed `run.py` / `worker.py`, author and independent reviewer receipts, raw-state/SQL-trace checker, protocol and main article extension. Independently reopened SQLite Transaction §2.2–2.3/§3 and File Locking §3. Transaction page reports last update 2026-02-18; locking page 2025-05-31, both rolling documents accessed2026-10-31, not authenticated installed-build source.

The observed held-reader COMMIT returns code5 with pending writer125 versus reader100; after reader release, the same writer COMMIT succeeds with one reward mutation. The raw SQL callback trace, full rows, two separate fresh-read processes across author/reviewer runs and exact base64/hash archives support the narrow conclusion. Main `check_archives.py` independently checks both retained runs using literal expectations under normal and optimized Python; outputs agree. It reads archives only, executes no SQLite or author code, and makes no new runtime claim.

Original ledger and BEGIN-contention file bytes remain unchanged. Existing article preserves old scope and adds this branch; no new indexed article. Reviewer `check.py` and run metadata retain historical workspace paths and are not automatically relocatable. For portable archive checks use `python -B integration/check_archives.py /path/to/sqlite-commit-busy` (or `python -O -B`), from a new checkout; for new runtime evidence choose a new external output directory via `run.py`.

Runner source hashes are measured at start, not a hostile concurrent-source modification defense; unsigned output hashes provide consistency, not execution authenticity. Timeout/error branch code was read but no injected timeout or optimized fixture execution is claimed. Main verifies normal/optimized archive checkers, not optimized SQLite behavior. The unique UUID/terminal check is specific to this fixture, not a claim that the generic fresh Godot harness runs SQLite.

Pre-reset local logs remain unavailable. Only new post-reset author/reviewer UUIDs and source hashes are published. Publication and archival recovery are separate from database transaction recovery; neither supplies power-loss evidence.
