"""Synthetic stage/identity controls; never reads a Unity build."""
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Variant:
    shader_asset: str
    pass_id: str
    stage: str
    backend: str
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class Capture:
    artifact_id: str
    complete_slices: frozenset[tuple[str, str, str, str]]
    variants: frozenset[Variant]


def scope(v):
    return (v.shader_asset, v.pass_id, v.stage, v.backend)


def stage(capture, artifact_id, variant):
    if capture.artifact_id != artifact_id:
        return "wrong_artifact"
    if variant in capture.variants:
        return "seen"
    if scope(variant) in capture.complete_slices:
        return "absent"
    return "unknown"


def diagnose(expected, requested, artifact_id, before, after, runtime):
    if requested != expected:
        return "request_mismatch"
    if runtime == "exact_and_visual_checked":
        return "tested_runtime_case_passed"
    if runtime != "strict_missing":
        return "runtime_not_verified"
    a, b = stage(before, artifact_id, requested), stage(after, artifact_id, requested)
    if "wrong_artifact" in (a, b):
        return "captures_not_comparable"
    if a == "seen" and b == "absent":
        return "lost_between_observed_stages"
    if a == "absent" and b == "absent":
        return "absent_at_both_observed_stages"
    if b == "seen":
        return "seen_late_runtime_still_missing"
    return "build_membership_unknown"


frost = Variant("weapon-A", "0:1", "fragment", "Vulkan", ("FROST",))
base = replace(frost, keywords=())
shadow = replace(frost, pass_id="0:2")
wrong_backend = replace(frost, backend="D3D11")
early = Capture("candidate-B", frozenset({scope(frost)}), frozenset({base, frost}))
late = Capture("candidate-B", frozenset({scope(frost)}), frozenset({base}))
partial = replace(late, complete_slices=frozenset())
other_build = replace(late, artifact_id="candidate-A")
named_report_a, named_report_b = len({frost}), len(late.variants)
assert named_report_a == named_report_b == 1
assert stage(early, "candidate-B", shadow) == "unknown"
assert stage(early, "candidate-B", wrong_backend) == "unknown"
cases = [
    (base, early, late, "strict_missing", "request_mismatch"),
    (frost, early, late, "strict_missing", "lost_between_observed_stages"),
    (frost, late, late, "strict_missing", "absent_at_both_observed_stages"),
    (frost, early, early, "strict_missing", "seen_late_runtime_still_missing"),
    (frost, early, partial, "strict_missing", "build_membership_unknown"),
    (frost, early, other_build, "strict_missing", "captures_not_comparable"),
    (frost, early, late, "no_message", "runtime_not_verified"),
    (frost, early, early, "exact_and_visual_checked", "tested_runtime_case_passed"),
]
print(f"equal_counts_do_not_identify_members={named_report_a}/{named_report_b}")
for req, before, after, runtime, want in cases:
    got = diagnose(frost, req, "candidate-B", before, after, runtime)
    assert got == want, (got, want)
    print(got)
