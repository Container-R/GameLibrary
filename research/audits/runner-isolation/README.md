# Additive future-runner environment helper acceptance

- [Source gate](source-gate.md), [author evidence and amendment](author/README.md), [independent review](review/REVIEW.md).
- [Source and applicability note](../../source-notes/runner-environment-contract.md).
- Production `scripts/evidence/isolation.py` is byte-identical to final author and final reviewer fixture copies. Initial fixtures and their accepted results remain under author/historical-pre-root-guard and review/fixture; they are not relabeled as final runs.
- The exact test copies retain their original `isolation.py` and `protocol.json` imports/identities. Historical README references to research-drafts describe the preparation workspace, not additional public evidence.
- Eight recorded synthetic children total, zero engine processes. Four supplementary unique filesystem scenarios, repeated in normal/optimized mode for initial/final source. No historical runner rerun or migration.

From the repository root, the following **read-only static check** launches no child:

```sh
python3 research/audits/runner-isolation/integration/check_archive.py
python3 -O research/audits/runner-isolation/integration/check_archive.py
```

[Preserved-file manifest](integration/preserved-files.json) pins 1,723 existing experiment/fresh-harness files against baseline commit `7b17492ff1064fdd6c9cdd4f3f41b9236c13f682`. Static consistency does not prove execution authenticity, replay deleted temporary sentinels or guarantee isolation. To rerun synthetic tests, copy the three source files from author/ to a new temporary directory and run the commands in its README; doing so creates new evidence, not verification of the historical child executions.
