# Independent SQLite writer-contention review

2026-10-31 16:01 UTC. Read author proposal, ledger.py, worker.py, run.py and README; copied only three frozen code files to fixture/. Ran `PYTHONDONTWRITEBYTECODE=1 python3 research-drafts/deep-qa/sqlite-writer-contention/fixture/run.py`: one handshake sequence, four actual child processes passed. Not four independent contention scenarios. No source/original database/main-tree edits or remote writes.

Raw oracle: `python3 research-drafts/deep-qa/sqlite-writer-contention/check_raw.py research-drafts/deep-qa/sqlite-writer-contention/fixture/results` passed. Per-role raw CONFIG/EVENT lines exactly match parent transcript receive records. Both READY precede sendAPPLY_HOLD; HELD precedes sendTRY_BEGIN; actual BUSY_OBSERVED precedes sendCOMMIT; COMMITTED precedes sendRETRY_SAME. Code confirms real SQLite BEGIN call catches OperationalError and checks actual code/name, not fabricated BUSY. B read100/no reward while A uncommitted125/reward; after Acommit Bduplicate125, final fresh reader125 with exact two rows/sum/integrity. Config readback and runtime metadata consistent, all four exits0/cleanstderr. Output independent-output.json preserves observations.

Runner uses pipe flush/Queue handshakes, no sleep ordering. Cleanup inspected: finally polls, terminates live child, waits bounded2seconds then kill/wait, joins drain threads and preserves transcript/raw output. Normal path verified; no separate timeout-failure injection, no universal guarantee of reaping an OS-uninterruptible child or handling every startup/cleanup exception. README correctly says cleanup code not exhaustively tested.

Final DB lossless base64 produced in fixture/results/ledger.db.base64; independently decoded bytes/size/hash against summary and actual final database, all match. Summary serves manifest. Output notes original_runtime_file_compared=true. On archived copy with runtime DB omitted, checker still verifies decoded size/hash and reports original comparisonfalse explicitly; historical path is not required. This is final after-close state, not a held-transaction snapshot; no SQL reconstruction.

Source hashes:
- ledger.py0dac2e06ee86007d6f09aa5e5bd17b92185bcf6d96ec679b7bb0ecb6f016b5a7
- worker.py6aee69d65917d338716fcf4018d52f2112ae3516556f70e2293e1732d876acf7
- run.py3efe3e3f5d85ef2b9c012a3e3b195e99cbec7698c0b7c95e134c625220a40d6c

No material issue within scope. BEGINbusy/no active transaction differs from COMMITbusy; no evidence of fairness/performance, generalized isolation, production retry policy, power-loss durability or award authority. Source_id and binary hash remain identification, not build authentication. Local-ready only.

Archived checker: from this directory run `python3 check_raw.py results`. Runtime database directories are omitted; summary absolute paths remain historical receipts. The base64 snapshot is the lossless final database. Avoid rerunning fixtures in the evidence archive; use disposable copies.

## Local integration acceptance — 2026-10-31 16:03 UTC

Read staged experiment README, archived review README, economy article subsection, and old termination-fixture cross-link. No runtime repeat. Relative Markdown links resolve; archived checker invocation `python3 check_raw.py results` matches its packaged location. Historical draft commands and absolute database paths are retained as receipts, not checkout dependencies. New three code files match reviewed draft bytes; old termination worker.py/run.py likewise remain unchanged.

No material issue. Article distinguishes each author/reviewer one sequence with four processes from the earlier four scenarios/ten processes. BEGIN BUSY, absence of active transaction, held-state old read, commit-before-retry, exact duplicate receipt and fresh final reader claims match observed protocol. COMMIT BUSY, fairness, throughput, cancellation and full isolation remain untested. Base64 is final after-close snapshot, not crash/held state. Registry 103 is an integration-reported consistency count, not a raw-protocol/database validation claim or a new runtime measurement; this acceptance does not rerun it.

Reviewed staged hashes:
- experiment README.md: 3c579eb25acd811ab15fff3bdede78a209645d62faf90945ae4cb0730aa33625
- review/README.md: 47186e4ccded9ae0a720a9a6358505de8219321ce7c268e91fa7ab175d59f674
- solutions/design/single-player-economy-ledger.md: 54ed5a1be88c99023d07d37806c523d5477f619271a45bdbb67b594c72b739e4

Only this draft review addendum was written. Main staging and remote unchanged by reviewer.
