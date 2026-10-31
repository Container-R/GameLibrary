# Future native runner environment isolation: bounded source gate

2026-10-31, read-only inspection of `gamelibrary-publish-physics-callback` plus exact recent author runner snapshots. No helper implemented, no tests or engines run, no historical files changed.

## Verified current capability, not remembered coverage

`script/evidence` is not the path; the existing tools are **`scripts/evidence/fresh/`**:

- `harness.py` SHA256 `ab74e41ecf123c6a5ae1b60728d55ca06a4feb7f367d4f0bfcfdfab0257a5eb0`.
- `registry.json` SHA256 `bb063ecaf012b00cf16338fe21f043313624a8bf8d57931cd26c26376ace0aee`.
- `test_harness.py` SHA256 `d1bb660fdda8450510a5c1e5791fc4cc7cceb279f2f45f34c33caf451bb78d84`.

Read actual invoke/validate_summary/consumer code, registry, test methods and integration audit. Registry has six pinned legacy fixtures; **normal_enabled is true only for godot-focus-boundary**. validate_summary also explicitly requires that fixture and checks gate/naive/guarded raw/parsed association. Fixed-step, pause-input, import-boundary, navigation-sync and animation-events remain registered for the checked optimized-child rejection path, not five working normal adapters. Neither new root-motion nor physics callback fixture is registered. Fifteen existing unit methods concentrate on freshness, process outcome, artifact/source/path identity and timeout; they are not a dedicated environment-key completeness contract suite.

The current harness already creates and sets **HOME, XDG_CACHE_HOME, XDG_CONFIG_HOME, XDG_DATA_HOME, TMPDIR** under each invocation, and preserves PATH resolution to the measured engine. It should not be rewritten merely to share a helper: its identity is part of existing receipt trust, and a source edit would require versioned consumer/registry migration. Its process-group cleanup and artifact-consumer features are separate from environment construction.

## Exact recent duplication and failure evidence

- `research-drafts/root-motion-native/run.py` SHA `d3efc79c6961abfe0d4ff591a30a84a97921a900f77d815909824ebd76d3f7e4`, lines 67–75: own temporary workspace; explicitly creates one directory for each of the five keys, then passes the copied environment to every version/behavior child.
- `research-drafts/physics-callback-native-v2/run.py` SHA `2b00a96795564d2dc067928ceaa2f3c541ecc699873c80d9f9ae2d54a54f4803`, lines 67–75: sets all five keys, HOME/TMPDIR at workspace and XDG paths under it; unlike the root-motion loop, does not explicitly mkdir each XDG child itself.
- Preserved `physics-callback-native/initial-startup-failure/run.py`, SHA `910304159f5240a9307eb4739735a848430a9e117de8cbaaad1622cc337045da`, only sets HOME/cache/config, inheriting or omitting data/tmp values. UUID `fb43cbe6-ccbd-4507-9e2f-a3d61e2da016` retains actual directory-related error output and process returncode -6 (crash text mentions signal 11). This is evidence of the encountered bad setup, **not** proof a five-variable helper universally prevents crashes or that it diagnoses later no-entry v1 behavior.

## Proposed minimal additive change (future runners only)

A new stdlib module, provisionally `scripts/evidence/isolation.py`, with only two functions:

1. `prepare_environment(base_env, owned_root)` — caller supplies its freshly created, exclusively owned temporary root. Create five named subdirectories with fail-closed `mkdir(exist_ok=False)`, return a **copy** of base_env overriding the five fixed keys to their absolute paths. Preserve unrelated keys such as PATH; do not log the whole parent environment or credentials. Return separately an allowlisted five-key manifest for receipts. Caller retains temp-directory lifetime and cleanup ownership.
2. `validate_environment(env, owned_root)` — immediately before a future runner launches a child, require all five exact expected values, existing real directories and containment in that root, rejecting missing keys, redirected values, missing directories and symlink components. No arbitrary path whitelist expansion. It does not allocate processes, kill descendants, parse engine output, choose a binary or certify a fixture adapter.

New runners use prepare once and validate at each version/help/behavior spawn boundary. This is a narrow precondition, not an automatic guarantee that every future caller uses it. Do not monkeypatch subprocess, rewrite frozen runners or claim existing harness positives transfer to a new module. If a caller deliberately mutates environment after validation or a hostile actor races filesystem replacement, this helper is not a security sandbox.

Keep Godot-specific suppression flags and executable/PATH identity logic in caller, not in the generic helper. Explicitly describe this as isolation of **five selected writable runtime locations**, not complete OS/environment isolation: loader variables, display variables, XDG_RUNTIME_DIR, engine caches outside these paths, current working directory and privileges are not controlled. Do not silently invent XDG_RUNTIME_DIR semantics in this unit.

## Finite proposed acceptance (unexecuted)

Use only fresh disposable directories and stdlib tests; no Godot required:

| Check | Exact expected observation |
|---|---|
| Construct from deliberately hostile inherited five values | Returned five paths are exact fresh subdirectories, all exist; input dictionary remains unchanged; unrelated sentinel/PATH preserved |
| Two separately owned roots | Disjoint five paths; no cross-run path reuse |
| One synthetic Python child, explicit env | Child reports only five selected values and writes one unique sentinel under each; parent confirms expected location/content. Do not enumerate entire environment |
| Remove each required key, five finite cases | validate rejects before any child; no fallback to inherited/home defaults |
| Redirect each key to another existing directory, five cases | Reject despite directory existence |
| Delete one created directory; replace one with symlink in separate cases | Reject missing or redirected path; do not follow or modify outside sentinel |
| Reuse root with preexisting reserved directory | Prepare refuses; no merge with possible stale cache |
| Normal and optimized Python | Same finite acceptance because checks use explicit exceptions, not assert-only production guards |

One synthetic child per normal/optimized suite is enough; all rejection checks can remain pure function/filesystem tests with a launch sentinel proving no subprocess call where applicable. A frozen test protocol and source/results receipt should identify helper/test hashes and separate synthetic executions from engine behavior. No performance or crash-resilience measurement.

## Decision and stopping condition

Recommend this additive helper **only after approval**, with the above finite contract suite. Stop when the helper handles these exact omissions/redirects and two synthetic environment observations pass; do not expand to a common runner framework or migrate old receipts. Existing harness stays byte-identical. Adoption is initially a documented requirement for the next genuinely new runner; no claim of retroactive native fixture coverage. Future integration into the legacy freshness wrapper is a separate versioned migration proposal, not part of this unit.
