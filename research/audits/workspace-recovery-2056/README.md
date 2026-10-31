# Workspace snapshot recovery, 2026-10-31 20:56 UTC

A read-only local command failed with an exec-server transport disconnect. The next command saw an older workspace snapshot. No GitHub write was in flight. Canonical HEAD remained `3721e5b6ae2fd506aca022c30e489524c03442f0`; published research was intact.

The main worker reconstructed all **2,005 remote blobs** from matching old local files, retained upload content and 128 missing blobs fetched through the authorized GitHub connector. Every recovered file matched the canonical Git blob SHA-1. The restored snapshot passed 285 static archive consistency checks, taxonomy validation (27 source-backed articles) and queue validation (54 tasks / 24 declared paths). These are restoration checks, not new execution of archived experiments.

Uncommitted SQLite COMMIT-BUSY author and reviewer raw logs/database archives were unavailable. Earlier reported passes were not relabeled as recovered raw evidence. The [new fixture](../../experiments/sqlite-commit-busy/README.md) contains reconstructed source/protocol with new hashes, newly executed UUIDs and a new independent repeat. Historical reports remain historical; only the new retained runs support the published extension.

`recovery.json` preserves the actual recovery checkpoint before SQLite integration. Some paths in that record name local working artifacts rather than public archive links. No schedule, visibility or access restriction was changed during recovery.
