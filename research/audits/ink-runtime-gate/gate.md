# ink runtime feasibility gate — 2026-10-31

## Actual capability result

Defer runtime experiment. `command -v dotnet mono csi inklecate` found none on PATH. Node exists at `/opt/codex/runtimes/codex-primary-runtime/dependencies/node/bin/node`, self-report v24.22.1; this is JavaScript capability, not an installed ink runtime.

`probe.cjs` uses Node `createRequire(...).resolve()` only (does not execute package code), checking inkjs and ink from workspace, npm-reported global root `/home/agent/.local/lib/node_modules`, and the runtime's node/lib/node_modules resolution roots. All six resolutions return MODULE_NOT_FOUND. Reported global directory does not exist. `npm root -g` emits an existing http-proxy config warning, retained in stderr. No npm install/npx/fetch/download or credentials used. These bounded checks are not proof that no binary exists anywhere on the machine. The npm package named ink is also not by name alone proof of inkle narrative runtime identity.

Initial inline Node probe had a missing closing brace and failed with SyntaxError Unexpected end of input before package resolution; corrected bounded standalone probe then produced saved actual results. That initial failure is not counted as package absence. `probe-output.txt` and `probe-stderr.txt` contain the corrected command results; original shell results available to coordinator. No story compiled or executed.

## Existing knowledge inspected

Read `gamelibrary-work/research/source-notes/ink-v1.2.1-host-boundary.md` and `research/audits/ink-source-independent-review.md`. Existing pin is ink v1.2.1 commit35c63e52f1d36060930dc7ed3cfba38ea224b528. They already cover General-vs-convenience lookaheadSafe defaults, state-vs-host save boundary, content identity and choices. Another abstract reward ledger would duplicate coverage without testing ink.

## Useful new source-only boundary: exact story location vs approximate recovery

Read pinned official CallStack.cs and Story.cs via GitHub plugin:

- [CallStack.cs lines53–105](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/CallStack.cs#L53-L105): thread restoration resolves a saved container path. Missing content can throw; approximate resolution takes an explicit warning path, rather than universally rejecting every non-exact path. The code also restores an index and previous pointer. This local branch is source evidence, not observed behavior of any given edited story.
- [Story.cs lines754–784](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/Story.cs#L754-L784): PointerAtPath distinguishes no recoverable content (error) from an approximate object (warning). Therefore absence of a top-level exception alone is an inadequate project acceptance test for content migration.

Unresolved concrete test if a verified runtime later becomes available: create two tiny original compiled story revisions where an old saved internal location no longer maps exactly; load old state in a fresh candidate of new content, record warnings/errors and next text/choice identities, and compare with an explicit intended narrative continuation. **Do not predeclare that a particular edit must yield approximate recovery**: that trigger must be established by actual runtime and source path. A clean load may still be semantically wrong if paths remain valid but meaning changes. Keep old and new compiled-content hashes separate from save-format version.

This adds NARR-specific acceptance (intended next dialogue/choice, warning classification, author-approved migration) rather than another host-transaction model. Source-only worthwhile work is tracing precisely which saved pointer fields use strict resolution versus approximate recovery and defining content-author migration review criteria. Without runtime, don't claim edited-story compatibility, callback counts or save migration success. No new article or synthetic substitute proposed now.
