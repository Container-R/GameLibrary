# Pre-native implementation review request

2026-11-01. Frozen protocol remains `86323211989a29ef3a8cdb008fe9789100e2235c5929af979d2743c940c80e6e`; its pending-at-freeze wording is historical, with separate acceptance record.

Current implementation has not executed Godot, a version query, a socket bind or network traffic. Only six stdlib-only synthetic test methods were run in normal and optimized Python. Initial five-method successful outputs are retained separately; this is development chronology, not extra native evidence. The added sixth method constructs an explicitly synthetic receipt and rejects six receipt mutations. Such fabricated test inputs are not execution receipts.

Pre-native refinements within the protocol: client waits for all three actual connection/welcome/peer events in any order before first submit; disconnect callbacks permit teardown only after the observation is closed AND the parent STOP exists. Engine arguments remain untyped Variants until exact scalar type checks. Parent STOP cannot be written until both terminal raw payloads pass the literal oracle. Protocol has exactly three command RPCs and five control RPCs, not eight packets.

No execution authorization is implied by this document. Reviewer should inspect GDScript parsing/setup by source, then Python bounded collection/cleanup, raw and receipt binding, and synthetic mutations. Source hashes are in `SOURCE-SHA256.json`. `run.py` is the only native entry point and must not be invoked before separate approval. `test_pure.py` and `consumer.py` do not launch tools. Python `-O` is permitted for pure checks but rejected by the runner after prior-summary removal and before local imports/native entry.

The own-process-group timeout branch only attempts bounded cleanup. It is not yet executed, does not promise escaped-descendant containment, and marks incomplete drain explicitly. Minimal base environment plus five-location helper is not a sandbox. Portable consumer checks recorded paths as strings against the original invocation but reads only provided source/evidence directories; it has no dependency on current Godot bytes or historical absolute source paths.
