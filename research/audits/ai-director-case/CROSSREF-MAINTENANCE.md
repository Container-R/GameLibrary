# Stale cross-reference maintenance review

2026-11-01 01:56 UTC. Read current local canonical files; no shared edits or native execution.

## Exact text

Original stale sentence:

现有导航文章也明确未测试实际角色移动；不能把它的有限运行观察升级为完整 NPC 行动验证。

Parent proposed replacement:

导航文章随后补充了两条固定配置下的实际 CharacterBody3D 运动观察，但没有把导航路径消费与物理角色控制器耦合为完整执行器；这些有限证据仍不能验证完整 NPC 行动。

Accepted with one precision refinement to avoid implying two separate configurations:

导航文章随后补充了同一固定配置下两条通道的实际 CharacterBody3D 运动观察，但没有把导航路径消费与物理角色控制器耦合为完整执行器；这些有限证据仍不能验证完整 NPC 行动。

## Evidence and scope

Current SOL-AI-001 verification_method explicitly includes author/reviewer actual CharacterBody3D dual-lane move_and_collide observations, while excluding navigation/controller coupling and slide. Section 7 is controlled Node3D path following; section 8 is a separate no-navigation-agent fixture. The fixture README records two repeated behavior processes, the same two-lane configuration, and no complete controller stack. Thus the old blanket absence claim is stale; the proposed replacement maintains the important complete-NPC limitation rather than upgrading the case or inventing coupled execution. Earlier article sections retain their own scoped historical exclusions. No change to CASE-AI-001 verification_method is required.

## Snapshot SHA256

- `case-studies/ai/killzone3-plan-execution-continuation.md`: `21c015a5b1f57b6c17eb19a5193e7f59868f5efd6f6f2cb30676ea1092048dad`
- `solutions/ai/navigation-readiness-and-partial-path.md`: `04f94461c4295b898e068bbbe5f1effba6a9486fb11374cb9c33172281b20a94`
- `research/experiments/godot-character-motion/README.md`: `d470741ebe4ae182bfdcad5aad46521a4a25415c6fb5f3bea0488c5901f220da`
