# Frozen protocol — Resource duplication graph policy

2026-11-01 UTC. **Protocol only, not implemented or executed.** Source gate `gate.md` identifies official Godot4.6 documentation and comparison source35e80b3a8822a9df9be390814b62f44c0a9c69e8. This unit does not repeat threaded IGNORE/IGNORE_DEEP or request-broker experiments.

## Question and permitted execution envelope

For one loaded graph, distinguish container sharing, internal/external Resource copying, and preserved repeated-reference aliasing inside the copy. Three independent behavior processes, one mode each; one preceding version process: **maximum4 native processes per accepted author invocation**, no retries, import/editor/parse-only/help/capability subprocesses. Version timeout10s; behavior timeout20s each. No user assets, GPU observations, concurrent mutation, scenes, installs or network. After a failed process stop the invocation, retaining evidence. A later retry requires diagnosed cause and separately identified invocation; do not silently consume extra native processes.

Use installed `/usr/local/bin/godot`, expected observed historical SHA256 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3` and banner `4.6.3.stable.official.7d41c59c4`. Query once with `--version`; behavior records Engine version dictionary. Neither self-report nor matching bytes authenticates an official release or exact source correspondence. Fail before launch if binary hash differs; do not bless another binary automatically.

Use the existing vetted isolation helper `scripts/evidence/isolation.py` unchanged (current expected SHA256 `bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970`, verify bytes before adoption). Minimal base environment PATH=/usr/bin:/bin, LANG=C, LC_ALL=C, then helper-owned HOME, XDG_CACHE_HOME, XDG_CONFIG_HOME, XDG_DATA_HOME and TMPDIR directories under each invocation's workspace. Validate helper environment immediately before each launch. Follow existing `godot-character-motion/run.py` receipt/consumer pattern, not its physics claims. No implementation or environment setup executes at protocol stage.

## Original immutable inputs

Freeze exact bytes and source hashes before native entry:

- `project.godot`: minimal headless-compatible project, no main scene, plugins or autoloads; use compatibility renderer setting only as environment configuration, not a rendering test.
- `config.gd`: extends Resource, one `@export var entries: Array = []`; no class_name, required constructor, setters, signals, tool annotation, custom property flags or other payload.
- `external.tres`: native Gradient C, offsets[0,1], colors green `(0,1,0,1)` and white `(1,1,1,1)`.
- `config.tres`: root Resource A using explicit `res://config.gd` script reference; embedded native Gradient B, offsets[0,1], colors red `(1,0,0,1)` and white; exported entries `[B,B,C]`, C referenced explicitly as `res://external.tres`.
- `main.gd`: original SceneTree probe, direct script entry; exact mode argument from user arguments. No native-generated source files or editor registration required.
- Runner, oracle, consumer, pure tests, protocol and isolation helper. File-list manifest includes every runtime source/config input and evidence-validation source.

No runtime ResourceSaver calls or setting resource_path/take_over_path. Each mode runs in its own fresh invocation-owned copy of the frozen project inputs; source originals are never the engine working directory. Copied input hashes must equal the frozen originals before execution. Existing input content is immutable throughout behavior. Input/project/source originals and each mode's copied input bytes hash-equal before and after the invocation. Any generated incidental `.godot` data in each fresh project copy is not evidence of isolation or part of payload; no import step is allowed.

## Startup and baseline (each fresh behavior process)

Command shape: `godot --headless --path <mode_fresh_copy> --script <mode_fresh_copy/main.gd> -- <mode> <invocation_uuid>` (mode is exactly shallow, internal or all). No process-mode/time/frame scan. Probe runs finite operations then exits explicitly.

1. Record Engine version dictionary, actual mode, process ID, invocation UUID passed explicitly by runner, and initial property/mode constants. Fail if required methods/enums/types are unavailable; do not launch an extra capability process.
2. Call explicit synchronous `ResourceLoader.load('res://config.tres', '', CACHE_MODE_REUSE)` twice as A and A2; retain both live. Retain original B=A.entries[0] and C=A.entries[2], plus `ResourceLoader.get_cached_ref('res://external.tres')` as Ccache. No additional loads to fabricate isolation.
3. Establish A/A2 same ID; cached root ref same A; B=A.entries[1]; C=Ccache. Record native class and attached script separately; A has native class Resource with script path `res://config.gd`; B,C are Gradient with two points, offsets exactly[0,1] and declared colors. Initial entries length3. B path must begin `res://config.tres::`, `is_built_in()` true; C path exactly `res://external.tres`, `is_built_in()` false. Root path exactly `res://config.tres`. Record duplicate paths if useful but do not require preservation: copies may have blank paths.
4. Record actual entries property type/usage from `get_property_list`; require TYPE_ARRAY, STORAGE bit present and ALWAYS_DUPLICATE/NEVER_DUPLICATE bits absent. Record `is_typed()` false on entries. Do not infer these only from source text. All payload resource_local_to_scene flags false; no PackedScene path.

Identity checks compare simultaneously held live references. Encode `str(get_instance_id())` as canonical decimal string in raw JSON; Python validates/compares exact integers, not lossy JavaScript numbers. Require nonzero, allow signed representation. No cross-process ID comparison or persistent identity claim.

## Copy and mutations, exact order

Modes: shallow=`A.duplicate(false)`; internal=`A.duplicate(true)`; all=`A.duplicate_deep(Resource.DEEP_DUPLICATE_ALL)`. All create distinct root D. Keep A/A2/B/C/Ccache/D alive through final record. Script dependency intentionally remains shared; record script identity equality but do not classify it as isolated payload. The source's script handling is not an ALL-payload violation.

Before mutations capture stage `copied`. Then:

1. `append`: append integer137 to D.entries. Record snapshot.
2. `internal_edit`: set D.entries[0] Gradient point0 to blue `(0,0,1,1)`. Record snapshot.
3. `external_edit`: set D.entries[2] Gradient point0 to magenta `(1,0,1,1)`. Record snapshot.

Snapshots must contain newly constructed scalar/string/number arrays, immediately serialized records or equivalent immutable value copies. Never retain an Array of live Resources as the historical evidence object. No resetting originals between steps; use a fresh process for each mode.

## Prospective oracle

| Mode | D root distinct | D entries same Array as A | D B same as original B | D C same as original C |
|---|---|---|---|---|
| shallow | yes | yes | yes | yes |
| internal | yes | no | no | yes |
| all | yes | no | no | no |

In every mode D.entries[0] and[1] must be same Resource, with the same ID both before and after mutations. A/A2 remain same original root; original B and C IDs stable. D IDs stable across all four post-copy stages; any identity replacement is a failure for this fixture. D script same identity as A script (shared implementation dependency).

- copied: both graphs length3, B red/white, C green/white.
- append: D length4 and slot3 exact integer137; A/A2 length4 only shallow, otherwise3. Colors unchanged. Slot0/1/2 identities unchanged.
- internal_edit: both D B aliases blue/white. Original B and A/A2 B aliases blue/white only shallow, otherwise red/white. C remains green/white everywhere.
- external_edit: D C magenta/white. Original C/Ccache/A/A2 C magenta/white in shallow/internal, green/white in all. B colors retain preceding stage. Lengths/sentinel unchanged.
- All offsets remain[0,1], point count2, all white endpoints unchanged. Root cached ref remains A after duplication/mutations. Disk/source bytes unchanged.

Colors are exact binary-representable0/1 components; compare exact numeric values after requiring exact JSON int/float type excluding bool and finiteness. Counts/sentinel require exact int excluding bool. No tolerance is needed for these frozen values. Identity equality alone or serialized-value equality alone is insufficient; both tables must hold.

## Raw record schema and independent consumption

Each stdout consists of the recorded exact engine banner/allowed blank lines plus exactly one uniquely prefixed `RESULT_JSON:` object; reject extra result objects, trailing nonprotocol lines, parse errors, duplicate JSON keys and nonfinite constants. No broad ERROR/WARNING suppression. Require returncode0 AND empty stderr. Preserve raw stdout/stderr even on failure.

Result fields (exact schema version1):
- `schema`, `invocation_uuid`, `mode`, `process_id`, `engine_version`;
- `constants` for copy modes/type/usage bits actually used;
- `setup`: property metadata, root/B/C paths+built-in flags/local-to-scene, entries typed flag, baseline cached/root/script/reference IDs, initial numeric snapshots;
- `stages`: exactly four ordered objects named copied,append,internal_edit,external_edit. Each contains A,A2,D root IDs, cached root ID, original B/C/Ccache IDs, A and D entries lengths, first3 IDs, slot3 scalar if present, B0/B1/C colors+offsets+pointcounts for BOTH graphs, original held B/C/Ccache values, Array identity boolean, script IDs. Missing/extra/duplicate stages rejected.

Freeze actual field spelling in code before execution; schema validation checks exact keys and types, not only selected booleans. The independent Python oracle recomputes the mode-specific expected identities/values from this protocol. It must not merely trust a GDScript `passed` flag or compare summary to itself. Retain raw per-stage records and derived expectation checks.

Consumer verifies complete successful receipt, UUID/output-directory agreement, exact expected4 process records (one version then shallow/internal/all), command/mode binding, current exit statuses, matching stderr/stdout hashes, protocol/source/input/binary-before/after identities and per-mode oracle. Record script-side PID against runner child PID. Parsed artifacts, if saved, must equal reparsing rawstdout and have matching hashes. No fallback to a previous summary or another invocation's cached result.

## Freshness, failure and freeze rules

At runner startup remove any old top-level success summary BEFORE optimized-mode/argument rejection, then create a fresh UUID invocation directory with exclusive creation and RUNNING receipt. No PASS summary written until all checks and independent consumer verification succeed. Explicit checks remain active or optimized mode must reject before native; choose and test that behavior before native entry.

Each subprocess record is written ATTEMPTED before spawn; record PID after successful launch, full argv/cwd, selected environment, UTC times, timeout, return status and raw-stream hashes. Launch failure is not a successful execution. On timeout terminate only the runner-owned process group and use bounded cleanup wait; preserve partial streams and mark FAIL. Failure paths attempt source/binary-after hashes and explicitly report if unavailable. A strong-kill/unwritable-workspace cannot be turned into a guaranteed complete receipt: consumer must reject incomplete evidence.

Pure pre-native tests should reject forged ID alias/value tables, bool-as-int/nonfinite values, missing/duplicate records, mismatched UUID/source/stream hash, truncated/failed receipts and stale summaries. These tests generate original synthetic JSON only; they do not count as native resource observations. Freeze source manifest before native run and retain any first failure. Never revise expectation to fit unexplained output. Independent reviewer copies exact sources and reruns separately only after parent approval; author originals remain immutable.

## Scope and stop

Acceptance covers this acyclic three-entry graph and these methods on the recorded installed binary. No arbitrary graph clone, cyclic container, property override, required constructor, C# GC, lifecycle/eviction, threading, signals, save persistence, exported build, GPU, memory/performance or all-version guarantee. Do not conflate internal path scope with resource_local_to_scene. Copying current in-memory STORAGE values is not disk reloading or cloning all transient runtime state.

Stop after3 mode results, input/identity verification and independent review. No new role article or broad asset-cache benchmark. This protocol currently authorizes no execution until accepted by parent/reviewer.
