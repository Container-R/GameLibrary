# Five selected writable runtime directories for future runners

Additive proposal for `scripts/evidence/isolation.py`; no old runner, historical archive, registry, or fresh harness has been edited. Linux local Python 3.12.14 evidence only. `protocol.json` SHA256 `2717199e1cb4800b3e42665307657e8257e39ff90863c1e7dfd82fe18251e712` was frozen before implementation.

## API and caller responsibility

`prepare_environment(base_env, owned_root)` returns a copied environment and a separate five-key receipt manifest. Caller must supply an absolute, already-created, exclusively owned fresh temporary root and retain its lifetime until every child finishes. HOME, XDG_CACHE_HOME, XDG_CONFIG_HOME, XDG_DATA_HOME and TMPDIR map to identically named direct child directories. The helper preflights all reserved names, creates directories with exist_ok=False, and validates the mapping. Parent environment is not mutated; unrelated variables are preserved, not logged. The manifest contains only these five chosen paths.

`validate_environment(env, owned_root)` checks exact mapping, directory existence, and symlink-free root components/children. Use immediately before each future child spawn. It is not a process launcher, binary selector, output parser or fixture adapter. Callers can mutate env or paths afterward; there is no TOCTOU defense, hostile filesystem sandbox, ownership attestation or promise that all engine writes use these locations. It does not normalize away symlinks before checking. Permission failures or races during creation may leave partial children: cleanup remains caller-owned. No rollback/deletion of outside files is attempted.

PATH and loader/display variables, XDG_RUNTIME_DIR, current working directory, privileges, runtime-created paths outside these five, descendant lifecycle and full environment isolation are not covered. Godot-specific flags remain caller-owned. A new caller must actually adopt this API; merely publishing it does not prevent omissions in unrelated scripts. Existing focus-only normal harness adapters are not expanded.

## Actual finite tests

From a fresh copied directory containing isolation.py, test_isolation.py and protocol.json:

```sh
python -B test_isolation.py
python -B -O test_isolation.py
```

Both author suites exited 0: five unittest methods each, including five missing-key and five redirected-key subcases, root/reuse/symlink/missing-directory checks, dictionary-copy/disjoint-root checks, and **exactly one real synthetic Python child per suite**. Two synthetic children total; zero Godot/other engine processes. The child independently reports only the five keys and writes five distinct sentinel files; the parent verifies contents before the temporary directory is removed. Temporary sentinels are not retained artifacts. Raw stdout contains the single RESULT_JSON plus nested actual child command/stdout/stderr; unittest output is in normal.stderr/optimized.stderr. Each payload binds three source hashes and records optimization mode. No source imports author validation from another fixture. Tests use unittest assertion methods, which remain active under -O; production helper uses explicit exceptions.

No failed initial run was discarded: the first frozen implementation passed both author suites. The tests do not inject permission errors, disk exhaustion, concurrent races or child timeout. Results are finite local evidence, not crash prevention, complete sandboxing or tamper-proof execution proof. Independent review copied the same three frozen files and repeated both suites: another two synthetic children, zero engines. Four extra pure/filesystem probes per mode included an injected third-mkdir PermissionError; observed partial creation and unchanged base mapping matched the caller-owned cleanup contract. This is a synthetic injected failure, not actual disk/permission exhaustion. Review evidence is retained separately in `research-drafts/deep-qa/runner-isolation-helper/` for integration.

## Prepublication anchor-root guard amendment

Initial accepted source/results and documentation are preserved unchanged in `historical-pre-root-guard/`. Main review then requested one misuse guard: `_root` now rejects the filesystem anchor before directory creation. `/` cannot be a fresh caller-owned invocation root; this is not an ownership/security authentication mechanism. Protocol amendment records the old digest and new case explicitly; initial freeze claims refer to the original protocol, not a fabricated pre-run timestamp for this amendment.

The existing invalid-root test method now checks `/` while `Path.mkdir` is mocked to raise if called. No root write can occur even if the production guard regresses. Source change is only this guard, its negative test and the transparent protocol amendment. Final author normal/-O suites each passed five methods and launched one synthetic child: two new synthetic children, zero engines. Current result files correspond to final source hashes in SHA256SUMS. Initial independent acceptance above describes the historical source; final-source reviewer repeat passed normal/-O five methods each, exactly two additional synthetic children, with four supplementary pure/filesystem probes per mode. Combined initial and final author/reviewer suites executed eight synthetic children total, zero engines; these are not eight engine tests. Final reviewer artifacts are in the review archive’s `final/` directory, while initial reviewer artifacts remain unchanged. No historical engine fixture or harness was changed.
