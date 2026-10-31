# Additive queue contract guard

Draft-only tooling; no main-tree migration or remote write. Mirrors the existing taxonomy tests' use of standard-library JSON/unittest but adds the missing queue reference check.

## Scope

`validate_queue.py` reads `taxonomy/disciplines.json` and `.agent/queue.json` below the supplied root. It checks:

- taxonomy IDs and task IDs are nonempty strings and unique;
- each task discipline refers to an actual taxonomy ID, including valid legacy IDs;
- **only when present**, `artifact_paths` is an array of unique normalized repository-relative POSIX paths;
- absolute paths, Windows drive spellings, backslashes, traversal/dot components, empty components and control characters are rejected;
- resolved paths remain under the repository root, including existing symlink parents;
- for a task whose exact status is `published`, optional paths must exist. Files and directories are both permitted as artifact locations. Other states may declare not-yet-created locations.

Legacy `expected_artifact` remains free text and is not interpreted as a path. Optional `artifact_paths` may be absent or empty. Unknown/additional task states and unrelated metadata remain compatible. This is not a complete queue-schema validator, a security scanner, or proof that existing files contain reviewed evidence. Presence of a directory does not verify its children. Symlink containment is a point-in-time check, not protection against concurrent filesystem changes.

The parser rejects duplicate JSON keys and explicit nonstandard NaN/Infinity tokens; it does not claim a general strict numerical metadata validator. Core fields are separately type-checked. No network, installed engine, test fixture or downloaded code is executed by this tool.

## Actual commands and outputs

```sh
python -B test_queue.py
python -B validate_queue.py /path/to/repository
```

Nine isolated unittest methods passed; raw outputs are `tests.stdout.txt`/`tests.stderr.txt`. Cases include unknownRENDER, duplicate task, traversal/absolute paths, published missing versus planned missing, legacy prose, flexible states, malformed optional arrays and symlink escape.

Against `gamelibrary-publish-broker`, the actual CLI exited1 and reported TASK-2026-0048 discipline `RENDER`. `current.*` preserves that failure, not a fabricated clean run. A separate in-memory-only correction to GFX then passed48 tasks and0 optional artifact paths; receipt in `in-memory-correction.json`. **Zero paths checked means legacy tasks have not been granted artifact coverage.** No original queue bytes were changed.

`artifact-path-suggestions.json` is a proposal for0045–0048 only.0045–0047 point to actual published articles/experiment directories.0048 remains empty because its exact destination was not frozen in this audited queue; the integrator should choose it later. No fictitious migration or finished artifact is asserted. The optional field can be added without altering existing `expected_artifact` or schema_version.

CLI prints a success report only after all checks; first failure prints a diagnostic tostderr and exits1. It does not write reports into the repository or overwrite previous output. A caller that redirects stdout owns that output file and must inspect this invocation's exit status, not an older PASS file.
