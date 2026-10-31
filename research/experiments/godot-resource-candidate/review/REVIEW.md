# Independent resource-candidate ownership review

2026-10-31. Accepted within the finite graph and installed-binary scope. Current runner SHA256 f2ef26f570b62f07e505322534f6fcc8e7bfa0d5d458a552eee04672553288bc; main.gd da1eb0a9edb0b0799c4b6fac131d8c19404123a6b8de3fe9c7c4a94a1a58e026. Frozen pre-code contract 267f450ad57c6a802346d0b9c7ac9d79e240871a64a2e6566f62e3810f6bd941 read before execution. README final 3b010d953570fcf5cbb038df32148a850e15ed2d4246021f66b738b37bafade1 accepted.

## Executed independently

From repository workspace, commands (all exit 0):

- python3 -B research-drafts/deep-qa/godot-resource-candidate/fixture/run.py
- python3 research-drafts/deep-qa/godot-resource-candidate/check.py
- python3 research-drafts/deep-qa/godot-resource-candidate/fixture/check_freshness.py

Outer stdout/stderr retained beside this review; per-process commands, outputs, version and hash receipts remain under fixture/results. Original/main files untouched. Exactly two actual fresh engine processes in this reviewer run; both status sequences [3], not an observed in-progress transition. Independent check.py imports no author code and uses literal mode/alias/color expectations, raw REQUEST/RESULT records, exact integer identity and file digests. Final author and reviewer use the same installed binary, not independent implementations.

IGNORE roots differ but live Gradient IDs match; changing candidate point 0 to blue also changes active and separately held Gradient. IGNORE_DEEP roots and dependencies differ; candidate blue, active red. All four live object IDs stable before/after, active root remains original. Same-process equality is meaningful; IDs need not be positive and are not persistent asset identities. Python integer parsing avoids a JavaScript Number precision round-trip. Disk-input hashes match source and remain unchanged.

GDScript inspected directly: retained active references, one request call in initialization, one get guarded by LOADED and finished flag, mutation after get in main-thread callback; candidate never assigned to active. request_count/get_count fields are declared constants, not incrementing instrumentation, so exact once execution is supported by this bounded source/control-flow inspection plus one request/result record, not counters independently proving arbitrary execution. No claim of a concurrent mutation race or nonblocking frame budget is supported.

## Freshness and history

Reran author's bounded freshness harness in the independent copy: -O and missing engine each exit nonzero, remove seeded PASS, write FAILED current invocation and record zero engine starts. These are two pre-engine failures, not engine tests. Independent inspection confirms cleanup precedes the guards and current invocation must match summary. Harness result itself is not a transactional completion receipt for arbitrary interrupted reruns; timeout, filesystem failure and malformed output were not injected here.

Inspected historical-initial invocation: FAILED after one actual process, reason identity changed: active_root_id. Historical positive-ID guard rejected a nonzero negative ID; author preserved raw values and did not revise expected alias/color outcomes. Current code uses exact nonzero integers and stable equality. Thus author initial failure1 + final2 and reviewer2 must not be described as five successful unique scenarios.

## Sources and limits

Independently read official Godot4.6 ResourceLoader page on 2026-10-31, CacheMode lines58–75 and threaded get/status/request lines165–184: ordinary IGNORE external dependencies use REUSE, deep mode propagates; status polling across frames/get after loaded is documented. https://docs.godotengine.org/en/4.6/classes/class_resourceloader.html . Source-gate fixed commit references inspected as supplied provenance, not fetched anew in this review. No full engine audit or exact-build authentication implied.

Newly checked binary SHA f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3 and raw self-report7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3 remain distinct from public source comparison35e80b3a…. README correctly limits numeric graph observation, excludes GPU sampling, latency, arbitrary graphs, repeated-path token behavior, exports and general isolation/thread safety. No material publication blocker found.
