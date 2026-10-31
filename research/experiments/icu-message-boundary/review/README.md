# Independent finite ICU MessageFormat review

2026-10-31 15:37 UTC. Local-only. Copied frozen case.py/run.py to fixture/; ran `python3 research-drafts/deep-qa/icu-message-boundary/fixture/run.py`. Four fresh subprocess cases passed. No installation, main-tree modification, account action or remote write.

Independent raw oracle command:
`python3 research-drafts/deep-qa/icu-message-boundary/check_raw.py research-drafts/deep-qa/icu-message-boundary/fixture/results`
It checks raw stdout JSON rather than trusting author summary; expected strings, numeric inputs, explicit double type, code-unit lengths, capacity, open status and preserved warnings all pass. Output independent-output.json retains full diagnostics and all three resolved library file paths/hashes; source/binary identity also in fixture/results/summary.json.

Observed: naive global accent transformation fails parsing65799 U_PATTERN_SYNTAX_ERROR while returning a nonnull handle; no format call follows. Valid patterns parse0; n1 formatting returns-127 U_USING_DEFAULT_WARNING and n2 returns0. Baseline One key/Many keys; manual literal-only Óné kéy/Mány kéys; intentional branch-text swap Many keys/One key. Library files/version match across four processes. Parser success does not certify branch-text semantics. No warning-cause diagnosis asserted.

Reviewed code: one fixed positional argument0, one c_double vararg, Linux x86_64/type/layout guards, UTF-16 uint16 arrays, explicit status gating, bounded output before decode, finally close including failed-open nonnull handle. Pattern whitelist prevents arbitrary vararg signature selection. These are four finite probes, not a general FFI interface or pseudolocalization algorithm.

Independently fetched official commit8eca245c7484ac6cc179e3e5f7c1ea7680810f39 files using GitHub plugin:
- icu4c/source/i18n/unicode/umsg.h open/format signatures;
- icu4c/source/common/unicode/parseerr.h context length16 and int32/UTF16 layout;
- icu4c/source/i18n/umsg.cpp lines426–428 kDouble reads double vararg;
- icu4c/source/i18n/msgfmt.cpp lines1662–1666 plural maps kDouble.
Base URL https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/ . This source comparison does not authenticate installed package build provenance. Current web documentation79 not used as76 runtime proof.

Frozen copied source hashes:
- case.py6305b982792337ccab59e0ae23237d2b834683408090e20365840bfa75702e45
- run.py09d317dbfaf41a0411c6d082221c03fa9ef96a760a86e7e5c7d6722ab3e3176c

No material issue found within declared en,n1/2,four-pattern scope. No Unity, RTL, layout, actual LQA, real player or general plural correctness claim. Literal-only control explicitly handcrafted. README adequately separates parse validity, binding/example output and semantic review. Local integration-ready only; publication gate remains separate.

## Read-only integration review — 2026-10-31 15:45 UTC

Read staged solutions/localization/pseudo-localization-contract.md and fixture README/review layout. Frozen case.py/run.py hashes unchanged. No additional runtime execution in this review.

New failed-open source comparison verified directly against previously independently fetched immutable umsg.cpp: lines251–259 construct MessageFormat, handle allocation failure separately, and return retVal without converting a construction parse-error status into null. Thus “can return nonnull after parse failure” is supported; not every open error does so (earlier bad arguments return null). Staged wording preserves this distinction and does not claim binary-source authentication.

Dependency caveat accurately limits hashes to inspected file paths, explicit icuuc/icui18n loads versus unverified actual dependency/data closure. Integrator’s later unset environment-variable observation is clearly not historical process evidence and does not explain warning-127. Article keeps four author+four reviewer processes distinct from saved-log revalidation; handmade literal control and swapped semantic negative remain finite, with no Unity/RTL/LQA or full acceptance-matrix upgrade.

No material gap found in added wording. The reported95 archive checks/9 tests were not rerun by this review; they are integration reports, not added ICU executions. Public-audience hold unchanged; no main edits or remote writes.

## Runner v2 independent rerun — 2026-10-31 15:47 UTC

Preserved original review fixture and raw results under historical-runner-v1/; original independent-output.json remains v1 evidence. Fresh fixture copy uses unchanged case.py6305b982… and run.py `3798aae09d1db0402116ed90b083d39d90b5783c548a6cce05068e14a9bf5eac`. Four actual ICU subprocesses rerun successfully; reused independent raw checker passes and saves independent-v2-output.json. This is a new four-case repeat, not merely log checking.

Read updated runner: old summary removal now precedes optimization refusal; timeout handler saves partial stdout/stderr (bytes decoded with replacement if necessary), timeout marker and command metadata with null returncode. No false child exit code or PASS generated on timeout.

Copied negative harness and its frozen inputs-v2 into negative/ and ran `python3 research-drafts/deep-qa/icu-message-boundary/negative/check.py`. Six synthetic negative cases rejected: optimized invocation, child nonzero, malformed payload, multiple payloads, wrong expected output, deliberate timeout. Each exits1 and removes preseeded stale PASS. Optimized case has no child execution marker and reports Refusing -O. Other injected children execute; timeout stdout/stderr markers and metadata independently reread and retained with timed_out=true, timeout_seconds0.05, returncode=null. Negative output at negative-output.json; full per-case raw logs under negative/results/.

Timeout is a modified runner copy (20→0.05 seconds) with a sleeping synthetic Python child, not an ICU timeout observation or universal process cancellation guarantee. All other negative copies match final runner hash. Source/case unchanged after harness checks; no main-tree edits or remote writes. No material issue remaining in these bounded fixes.

15:47 UTC harness addendum: integrator identified harness-level stale observations.json retention. Updated copied check.py to SHA256942739f4c812c9645d6750841152f9beed447d4540dc75260ec9888134156378; inspected cleanup now removes observations.json before checks and writes completion only after all six. Repeated all six synthetic negatives, all rejected as expected; final output negative-final-output.json. Earlier negative-output.json retained as historical run. ICU runner unchanged, so no additional ICU execution for this harness-only correction. Per-case leftovers are not full-check completion proof; no generic atomic receipt guarantee.

Archived layout: `python3 check_raw.py results` from this review directory. Historical command paths document actual executions, not checkout prerequisites. See the fixture README for library dependency identity limits.
Archived negative harness is named `runner-negative/` here (original review workspace used `negative/`); its output files retain historical command paths. Run only in a disposable copy if reproducing, so saved evidence is not overwritten.

Public selection note: original v1 review-output descriptions above are historical. This public archive retains v1 source/summary, current v2 raw outputs and independent-v2-output.json; redundant v1 raw copies and the earlier negative-output.json are omitted. negative-final-output.json and current negative raw results are retained. Generated per-case source copies can be recreated by the frozen harness.
