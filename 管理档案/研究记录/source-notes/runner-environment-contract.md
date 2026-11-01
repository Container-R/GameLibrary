# Future runner environment contract: five selected writable locations

## Decision and exact applicability

The physics callback v1 startup attempt omitted an explicit `XDG_DATA_HOME` override and failed before producing a contact observation. Its directory diagnostics motivate a reusable setup check; they do not prove a universal crash cause or that five variables prevent crashes. The existing fresh harness already constructs these five locations. Its source, registry and focus-only normal adapter are unchanged. Publishing this helper does not migrate any historical runner.

New [isolation.py](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/scripts/evidence/isolation.py) prepares a copied environment and a five-key manifest under a caller-owned, fresh, absolute temporary directory. It validates `HOME`, `XDG_CACHE_HOME`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME` and `TMPDIR` immediately before a future caller launches a child. Missing/redirected values, missing directories, symlinks, reserved-name reuse and obvious invalid roots are rejected. Filesystem-anchor rejection is a documented prepublication amendment, not a retroactively frozen test.

This is **not a sandbox or ownership authentication**. The caller must own the root, manage its lifetime and clean up partial creation on failure. There is no atomic filesystem race defense. Other variables, working directory, privileges, descendants and arbitrary runtime writes remain outside this contract. In particular, preserving unrelated variables is deliberate; this is not full XDG or full-environment isolation.

## Primary references actually read

- [Python 3.12 pathlib documentation](https://docs.python.org/3.12/library/pathlib.html): directory creation, existence and symlink operations inform the checks. The page served documentation version 3.12.16; local execution was Python 3.12.14. This is an API-level reference, not identical-runtime source authentication.
- [Python 3.12 subprocess documentation](https://docs.python.org/3.12/library/subprocess.html): an explicit `env` mapping replaces default environment inheritance for the child. A timeout does not guarantee interruptible initial process creation. The helper itself launches no process and makes no descendant-cleanup guarantee.
- [XDG Base Directory Specification 0.8](https://specifications.freedesktop.org/basedir/0.8/), dated 2021-05-08: data, config and cache home paths are absolute and have HOME-based defaults when unset or empty. The latest endpoint timed out; the versioned endpoint was successfully read. The specification also covers locations deliberately outside this five-key helper, including state/runtime directories. No claim of full specification compliance follows.

## Finite evidence and retained amendment

[Exact author/reviewer archives](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/audits/runner-isolation/README.md) preserve initial and final sources, frozen protocol/amendment, stdout/stderr and independent review. Four source-stage/owner combinations each ran normal and optimized parent Python suites: **eight suites, five unittest methods each, eight synthetic Python children total, zero engines**. Each child reports only the five selected variables and writes five sentinel files that its parent checks before temporary-directory cleanup. The child uses `-I`; optimized parent mode does not imply an optimized child.

Four supplementary pure/filesystem scenarios were repeated by the reviewer for both source stages and parent modes: ancestor symlink, lexical parent traversal, dangling reserved symlink and injected third-mkdir failure. These are four distinct scenarios, not sixteen newly invented behaviors. Partial creation remained caller-owned; no actual disk exhaustion or OS permission failure was induced. The anchor-root negative test mocks mkdir so a regression cannot write to `/`.

The initial implementation passed its then-frozen contract. The additional anchor guard and final source identities are separately documented; no failed initial execution was hidden or relabeled. A portable read-only checker binds the eight existing result records to their exact source hashes, checks child records and verifies 1,723 historical experiment/fresh-harness files remain unchanged. It does **not** rerun children, recheck deleted sentinels, authenticate execution or establish general isolation/security guarantees.
