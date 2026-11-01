# Editorial review: omitted defaults and narrative migration

2026-11-01. Accepted unchanged as an adversarial source-only audit, not a correction of the original central claim.

Reviewed audit `research/audits/ink-default-migration/review.md` with SHA-256 `a17b661be5fa868aae96948513fd2e0418f131c0edfe4b2d822b04a03795823f`. Read its SOURCE-REVIEW and the complete original `research/source-notes/ink-save-content-compatibility.md`, SHA-256 `d164cf8b180538054873863f18e9d893f29368a5f8b31d5abaffc96c17687329`. No linked runtime or private records were opened.

Independently reopened fixed [VariablesState.cs](https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/ink-engine-runtime/VariablesState.cs#L145-L225), including default omission, restoration and the Boolean equality branch, plus default snapshot and SetGlobal at 342–378. The rest of the audit's source paths were evaluated against the separately recorded source review rather than claimed as newly reopened in this editorial pass.

The Boolean counterexample is correctly conditional on the old value/default, enabled omission, a new default and execution reaching variable restoration. It is not represented as a compiled complete story, successful full load or observed later branch. Delaying the variable's narrative use explains why a current-output check cannot cover all future-state invariants; no actual display or callback result is invented.

The direct dictionary path does not establish the proposed immediate variable-notification criticism. The audit appropriately confines that negative result and does not generalize it into a side-effect-free loader. More importantly, the original source note already requires content identity, author-approved branches and controlled host bindings. The audit acknowledges those clauses instead of fabricating an earlier assurance that matching the next screen certifies migration.

Retention, conversion and intentional reset remain project decisions. The text does not require every new version to preserve old false, infer old state from new defaults, or imply a newly disabled omission setting can repair already missing historical fields. Candidate-instance isolation and historical-default interpretation are distinct responsibilities.

The relative reference `../../source-notes/ink-save-content-compatibility.md`, resolved from the intended public `research/audits/ink-default-migration/review.md`, correctly reaches the existing source note. The original note is reviewed as evidence, not rewritten. Public prose remains neutral, contains no private execution identifiers or host-specific runtime metadata, and does not duplicate source code or a full factual summary.

No compiler, runtime, actual save, model, player data or migration execution was inspected or run. Acceptance covers the exact audit and its bounded counterexample only, not all ink serialization behavior or a complete migration algorithm. No correction requested.
