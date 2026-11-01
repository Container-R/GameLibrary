# Resource sharing gate — deep copy is a policy, not universal isolation

2026-11-01 UTC. **Meaningful new depth exists, but not in repeating two cached loads.** Source-only discovery and proposed fixture; no Godot process, code, import, user assets or repository edits. Exact existing coverage metadata/hashes: `coverage-metadata.json`.

## Existing coverage inspected

SOL-ENGINE-001 `solutions/engine/asset-import-intent-contract.md` already covers import intent/sidecar semantic differences. Its native `godot-resource-candidate` supplement compares threaded IGNORE versus IGNORE_DEEP: different roots can still share a mutable external Gradient. `godot-resource-broker` addresses same-path in-flight request reuse and conflicting requested cache modes. Read their README contracts/results and article metadata. Repeating “new root does not imply isolated dependencies” alone would add little.

**Selected gap:** copying an already loaded mutable object graph with `Resource.duplicate(false)`, `duplicate(true)` or `duplicate_deep(ALL)` is a different decision from loading with cache modes. Need discriminate container sharing, internal versus external Resource sharing, and repeated references remaining aliases *within* the copied graph. No current inspected experiment measures this duplication API boundary.

Engineering question: when a designer duplicates a loaded configuration before modifying one nested value, which other consumers are still observing that mutation? Copying the root or array does not answer this for its Resource elements.

## Sources actually read

Access2026-11-01. Official versioned API reference is4.6, not necessarily the installed binary's source.

1. https://docs.godotengine.org/en/4.6/classes/class_resource.html
   Description (cache/refcount), DeepDuplicateMode, `duplicate`, `duplicate_deep`, `resource_local_to_scene`. Locators rendered lines10–14,64–75,80–88,159–176. Compact support: shallow duplication shares nested containers/resources; deep duplication copies containers and defaults to internal resource scope. Repeated references to a duplicated resource remain aliases to one copied resource. Storage/property flags and required constructor arguments affect copying. Scene-local instantiation is a separate mechanism, not a synonym for built-in/internal path classification.
2. https://docs.godotengine.org/en/4.6/classes/class_resourceloader.html
   CacheMode and load/get_cached_ref descriptions, lines58–75,96–100. REUSE can return existing resource identity; IGNORE versus IGNORE_DEEP differs for dependencies. Existing published experiment already covers that distinction; no new cache-performance claim planned.
3. Pinned public comparison source commit **35e80b3a8822a9df9be390814b62f44c0a9c69e8**:
   - https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource.cpp
   - Actual readable raw endpoint: https://raw.githubusercontent.com/godotengine/godot/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource.cpp
   - `_duplicate_recursive` source lines253–347: shallow-container return, flags/mode selection, script exclusion, remap lookup, Array/Dictionary traversal. `_duplicate`349–399: create/register copy, assign script, copy STORAGE properties. `duplicate`479–496 selects INTERNAL; `duplicate_deep`499–518 selects supplied mode. Binding701–707 distinguishes public modes. Web extraction lines are zero-based, so these source-line locators are shifted by1 from displayed web L indices.
   - https://raw.githubusercontent.com/godotengine/godot/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource_loader.cpp , source498–518 load path and567–576 cached REUSE return. Read directly; this is corroboration, not new threaded behavior research.

Pinned source is a semantic reference only. Existing installed program self-reports4.6.3.stable.official.7d41c59c4; correspondence to an authenticated official release or this commit remains unverified. No new binary observation this gate.

## Important exact semantic distinctions

- `duplicate(true)` is not “copy every external Resource.” It selects internal-resource duplication, alongside container recursion. `DEEP_DUPLICATE_ALL` broadens that scope, but property usage exceptions and script handling prevent claiming every reachable object is universally independent.
- Internal/local subresource path in the duplication mode is not `resource_local_to_scene=true`. Do not test a scene instance and silently substitute its behavior for direct Resource duplication.
- Copies may be isolated from the original while deliberately preserving aliasing between two properties/elements within the copy. Isolation does not mean “one new object per reference.”
- Loading reads serialized storage; duplicating copies selected current in-memory properties. It is not a disk reload or complete clone of runtime transient/custom state.
- `get_instance_id` is only a live in-process identity witness, not persistent asset identity. Holding references prevents lifetime ambiguity during comparisons. No reclamation/refcount-timing test proposed.

## Smallest proposed original fixture (not implemented)

Three fresh headless behavior processes, one duplication mode each: shallow, deep-default, deep-ALL. Avoid additional cache-mode matrix, threaded loads, scenes or imported images.

Original fixture input graph:
- `config.gd`: plain Resource subclass with one exported untyped Array `entries`, no required `_init`, setters, custom property flags, tool mode or class_name registration.
- `config.tres`: scripted root A; entries `[B, B, C]` where B is an embedded built-in Gradient subresource and C an external `external.tres` Gradient. Both Gradients have two simple declared colors. No textures or rendering.
- Script is an external implementation dependency; it is intentionally not counted as an isolated mutable payload. Never promise ALL duplicates it.

At start of each fresh process, explicit REUSE-load A twice, retaining both roots and both Gradient references. Establish actual same-root identity and the declared B alias, paths, types, contents, cache reference. This is a setup control only, not the unit's novel claim. Duplicate first A using that process's selected mode, retain result D, and record root/B/C IDs plus actual values. Test three mutations in a fixed order, recording before/after each:

1. Append a simple scalar sentinel to D.entries; observe original array size. This witnesses container sharing versus independence without relying only on equality operators.
2. Change point0 color through D.entries[0]; observe D.entries[1] and original B. Tests preserved aliasing separately from original/copy isolation.
3. Change point0 color through D.entries[2]; observe original C and a separately held external reference. Distinguishes external-resource scope.

Prospective expected table, not observed output:

| Copy mode | Root D distinct | Original array sees append | Original B sees color edit | D B aliases still share | Original C sees edit |
|---|---|---|---|---|---|
| duplicate(false) | yes | yes | yes | yes | yes |
| duplicate(true) | yes | no | no | yes | yes |
| duplicate_deep(ALL) | yes | no | no | yes | no |

Use both identity relationships and numeric color values as oracle. Snapshot immutable value data before mutations; do not retain mutable containers as purported historical snapshots. The active/cached root should keep its original ID; disk inputs must retain hashes. If an assumption fails, preserve the result and inspect actual storage flags/path classification rather than loosening acceptance.

## Protocol acceptance prerequisites and bounds

Before any future execution, freeze exact input graph, exported property metadata, mode table, mutation values, independent parser checks, timeout and provenance fields. Check API availability on the installed build and record any failure, not infer from self-reported version alone. Originals only, no installs/downloads. Separate invocation output directories and source/input/binary hashes; reject engine errors/nonzero exits, preserve first failures. Independent review should inspect both engine-side assertions and raw-value Python oracle. Do not add a UI, frame schedule sweep, rendering benchmark or imported assets to this question.

Potential failure ambiguity is narrow: custom Resource script must load without editor-generated class registration, and the input must prove B is built-in while C has an external path. If that cannot be established with original text resources, stop and report rather than converting it to a generic cache test.

No claim about save persistence, changes emitted by custom setters, memory cost, thread safety, cache eviction, cyclic containers, node ownership, C# GC, arbitrary graphs, property flag overrides, constructor failure, engine versions beyond the tested binary, GPU appearance or safe editing of all assets. Those are outside this finite graph.

## Access, license and publication limits

GitHub HTML resource.cpp returned cache miss; the exact pinned raw first-party endpoint was accessible and actually read. No denied access bypass or substitute mirror used. Source header contains MIT terms; link/limited paraphrase preferred, no full code import. Documentation paraphrase should stay compact across published article/note; this local gate need not all be published.

**Recommendation:** accept for a short duplication-policy supplement or separate focused solution, after protocol review. Do not spend another unit merely showing REUSE identity or IGNORE external sharing; those would repeat existing evidence. Source gate stops here, with no native execution.
