# Pre-native finite-number gate correction

2026-11-01. The first eight-source freeze and pure outputs remain in historical-pre-native-review. No native invocation occurred under that initial source.

Main review found that initial GDScript setup checks used abs/distance comparisons without explicitly rejecting nonfinite readbacks before queries. The final source adds a small recursive finite check for numeric configuration and actual query parameters before comparisons/native queries; post-movement transforms are checked before basis comparisons, and final configuration before result publication. Any query-parameter failure returns through closed-state checks without continuing into movement.

This is a pre-native fail-closed improvement, not a demonstrated Godot defect or failed motion experiment. Protocol geometry, masks, movement arguments and numerical tolerances are unchanged. The actual GDScript guard was reviewed as source, not invoked with injected native NaNs. Final seven-method pure suites normal/-O pass; their guarded startup Python children never invoke Godot.

The protocol contains no post-move overlap query. A bounded final blocked position and collision travel do not independently establish that the final shape has zero overlap; prose must not invent that extra test.

Before first native launch, main also requested explicit CharacterBody3D/SphereShape3D/BoxShape3D casts at subtype property reads. Accepted intermediate GD0da737f7 remains in historical-before-explicit-casts. This removes a static typing ambiguity; no parser was run and no observed parser failure is claimed. Protocol, input geometry, oracle and method arguments are unchanged.
