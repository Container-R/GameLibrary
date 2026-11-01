# Editorial review: build-tool ordering and output invalidation

2026-11-01. Accepted without correction. This is a source-only review of an additive mechanism in the existing build-engineering role.

## Reviewed content identities

- `roles/engine/build-engineer.md` — SHA-256 `e6973e93f1a37e63272f154646c70471b81aee524d0b73bd15da62ff06570c2c`.
- `research/source-notes/build-engineer-role.md` — SHA-256 `6ad40285d5a5f59ae109ace8a2b32d75c219ac5df5c46b0e1260659a73bc5346`.

Compared both complete diffs with the preceding revision and read their surrounding role/source context. Employer attributions, the historical Cygames case, original candidate-handoff worksheets and SLSA boundaries remain unchanged. Metadata and dated references identify the added CMake scope; prior reading history is retained. No staged text was edited.

## Independent source spot-check

Reopened official [3.31 add_custom_command](https://cmake.org/cmake/help/v3.31/command/add_custom_command.html), including Generating Files, COMMAND and DEPENDS, and [CMP0112](https://cmake.org/cmake/help/v3.31/policy/CMP0112.html). Independently read the corresponding fixed documentation at commit `6acf7153156bb45038be62e79a32ed5a6ea2d00e`: [command lines 102–206](https://github.com/Kitware/CMake/blob/6acf7153156bb45038be62e79a32ed5a6ea2d00e/Help/command/add_custom_command.rst#L102-L206) and [policy](https://github.com/Kitware/CMake/blob/6acf7153156bb45038be62e79a32ed5a6ea2d00e/Help/policy/CMP0112.rst). Read the local independent and main source reviews, which separately resolved the version tag. This editorial pass did not repeat tag resolution or audit generator implementation.

The complete TARGET_FILE expression and executable-target DEPENDS entry are correctly distinguished. The component-expression policy is not misapplied to the complete expression. The actual-built-consumer premise matters and is explicit: merely declaring the generation rule is not an execution promise.

## Practical value and limits

The original example asks separately about table changes and tool recompilation while the output already exists. That distinguishes a missing invalidation edge from missing output on a clean build. Its statement is absence of the specified guarantee, not a universal prediction that the command cannot run for any other reason. It does not imply target dependencies enumerate every plugin, configuration or dynamically read input.

The role remains broader than CMake. The added mechanism is not attributed to Cygames or presented as an incident, actual rebuild trace or performance gain. The proposed checks are explicitly unexecuted; regenerated content is not equated with game-data correctness or release approval. The finite same-directory, single-output, native-tool scope excludes timestamp-preserving changes and the other listed build variants.

Source paraphrase is compact and the source note mainly provides locators and limits. The changed prose contains no private execution identifiers or host-specific runtime metadata. No configure, compilation, generation, test or archive inspection was performed. Acceptance is limited to these exact texts and the documented dependency distinction, not the completeness of a real project's build graph.
