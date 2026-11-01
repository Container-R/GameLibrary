# Offline silent-stem normalization: finite fixture awaiting native authorization

This directory contains original Python implementation and numeric byte inputs for the frozen protocol. **No FFmpeg invocation, version query, media command or native result has occurred in this unit.** The selected installed-file pins come from the reviewed protocol. Guarded Python failure-finalization tests perform file-only hashing of those paths, never execute them. Native execution requires separate exact-code acceptance and authorization.

## Files and scope

- `PROTOCOL.md`: accepted prospective specification, unchanged.
- `signals.py`: literal original byte generation and author whole-waveform check.
- `consumer.py`: portable strict JSON/receipt consumer, independently restates the protocol bytes; imports neither `signals` nor the runner. It reconstructs all samples from lowercase hex and binds inputs, outputs, raw streams, recorded process metadata, selected binary/library hashes and pinned sources. Receipt integrity does not authenticate execution.
- `run.py`: only future native entrypoint. Clears old summary before local imports/optimized guard, creates a UUID receipt, checks pins, then at most one version and three mixing processes, each with its own five-key owned environment. Each child has a 20-second deadline and bounded process-group cleanup attempt. Stops on first failure, retains partial raw logs/outputs and best-effort reversible failure media archives plus post-failure source/tool identities or explicit unavailable errors, preserving the original exception. Timeout branches have not been executed.
- `isolation.py`: unchanged vetted five-key helper; not a sandbox or dynamic dependency isolation claim.
- `SOURCE-SHA256.json`: frozen six-source manifest; README and logs are not pins.
- `test_pure.py`, `pure-*`: seven synthetic unittest methods, normal and `-O`, both PASS. Synthetic version text explicitly says it is not native evidence. Initial six-method outputs and source manifest 82a94e31 are preserved in `history/pre-failure-finalization/`. The final seven-method suites add partial failure archive and unavailable-file witnesses; UTC offset/type mutations are rejected. Each suite starts two Python-only guarded-runner children (optimized and missing helper), both terminate before native entry. These are not mixing cases.

The pure tests cover fixed literal bytes, nonfinite output rejection, complete output mutation, strict bool/number distinctions, duplicate/nonfinite JSON rejection, selected hash/log/archive tampering, command/environment/count/status mutations, and stale PASS clearing before guarded startup. These finite tests do not establish arbitrary tamper resistance or process isolation.

## Future authorized execution and archival

Do not run a historical evidence archive in place. After separate authorization, copy the six pinned sources, `SOURCE-SHA256.json` and this README to a fresh writable directory, leaving historical `evidence/`, summaries and logs untouched. Run `python -B run.py` there once, preserve outer stdout/stderr/exit. If successful, a separately authorized read-only `python -B consumer.py <directory>` checks the receipt. No filter/help probe, retry or extra native process is part of this protocol. No output byte or transition criterion may be adjusted from observed results.

Full inputs and outputs are retained as reversible lowercase hex; local `.f32le` files may be omitted from a text-only archive because the consumer validates the complete reconstruction. Keep raw logs, receipt and source manifest. The consumer compares optional local binary media to the hex archive when present. It does not require the installed native tool to read archived evidence.

Three unique mixing conditions examine silent-but-present versus ended input, not audible quality, middleware lifecycle, game scheduling, perception, arbitrary signal reproducibility or the complete dynamic library closure. The installed tool's future version self-report and selected hashes do not prove official release provenance or identity with the public comparison source.
