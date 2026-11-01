# Independent Resource duplication source gate

2026-11-01 UTC. **Accept for a finite three-mode protocol, not implementation/native execution.** No engine/version invocation or fixture code was run.

## Actual coverage read

The exact current article hash `fb68adbd1a4ce1b60e061d6caa804fad0534dcf96daa2d111a42350989a723d3` and prior candidate/broker README hashes `3b010d95…` / `d2d2d4f0…` match `coverage-metadata.json`. Read their finite contracts/results and metadata. Current `verification_method` is:

> 官方来源核对；原创 SVG 导入及原生资源候选依赖隔离及同路径请求登记的实际无头对照；未验证 GPU、导出包或跨版本缓存复现

The prior observations concern loading dependencies and uncollected threaded request reuse. They do not establish `Resource.duplicate` behavior. Repeating load-cache isolation alone would not add evidence; repeated aliases plus internal/external duplication scope is a distinct question.

## Independent original-source read

[Godot 4.6 Resource](https://docs.godotengine.org/en/4.6/classes/class_resource.html): DeepDuplicateMode, duplicate, duplicate_deep, local-to-scene and is_built_in sections. The documented deep default copies containers but limits Resource scope; the repeated-reference note supports one clone reused within the copied graph. Storage flags and required initialization parameters constrain copying. Scene-instance localization is separate.

[Pinned resource.cpp](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource.cpp#L253-L399), independently read at the exact raw endpoint: shallow non-object early return; mode/usage dispatch; Script exclusion; remap lookup; recursive Array traversal; root allocation/remap insertion; script attachment and STORAGE-property copying. [Public mode entry points](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource.cpp#L479-L518) choose INTERNAL for duplicate and explicit mode for duplicate_deep. These branches support the gate's prospective table for its declared graph, not arbitrary property policies.

An attempted raw `resource.h` open returned cache miss; no unread inline body is claimed. The public documentation plus read `is_built_in()` call site suffice for the gate; actual fixture classification must be observed rather than assumed from naming. The public source remains a comparison source, not authenticated provenance for the installed binary.

## Exact protocol conditions worth freezing

1. Keep the untyped exported Array and no special setters/property flags/required initializer. Record actual STORAGE metadata before copying; reject a setup mismatch before mutation. The root's native class and attached script identity are separate fields. A script filename is not proof of a distinct native class. Gradient payloads must actually be Gradient resources.
2. Establish original B as built-in with its path/classification and C as external at `external.tres`; record `resource_local_to_scene` independently, not as the internal-mode predicate. Do not require a newly cloned resource to retain its original disk path without a separate source contract. Keep originals alive and compare identities only within each process.
3. `_duplicate` attaches the existing script via `set_script(get_script())` despite the nearby comment's “Duplicate script first” wording. The normal recursive mode path also excludes Script resources. Thus script reuse is intentional here, including ALL, and should be visible in the logged graph; do not count it as payload-isolation failure or silently claim it was cloned.
4. The source remap cache permits D.entries[0] and D.entries[1] to refer to ONE new B in deep modes. Original isolation and within-copy alias preservation are two different predicates. Three mutation steps plus immutable value snapshots discriminate array sharing, internal-resource scope and external-resource scope. Do not save live Array/Resource references as historical snapshots.
5. The proposed table is supported: shallow shares Array/B/C; true clones Array/B but shares C; ALL clones Array/B/C; duplicated B is reused at both copied entries. All roots differ from their original. These remain prospective outcomes until exact runtime execution passes; no memory-cost, thread-safety, cycles, arbitrary scripts, rendering or persistence claim follows.

No source-level blocker found. Freeze literal colors/sentinel, stage order, all held-reference identity relations, complete value snapshots and failure stops before any native attempt. Keep REUSE only as a setup control, not three new cache scenarios.
