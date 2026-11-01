# Explicit-cast delta acceptance

Reviewed 2026-11-01 01:39 UTC; static inspection only.

Accepted current `main.gd` SHA256 `0697b51ff020e9a42dcfcb4e7dd8d2c1cb516cb0f21a8b609fd871a8931a6595` against previously accepted `0da737f752f7b1e4be01cab7ae988a193d7f30a9ddcb1a7d26258e9dfaa71a76`. Verified all eight current manifest hashes and byte equality of the other seven files to `historical-before-explicit-casts/`.

The exact delta adds explicit CharacterBody3D, SphereShape3D and BoxShape3D casts at subtype property reads only. The scene constructs these concrete types before use; the actors array is already typed Array[CharacterBody3D]. Geometry, method arguments, finite-data gates, query/movement order, tolerances, protocol, Python oracle and consumer remain unchanged. This resolves the inspection concern without claiming an observed parser failure or a successful native parse.

No remaining material blocker from this delta. Prior CODE-ACCEPTANCE.md remains an immutable review of its earlier source. No native, version or parser invocation was performed for this review; parent reports seven pure methods passing in normal and optimized Python for the current copy. Actual engine acceptance still requires the separately authorized invocation. In particular no post-move overlap query exists, so subsequent prose must not infer final non-overlap from the bounded stop-position interval.
