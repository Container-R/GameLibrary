# Recovery queue contract checks

Run from repository root:

```sh
python3 scripts/queue/validate_queue.py .
python3 scripts/queue/adversarial.py
python3 -O scripts/queue/adversarial.py
```

The validator is read-only. It checks task/taxonomy IDs and discipline references, and optional `artifact_paths`. Paths must use normalized repository-relative POSIX spelling, remain within the resolved root (including existing symlinks), and exist when status is exactly `published`. Directories are allowed; their children/content are not verified. Missing planned paths are allowed. Legacy `expected_artifact` prose and additional statuses remain compatible.

The initial migration adds paths only for tasks 0045–0049. Omitted or empty fields mean no artifact-path coverage, not a successful check of all historical task outputs. The report counts declared paths, including safely spelled planned locations; it is not a count of published/verified artifacts. This is not a complete queue-schema validator or a concurrent-filesystem security boundary.

The 15 test methods comprise 9 author and 6 independent methods. Both normal and optimized runs enforce checks through explicit exceptions/unittest assertions. Tests create temporary isolated directories; no engine/network calls. JSON duplicate keys and explicit nonstandard NaN/Infinity tokens reject, without claiming strict validation of every unrelated numerical field.

[Evidence and migration record](../../research/audits/queue-contract-guard/README.md) preserves the original RENDER rejection before GFX correction, independent review and current integration results. Historical outputs describe their observed queue, not the latest state.
