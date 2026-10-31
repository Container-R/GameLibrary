# Main pre-authoring source review

2026-10-31 22:14–22:15 UTC. Canonical baseline receipt `0ca989cc2910dcd0eaefd0e9ca8993958a55675c`; exact six existing role IDs confirmed from discovery gate and current role files. New candidate role ID ROLE-ENGINE-001 reserved locally, not yet published.

Directly read all four discovery sources: Cygames HRMOS 1793262169510682626 (duties lines9–37), Bandai Namco 050_0050_sa010_0500_0082 (lines12–28), Riot REQ-0010111 (introduction/responsibilities lines10–22), Cygames 2020-10-08 blog3442 Q&A (thumbnail lines40–44). Cygames role itself links blog3442. No employer publication dates inferred from crawl times; blog date explicit. No interview, video/slides or employer implementation validation.

Main inference: CI output can feed a subsequent tracked input, but the thumbnail example does not prove those files ship in a game package, trigger a particular rebuild or cause a historical defect. Source revision, candidate bytes, actual test target and destination configuration are distinct objects. Original worksheet must bind their scope and organizational decision owners without claiming vendor adoption.

Additional primary technical reference read:
- https://slsa.dev/spec/v1.2/build-provenance — Approved specification, Model/BuildDefinition/Builder/BuildMetadata. `subject` identifies output artifacts; `buildDefinition` and `runDetails` separate recipe from invocation. `resolvedDependencies` completeness is best effort, including at Build L3. This is not an instruction to list secrets or all environment variables.
- https://slsa.dev/spec/v1.2/verifying-artifacts — Approved verification guidance, steps1–2. Artifact digest matching is separate from signed-envelope verification against configured signer-builder trust and expected parameters. A self-recorded hash is not provenance authentication or a SLSA level claim.

These specification concepts may inform the original handoff worksheet; they are not evidence that any sampled employer implements SLSA, that the knowledge library meets it, or that provenance alone gives QA acceptance/deployment permission. No signing tool, production pipeline or runtime executed in this unit.
