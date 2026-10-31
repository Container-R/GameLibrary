# Independent reading-route QA

2026-10-31. Local-only review; no main-tree or remote edits. Read discoverability audit, registry, generator, tests, README and rendered route intent. Four curated routes preserve document IDs/status; three explicit role profiles are not inferred from relation tags; problem route disclaims universal shared algorithm. No user navigation benefit asserted.

Initial generator9767b949…: author10 tests and real --check passed. Independent five cases also passed: external symlink rejected, duplicate JSON key rejected, problem route cannot carry profile, punctuation path URL encoding, mismatch --check preserves bytes/mtime. Reviewer suite inherits author tests;15 means10+5, not15 new tests.

Found and reported bounded parser defects: comment-only/tab-comment title, unquoted colon delimiter and null accepted as literal text; quoted required key ignored even beside duplicate ordinary title. Author fixed and documented conservative scalar handling. Final-copy run at819ae411… passed11 author+5 reviewer tests; direct scalar repro rejects all five cases. Real preview --check matches. A final same-family whitespace-before-colon required key variant was requested for rejection; pending author freeze.

Files: adversarial.py contains five independent cases; probe_scalars.py records original/fixed rejection behavior; raw outputs retained. Original runs used an isolated source copy; portable final scripts now take an explicit source directory and no implementation copy is archived. Only test temporary directories and reviewer draft outputs were written. Current real verification uses --check, not generation.

## Final disposition 15:09 UTC

Author closed unsupported top-level key family by requiring simple lowercase key syntax on nonempty noncomment top-level lines. Reread code, copied frozen final and reran16 tests (11 author +5 independent), all passed; real --check matches. Final generator SHA256 `5dc8de823f44f0c9d3b5ac49dbd28422701d7948586532a607ea859260e51efd`. Earlier required-key blind spots resolved; supported scalar subset remains intentionally conservative, not full YAML validation. No remaining material blocker within declared scope. Ready for local integration; no publication authorization implied.


## Portable archive rerun — 15:10 UTC

Both reviewer scripts now require the navigation source directory argument. Imports and spawned CLI commands resolve from that argument, not an absent adjacent source tree. Removed obsolete isolated implementation copies from reviewer directory; earlier raw outputs remain historical. Commands run from workspace root (all returned exit0):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 research-drafts/deep-qa/reading-routes/adversarial.py research-drafts/reading-routes/scripts/navigation
PYTHONDONTWRITEBYTECODE=1 python3 research-drafts/deep-qa/reading-routes/probe_scalars.py research-drafts/reading-routes/scripts/navigation
PYTHONDONTWRITEBYTECODE=1 python3 research-drafts/reading-routes/scripts/navigation/build_routes.py gamelibrary-work --registry research-drafts/reading-routes/taxonomy/reading-routes.json --output research-drafts/reading-routes/DISCOVERY.md --check
```

Results retained in portable-adversarial-output.txt (16 passed:11 inherited author methods +5 added reviewer methods), portable-scalar-output.jsonl (five probes rejected), portable-check-output.txt (navigation matches). After archive relocation pass the actual scripts/navigation directory; do not recreate implementation copies. Source hash remains final5dc8de823f44f0c9d3b5ac49dbd28422701d7948586532a607ea859260e51efd.

## Repository-path integration check

The integrator preserved the final generator bytes and reran the 11 author tests, the 16-method inherited reviewer suite (11 + 5), the five scalar probes and the real navigation `--check` against the staged repository. Historical commands above refer to author/reviewer workspaces. From a repository checkout, use:

```sh
python3 scripts/navigation/test_routes.py
python3 research/audits/reading-routes/adversarial.py scripts/navigation
python3 research/audits/reading-routes/probe_scalars.py scripts/navigation
python3 scripts/navigation/build_routes.py . --registry taxonomy/reading-routes.json --output DISCOVERY.md --check
```

No user navigation study or remote publication is implied by these checks. The README integration edits replace draft-only path instructions; generator, registry and navigation preview remain the reviewed bytes.

## Subsequent curated-data extension — 2026-10-31 15:35 UTC

The new QA responsibility profile was added explicitly as a fifth route, with PROD, ENGINE and A11Y targets. Registry and preview bytes therefore differ from the original four-route review snapshot; the generator code is unchanged. A separate [QA integration review](../game-qa-role-review.md) checked the subject, target IDs/status and rationale, and the current `--check` matched. No role aliases or user-navigation effectiveness are inferred.

## Public archive selection

The initial scalar failure evidence and portable final suite/probe outputs are retained; redundant intermediate test-output copies are omitted. The level-design profile later adds the sixth route, reviewed separately in [level-design integration](../level-designer-role/integration-review.md). The generator is unchanged; earlier four/five-route observations remain dated history, not the current route count.
