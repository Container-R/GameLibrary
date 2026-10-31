# Physics callback archive association checker

`python check_archives.py V1_ROOT V2_ROOT REVIEW_ROOT`

Portable positional roots, no engine execution, no imports of author/reviewer validation and no access to historical absolute paths or current binary. Author v1/v2 roots retain `results/UUID`; review retains `fixture/` and `evidence/UUID`. Do not rename archived source snapshots; v1's three snapshot names are fixed in the checker. No large assembled archive is needed or produced.

Actual normal and `-O` invocations against local author/reviewer archives exited 0 with identical stdout and empty stderr. Explicit exception checks remain enabled under optimization. Counts per archive: v1 three attempted direct behavior processes, none accepted, three successful version commands; v2 author has two invocations (before and after the stdout-error guard), each with two accepted configurations plus one version command; independent v2 review repeats the same two configurations plus version with the old runner, not extra scenario types. Total: 9 behavior-process attempts (3 failed v1, 6 accepted v2), 6 version commands, only 2 unique accepted configurations. Checker execution adds zero engine processes.

Checks pin all four source hashes for each of the three failed snapshots and v2 source, bind UUID receipt/source/output manifests, require complete output sets and raw/parsed single-RESULT_JSON association, literal geometry/body mode/settings, actual callback body IDs, causal ordering and exit before the second entry, four consecutive **pre-physics boundaries** per declared observation window, node-property phase and finite final overlap. The exact direct error envelope has one primary and three bounded context lines; deferred stderr is empty. Historical failure stderr is retained and hash-bound, not forced through the successful v2 error whitelist.

The first failed process records returncode -6; its crash diagnostic mentions signal 11. Those are different observations, not permission to rewrite either. The original no-entry cause remains unresolved. Successful kinematic v2 does not retrospectively pass or diagnose static-body v1. A finite absence of deferred re-entry does not establish permanent disablement, universal N+1 scheduling or controller movement.

PASS is static consistency of these receipts and pinned finite observations, not authenticity of logs/build, an engine rerun or arbitrary event validation. Recorded source/runtime identity does not authenticate official provenance. No receipt is changed; checker prints its own result only after all checks. Parser-negative tests in independent review are synthetic and are not counted as engine configurations.

## Runner hardening provenance

Old author UUID `39536c18-7525-4dcc-b264-ca94a2097a2d` and reviewer UUID `a253567d-2230-43ca-9e02-8a8eb8415367` bind runner `3db75326…`. New author UUID `b3e7b2d4-351b-4342-8b6b-a084fda177f8` binds runner `2b00a967…`. The author historical snapshot contains only the old runner alongside its notes; unchanged GDScript/project/contract are bound from v2 root. Reviewer fixture preserves all four old files. No old receipt is upgraded to the corrected parser. All actual native stdout logs are independently checked clean here. Synthetic parser omissions/fixes remain reviewer evidence, not additional native runs.

Publication selection: final check_archives.py, README.md, normal/optimized stdout/stderr only; pre-hardening/ is local implementation chronology and need not be copied.
