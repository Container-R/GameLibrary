# Resource duplication graph witness

2026-11-01 UTC. Actual author run and independently reviewed repeat passed the frozen three-mode graph contract. Accepted protocol `PROTOCOL.md` SHA256 `748ab0748d80145721fa8ca3095b0264bf393b47d3062da424fe60f5605a5d0c`; final eleven-file manifest `SOURCE-SHA256.json` SHA256 `c105634a0748ccd16589138bc94e5a292e80e4ff7f822cdb32f16f8160d60ddf`.

## Observed graph behavior

Original inputs: scripted Resource A with exported untyped Array[B,B,C]; embedded Gradient B and external Gradient C. Each process loads/holds original references, duplicates A, then appends137, edits copied B to blue and copied C to magenta. Four immutable value snapshots separate copy from each mutation. Setup verifies original paths/built-in classification, native class versus attached script, untyped Array and actual STORAGE/no-override flags before copying or mutation.

| Method | Array shared with original | B shared with original | C shared with original | Two B entries inside copy |
|---|---|---|---|---|
| `duplicate(false)` | yes | yes | yes | same Resource |
| `duplicate(true)` | no | no | yes | same cloned Resource |
| `duplicate_deep(ALL)` | no | no | no | same cloned Resource |

Every copied root differs from A. The second cached load and cached root remain A; shared script identity is expected and outside mutable payload. Appending changes original length only for shallow; B editing changes original only for shallow; C editing changes original for shallow/internal. White endpoints, offsets, point counts and held identities remain consistent. Copies were not required to preserve resource paths.

## Actual executions and independent evidence

- Author invocation `db16c3a8-a67e-48ce-9e63-ab2b6706e777`: one version query plus three fresh behavior processes; runner exit0. Separate read-only consumer exit0. Raw outer commands/streams/exits are `native-author.*` and `native-consumer.*`; full evidence is under `evidence/`.
- Independent invocation `0ab51875-74f4-4335-8af7-7e0cdbdf9ab9`: exact copied sources, one version query plus three fresh behavior processes, all exit0. See [independent repeat](review/independent-repeat/) and [native review](review/NATIVE-REVIEW.md).
- The [independent literal checker](review/independent-oracle/) was frozen before author native execution and imports neither author oracle nor consumer. It accepted both receipts against its separately frozen expected identity/value table.

Totals: **two version queries and six behavior processes**, repeating **three unique modes**, not six distinct scenarios. Each mode has four snapshots. No native retries or extra capability/parse/import probes. Static Python inspections are not native cases. Each behavior process was bounded to20seconds, version query10seconds; no broad timeout/kill failure injection was performed.

Author normal and optimized pure suites each passed six unittest methods. Reviewer separately repeated the final six-method suites in normal and optimized modes; these are synthetic consumer/guard checks, not additional engine coverage. Earlier five-method output is historical, not the final suite count. Author pure logs/interpreter identity are `pure-tests*`; independent records are in review material.

## Corrected pre-native consumer defect

Independent review reproduced false acceptance when parsed numeric0 became False while raw output stayed unchanged and the parsed-file hash was updated: Python equality coerced the values. Initial eleven-file sources/manifest and pure outputs remain in `history/pre-typed-json-binding`. The final consumer uses recursive exact-type JSON structural equality for raw/parsed and derived-oracle binding. Focused regressions reject parsed0→False and derivedTrue→1. This is a real corrected evidence-consumer defect, **not a failed Godot process**; expectations and native inputs were not adjusted after results. The prospective README is preserved as `history/README-before-native.md`.

## Safe reproduction and read-only inspection

Do not execute the historical archive in place: the runner intentionally clears the top-level success summary and creates a new invocation. Copy the eleven files named in `SOURCE-SHA256.json` plus that manifest to a separate writable directory first, keeping originals and review evidence untouched. With the same installed binary and approved local execution scope, run inside the new copy:

    python -B test_pure.py
    python -B -O test_pure.py
    python -B run.py
    python -B consumer.py .

The runner rejects optimized mode before native entry. Synthetic tests include two Python-only early-rejection subprocesses for optimized mode and missing isolation helper; neither reaches Godot. Source/protocol/helper pins and binary identity must match before native launch; do not edit the expected hash to accommodate an unknown executable.

For read-only checking of an existing complete archive, `python -B consumer.py <archive-root>` consumes its summary and raw evidence without launching the engine. Portable checking binds historical command paths lexically and uses locally archived inputs, not inaccessible original directories. It verifies UUID, PID/mode/argv, exact raw/parsed association, source/input hashes, binary-before/after records and the prospective value/identity oracle. Record consistency is not execution attestation.

The unchanged helper `isolation.py` SHA256 `bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970` controls HOME/XDG_CACHE_HOME/XDG_CONFIG_HOME/XDG_DATA_HOME/TMPDIR beneath each invocation. Engine working directories are fresh per-mode input copies, never source originals. Environment/cache/pycache directories are incidental and need not be published; retain copied project inputs and raw records.

## Provenance and limits

Both invocations used installed binary SHA256 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`, self-reporting4.6.3.stable.official.7d41c59c4. The full Engine dictionary hash was already observed before this unit; e.g. `godot-navigation-completion/review/native-repeat/evidence/20597db7-f5c8-49d4-95eb-c4f80d1d781e/behavior.json`, SHA256 `debed028a230432d21553c7a4524fdafb8764967b484b2312cc305843595d5ff`, records `7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3`. These observations do not authenticate an official release or correspondence to public comparison source35e80b3a. Independent repeat uses the same local binary/platform, not a second implementation.

The result covers this acyclic Array[B,B,C] graph,0/1 Gradient color components and sentinel137. It does not establish GPU appearance, signal delivery, memory cost, lifecycle/eviction, threading, arbitrary graphs, custom duplication flags, constructor failure, scene instantiation, save persistence or universal isolation. Internal path classification and resource_local_to_scene remain distinct. Existing ResourceLoader/cache-token experiments are separate evidence, not duplicated claims here.
