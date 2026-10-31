# Texture runner finite synthetic negatives

2026-10-31 18:33 UTC. Originals and main staging untouched. This harness documents defects before fixes; it is not an all-negatives-rejected result.

Executed:
```
python3 research-drafts/texture-runner-negative/check.py research-drafts/texture-block-budget research-drafts/deep-qa/texture-block-budget/check_raw.py > research-drafts/texture-runner-negative/output.txt
```
`observations.json` holds source/checker hashes and ten subprocess commands/results. Each cases/ directory is an isolated copy; stdout/stderr/receipt are preserved. The final checker invocation has checker-stdout.txt/checker-stderr.txt and its command/exit in observations. Existing case directories are refused; to repeat copy check.py alone into a fresh directory and pass explicit source/checker paths. Harness removes its completion observations before starting, records current observations only after all finite calls. It captures observations, not a universal security/robustness assertion suite.

## Findings

1. **Medium — failed imports leave stale success receipt.** Synthetic local PIL.py raises ImportError; separate replacement model.py raises RuntimeError. Both actual runner invocations exit1 with no stdout, but old results/summary.json PASS bytes remain unchanged. Cleanup is after PIL/model imports. This does not make these invocations successful when exit status is honored; consumers looking only at an existing PASS receipt could misattribute previous work. Recommendation: after minimal stdlib/bootstrap path setup, remove old completion summary and reject -O before optional PIL/model imports. No guarantee against interpreter startup failure, unwritable directory, or all filesystem faults is implied.
2. **Medium — numeric payload-offset fields are not checked by author runner.** Mutate only emitted payload_offset to offset-127 rather than offset-128. Runner returns0/new PASS despite every reported payload offset being wrong by1. Sizes, actual fixed CHAIN slices and colors remain correct. Independent checker rejects mutant because it checks numeric prefix offsets. Recommendation: author runner explicitly compare each emitted numeric offset with independent prefix sums/literal expected offsets; optionally blocks_x/blocks_y as part of declared numeric schema. This is a testing blind spot, not evidence the unmodified historical offsets were wrong: original independent check already validated them.

## Other observed negatives

- Runner -O with healthy imports removes prior PASS, exits1, no new summary.
- BC7 block size16→17 mismatch exits1 before decodes, no stale summary.
- Checker missing artifact, malformed summary, missing summary and -O each exit1 with no PASS stdout.
- Checker intentionally leaves source evidence untouched even on failure. Retained input summary in those cases is correct for a read-only validator, not a freshness bug. Any externally redirected old checker report is caller-owned; this checker doesn't manage a persistent completion file.

## Actual work counts / limits

Ten child invocations total: five runner cases, four direct checker cases, one checker against the successful off-by-one mutant. Eight expected direct rejections plus the final mutant checker rejection; one runner false acceptance. Of these, only the offset-mutant runner reaches six actual wrapped Pillow decodes; its checker then performs six additional actual decodes before rejecting the numeric offsets. Thus twelve synthetic-context CPU decode calls, not twelve new positive format cases. Other failures occur before decode. Original fourteen-case/six-decode evidence is not modified or relabeled. Warnings from the mutant runner remain captured; no GPU, API creation, BC7 decode, installation, actual dependency breakage or production failure rate is claimed.

Imports were failed by local shadow/replacement modules solely inside disposable copies. No installed dependency was edited. Finite15-second subprocess timeouts bound harness waits, not arbitrary OS cancellation guarantees. No fixes have been applied to accepted fixture in this review.
