# Six Godot runners: early rejection leaves historical summaries

Local audit, 2026-10-31. This is a Python runner rejection experiment, **not a new Godot run** and not an assessment of engine authenticity or safety. The six current runners were read from `gamelibrary-work`; historical runner snapshots were excluded.

## Observed result

All six isolated invocations exited **1**, emitted no stdout, and left seeded `results/summary.json` byte-for-byte unchanged. The sentinel says PASS but explicitly identifies itself as historical. The rejection occurs before the summary cleanup and before any engine command. Therefore “summary exists and says PASS” is not a valid latest-invocation success test.

| Current fixture | Optimization rejection line | Summary unlink line | Result |
|---|---:|---:|---|
| godot-fixed-step | 14–15 | 21 | exit 1; sentinel retained |
| godot-pause-input | 13–14 | 18 | exit 1; sentinel retained |
| godot-focus-boundary | 11–12 | 16 | exit 1; sentinel retained |
| godot-import-boundary | 12–13 | 16 | exit 1; sentinel retained |
| godot-navigation-sync | 12–13 | 16 | exit 1; sentinel retained |
| godot-animation-events | 3 | 6 | exit 1; sentinel retained |

Paths above are under `research/experiments/`, each file `run.py`. Source SHA-256, actual temporary command paths, return codes, output digests, sentinel digests and post-run file lists are in `results.json`; unedited stdout/stderr are adjacent. Optimization rejection works as intended; retaining an earlier artifact is a consumer/freshness ambiguity, not evidence the runner falsely returned success.

## Procedure and limits

`audit.py` reads and copies each current runner only into a separate auto-cleaned TemporaryDirectory; it does not copy project/scene/GDScript/assets. It seeds one historical PASS summary, then invokes the current Python executable with `-I -B -O`, empty PATH, captured outputs and a 10-second subprocess timeout. The extra isolation and no-bytecode flags do not disable optimization. Before invocation an AST gate checks that only reviewed standard-library imports/docstring precede an unconditional optimization-mode raise. In this observed control flow no engine binary is queried, loaded or executed; the animation runner's absolute binary path is never reached. All copied runner directories contain only run.py and the sentinel afterward. The original runner bytes are rechecked unchanged.

This is six early-rejection cases, not broad fault injection. It does not test normal engine execution, later assertion failure, syntax/import failure, cleanup permission errors, concurrent writers, crash durability or genuine execution of prior summaries. Timeout is a subprocess guard, not a universal filesystem cancellation guarantee. Temporary paths in tracebacks are retained as raw evidence, so reruns need not produce identical stderr digests.

Reproduce from workspace root (writes only the specified draft output and temporary directories):

```sh
python3 research-drafts/runner-rejection-audit/audit.py gamelibrary-work research-drafts/runner-rejection-audit
```

## Narrow documentation changes proposed, not applied

Create shared note `research/source-notes/runner-invocation-freshness.md`. Link all six fixture READMEs with `../../source-notes/runner-invocation-freshness.md`. Keep provenance/authenticity note separate: this issue is result freshness, not binary identity. Suggested shared text:

> `results/summary.json` is an archived result, not a latest-invocation status channel. These runners reject Python optimization mode before their normal-path removal of an old summary. Thus a rejected invocation can leave a historical success summary in place. Consumers must capture and check the exit status of the specific invocation and retain a fresh invocation receipt (command, source identity, start/end, return code and output references). A nonzero exit must never be overridden by a pre-existing summary. For accepted runs, bind the inspected summary to that invocation rather than inferring freshness from existence, PASS text or modification time alone. These current summaries do not contain a unique invocation ID; use a fresh isolated run directory and an external receipt when freshness is required. Archived integrity checks establish consistency of selected historical files, not that the most recent attempted run succeeded.

Do not promise that all failures erase old results. A future runner/consumer protocol could introduce invocation IDs or dedicated fresh output directories, but this audit neither changes the runners nor claims that such a protocol is already implemented. Normal reruns may overwrite archive outputs; readers should work in copies, not rewrite preserved evidence.

Exact README wording review (line numbers at audited snapshot):

- `research/experiments/godot-fixed-step/README.md:16`: “启动先移除旧summary” is overbroad. Replace with “通过优化模式拒绝门槛、进入正常运行路径后移除旧summary；门槛前拒绝可能保留历史summary。须以本次退出状态及新调用回执判断，不得只读已有summary。” Keep subsequent all-checks-required claim scoped to new summary creation.
- `research/experiments/godot-pause-input/README.md:17`: already says “每次正常运行先移除旧summary”; not an all-failure-clear claim. Append shared-note link explaining early rejection retains historical output.
- `research/experiments/godot-focus-boundary/README.md:19`: “禁止-O…先删除旧summary” is ambiguous about order. Say “先拒绝-O；正常路径随后删除旧summary。失败不生成本次成功summary，但早期拒绝可能保留历史summary”，then shared link.
- `research/experiments/godot-import-boundary/README.md:13`: “每轮先移除旧成功summary” needs “通过优化模式拒绝后，正常路径…”。 “均不能生成成功summary” remains correct as a claim about new successful output, not deletion of historical output.
- `research/experiments/godot-navigation-sync/README.md:15`: “每次先删除旧成功summary” → “通过优化模式拒绝后，正常路径先删除旧成功summary”；append shared note.
- `research/experiments/godot-animation-events/README.md:40`: “拒绝Python-O，先移除旧summary，任何异常不生成PASS摘要” → “先拒绝Python-O；正常路径随后移除旧summary。异常不会生成本次PASS摘要；优化模式拒绝仍可能保留历史PASS摘要”，then shared note.

`godot-fixed-step/run.py:20` comment “Never leave an older success summary beside a partially failed new run” is broader than early-rejection behavior. No source change proposed for this documentation-only patch: preserve hashed code and explain that the comment applies only after the cleanup point. If source is changed later, distinguish its new hashes from the historical run evidence.

No main-tree or remote writes were made. Public-audience publication hold remains in force.

## Integrated archive note

The proposed shared note and six scoped README changes were applied locally after this audit; the six runner source files remain unchanged. Original prose above records the review before integration. From a repository checkout, reproduce into an external disposable directory with `python3 research/audits/runner-rejection/audit.py . /tmp/new-runner-rejection-audit`; the tool refuses an output directory inside the inspected archive. Do not overwrite this historical audit.

## Read-only integration acceptance — 2026-10-31 15:49 UTC

Reviewed staged shared note, all six fixture README clarifications, and `research/audits/runner-rejection/` archive. No material correction required. Text explicitly preserves six unchanged runner implementations; ICU-only fixes are not attributed to Godot runners. Historical PASS files are not latest-invocation success and no new engine run is claimed. The archive's final integrated note provides checkout-relative invocation with external `/tmp/new-runner-rejection-audit` output; original workspace command is retained as historical prose, not the portable command. All local links in the seven scoped documents resolve. Archived audit code/results/raw streams match the draft byte-for-byte; archive SHA256SUMS validates; all six current runner hashes still match the audit receipt. This acceptance ran only read/hash/link checks, not runners or engines, and made no main-tree edits.

Publication note: statements about an active publication hold above describe the audit-time state. The owner later authorized public continuation. The ICU reference describes separately reviewed local work, not an ICU artifact included in this correction batch.
