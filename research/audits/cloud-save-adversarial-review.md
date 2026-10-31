**集成后记（2026-10-31）**：下文为未发表初稿的历史审查，两项缺陷已修复，并补充传入旧ID循环保护。初始失败输出保存在 `research/experiments/deep-model-qa/cloud-before-fix-output.txt`；同一独立检查修复后5项通过，见 `cloud-after-fix-output.txt`。生产I/O限制没有因此消失。

# Cloud save draft adversarial review

2026-10-31; read-only review of draft article and model. No sources independently verified here; no OS/Steam I/O executed. Source owner handles API review.

## Reproduced correctness gap

**High within the abstract model:** dispatch verifies only disk revision against base, whereas reload verifies full candidate equality with loaded for same revision. Without notification, replace disk `Save('a','',1)` with `Save('a','',55)` after preparing a local write. Dispatch succeeds and overwrites the corrupted/unexpected bytes; recovery evidence disappears. This contradicts the proposed same-identity/different-content stop policy in the unnotified-change case already tested elsewhere by the model. Require `disk == loaded` in this serialized immutable model, not merely `disk.rev == base`. In production this check alone is explicitly not a file-system CAS, and existing article warning must remain.

## Contract/precondition gap

**Medium, identity assumption:** after writing a→b, caller can queue revision a and dispatch a new payload. Model permits a→b→a identity reuse, violating proposed unique immutable revision identities; subsequent parent comparisons are no longer trustworthy. Reproduction is executable. Either require a supplied unique-ID allocator and state that callers must never reuse IDs (model cannot verify global unseen identities), or reject locally observed identities as partial protection and retain global uniqueness as a prerequisite. Do not imply an in-memory seen set enforces uniqueness across devices/restarts. Runtime types of constructor/edit/queue also are assumed rather than validated: bool values/blank or non-string revisions can bypass local publication but reload may reject them. A clear well-formed input precondition is sufficient for intentionally small internal model; otherwise validate consistently.

## Adversarial checks

`python3 research-drafts/deep-qa/test_cloud_adversarial.py`: 5 tests, 2 expected failures on current draft (content-only disk replacement; old revision reuse), 3 passes (dirty same-snapshot notification preserves dirty value; third revision invalidates old load during conflict; dirty deletion retains memory and does not recreate disk). Raw output adjacent. These are review evidence, not publication pass counts.

## Scope and limits assessed

- No conflict-choice commit method exists; article explicitly says player selection absent, so stale conflict UI confirmation safety is a production acceptance item, not tested success.
- Deletion keeps dirty memory but not a persistent backup; article accurately limits recovery copies to memory. No durability guarantee can be inferred.
- Notification-before-dispatch and serialized guard+assignment assumptions are stated; current model cannot validate suspension callbacks, multi-thread races or in-flight cancellation. Article correctly rejects epoch-only cancellation claims.
- Direct-parent-only acceptance conservatively conflicts when intermediate lineage missing. No false automatic fast-forward found under well-formed unique identities.
- Same snapshot with dirty local state returns ready and leaves dirty state intact; queued jobs from pre-notification epoch remain rejected.
- No additional defect found in tested stale-load, dirty-branch or deletion paths. This is a bounded review, not exhaustive proof.
