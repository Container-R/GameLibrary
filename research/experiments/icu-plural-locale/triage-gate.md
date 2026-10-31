# Bounded next-depth gate: plural branch coverage is locale-dependent

Status: triage proposal only, 2026-10-31 22:56 UTC. No implementation or native invocation authorized by this note. Exact inspected baseline and current library identities are in `identity.json`.

## One selected existing gap

Strengthen `SOL-LOC-001`, `solutions/localization/pseudo-localization-contract.md`, rather than create a new article. Its acceptance table already says that testing 0/1/2 is not a complete set for every language; final limitations explicitly exclude other locales and plural categories. Current actual fixture is four patterns, locale=en only, numbers 1.0/2.0, one positional double. The checked `case.py` confirms this rather than merely relying on metadata. Current evidence demonstrates syntax corruption and deliberately swapped prose, but **does not demonstrate a syntactically valid translation pattern silently falling through because a locale-relevant category was omitted**.

Proposed question: can a pattern that passes English one/other smoke tests omit a category needed by a second locale, remain parsable, and select the fallback text for a declared target input? This is a production handoff failure between localization branch coverage and format acceptance, not a new toy engine or translation-quality verdict.

## Selection rationale and rejected distractions

Read CATALOG and exact LOC article/fixture, plus MUSIC article, SFX verification metadata and DATA verification metadata. Music explicitly excludes encoded padding and resampling, but those add separate codec/timeline contracts and more complex interpretation. SFX lacks real middleware, not something another fake-port schedule fixes. DATA remains deliberate synthetic metric evidence; additional permutations alone would not close external ingestion behavior. LOC has an installed actual formatter and a specifically documented untested branch-coverage boundary, so it offers a smaller meaningful next step without another Godot variant or installation.

## Read-only capability check actually performed

Read/hash only three existing `/lib/x86_64-linux-gnu/libicu{uc,i18n,data}.so.76` paths, all resolve to `.76.1`; exact SHA256 in `identity.json`. No CDLL, symbol call, version call, formatter call or subprocess fixture execution was performed. This confirms accessible bytes, not ABI readiness, data closure, current runtime version or official-build authentication. The prior finite C ABI source discussion is reusable only after rereading its exact pinned definitions; never import legacy `case.py` as it executes at module top level.

## Required source gate before any code

1. Reopen original ICU `8eca245c7484ac6cc179e3e5f7c1ea7680810f39` definitions for the existing single-double `umsg_open`/`umsg_format`/`umsg_close` path. Do not expand varargs types, multiple arguments or arbitrary user patterns.
2. Read pinned original ICU/Unicode plural-rule data or matching official CLDR release data for English and Arabic cardinal rules. Record exact file/section and relation to ICU 76.1; a current rolling CLDR chart is not automatically the installed data identity. Arabic is a candidate because six named cardinal categories make the missing-branch risk visible; **this triage has not independently verified the rule table, so expected outputs must not yet be treated as frozen**.
3. Verify original MessageFormat semantics for omitted category falling back to `other`, and category selection with a `double`. Use small exactly representable nonnegative integers only; exclude visible trailing-zero/fraction operands, ordinal rules and offset/explicit `=n` precedence. If source cannot support these narrow semantics, stop at source findings rather than infer them from observed outputs.

## Proposed finite contract, pending source acceptance

After the above source gate, freeze a literal table BEFORE code/calls. Candidate vectors: 0, 1, 2, 3, 11, 100. Candidate three configurations in separate processes:

- English plus a full named-category pattern whose bodies are ASCII category markers.
- Arabic plus the same pattern, so the only configuration change is locale.
- Arabic with exactly the `few` arm omitted, retaining `other`; all other text unchanged.

Use original ASCII markers, not Arabic translations. Independently derive each expected selected marker from the verified rule definitions, then separately require the deliberately omitted-arm case to expose the target acceptance mismatch while remaining syntactically valid. Calling its output a semantic-contract rejection does not mean ICU malfunctioned. Do not accept any unexpected native result by rewriting the oracle; retain failure and stop.

Three configurations and six inputs would be 18 formatting requests, not 18 languages or full localization coverage. No additional locales, random inputs, nesting, rendered text or corpus processing. A separate fixed parse/open per configuration, explicit status/length gates and closing every nonnull handle preserve the existing ABI boundary. Preserve warning codes rather than treating negative warning as failure or suppressing it. Do not assume the previous -127 warning repeats or explain its cause without evidence.

## Evidence and stopping point

If main accepts the source gate, prepare a new versioned fixture without editing any prior source/results. Require source/protocol/library identity, invocation IDs, literal locale/pattern/number/output/status logs, exact process and call counts, bounded unique outputs and failure receipts. Use the already reviewed five-location environment helper, with explicit selected environment metadata; this is not a sandbox or dependency-authentication guarantee. Independent reviewer should enumerate expected branch membership from the source table without importing the author selector, inspect raw actual outputs, and run only the specifically approved repeat.

Stop after the frozen finite set or first unexpected failure. No Unity/SmartFormat/FMOD/engine invocation, font/RTL/layout evidence, actual translation approval, player study or complete language support claim. The desired deliverable is a small supplement to the existing LOC article: **parser success and English smoke coverage are not enough to approve target-locale branch coverage**, with actual formatter evidence and a maintainable locale-specific test-vector handoff. If this candidate is judged too incremental, retain this gate as a documented option rather than manufacture a coverage claim.
