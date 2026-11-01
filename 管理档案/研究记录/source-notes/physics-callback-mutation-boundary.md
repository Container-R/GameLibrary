# Physics callback mutation: three distinct acknowledgments

Access and local execution date: 2026-10-31. Source depth plus narrowly bounded native evidence; no universal combat policy or engine defect claim.

## Exact source boundaries

- [Godot 4.6 CollisionShape2D.disabled](https://docs.godotengine.org/en/4.6/classes/class_collisionshape2d.html#class-collisionshape2d-property-disabled): documents deferred property modification. It does not define application damage eligibility.
- [Object deferred calls](https://docs.godotengine.org/en/4.6/classes/class_object.html#class-object-method-call-deferred): idle-time processing and same-thread enqueue ordering; not a promise of one complete frame of delay.
- [SceneTree.physics_frame](https://docs.godotengine.org/en/4.6/classes/class_scenetree.html#class-scenetree-signal-physics-frame): before node physics callbacks. Four observed signals are not four separately instrumented completed solver steps.
- [Area2D overlap methods](https://docs.godotengine.org/en/4.6/classes/class_area2d.html): overlap state is updated through physics processing, not immediately by a transform assignment. This does not establish a universal N+1 observation guarantee.
- [PhysicsServer2D](https://docs.godotengine.org/en/4.6/classes/class_physicsserver2d.html): actual body-mode/space/shape getters used for configuration and diagnostic readback. Backend name and separate-thread values in RESULT remain ProjectSettings readback, not independent implementation authentication.

All following source links are immutable public comparison commit `35e80b3a8822a9df9be390814b62f44c0a9c69e8`, **not authenticated exact source of the installed executable**:

1. [CollisionShape2D setter](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/2d/physics/collision_shape_2d.cpp#L194-L204): writes local disabled member before forwarding.
2. [CollisionObject2D owner setter](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/2d/physics/collision_object_2d.cpp#L319-L336): stores owner state before invoking physics server.
3. [Server rejection](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/godot_physics_2d/godot_physics_server_2d.cpp#L351-L357): FLUSH_QUERY_CHECK precedes the backend shape change.
4. [Area signal dispatch](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/2d/physics/area_2d.cpp#L191-L205): signal emitted within callback handling. Do not substitute monitoring setter behavior for disabled setter behavior: their local-state update order differs.
5. [Step constraint islands](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/godot_physics_2d/godot_step_2d.cpp#L139-L205), [area/body pair](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/godot_physics_2d/godot_area_pair_2d.cpp), [body transform](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/godot_physics_2d/godot_body_2d.cpp#L303-L328): moved-area/active-body scheduling motivated a separately frozen kinematic revision after static control failed. This is a hypothesis, not a proven diagnosis or a general exclusion of static contacts.

## Original acceptance handoff, not a vendor API schema

| Evidence owned by the integration | Observable artifact | Insufficient substitute |
|---|---|---|
| Business eligibility | Explicit attack/target eligibility decision under the chosen game policy | A physics shape property alone |
| Mutation request | Request location, intended value, enqueue order and later observation marker | Assuming deferred means exactly next tick |
| Physical participation witness | Exact callback argument identity, exit between re-entries, finite horizon and subsequent overlap list | Repeated notification count or immediate overlap query |
| Invocation acceptance | Exact expected diagnostic envelope, both streams checked, returncode, source/contract hashes and unique receipt | Any old PASS file or arbitrary engine error treated as expected |

No business eligibility implementation is included. IDs are process-local exact integers; no positivity or cross-process identity assumption. Absent second entry is limited to the frozen observation horizon, not indefinite absence.

## Evidence links and accounting

[Current v2](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/experiments/godot-physics-callback-v2/README.md): author initial 记录别名 `历史执行记录-01`, reviewer `历史执行记录-02`, hardened author `历史执行记录-03`. Each has two behavior processes plus one version query. Same two configurations repeated, not six cases. [Independent review](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/experiments/godot-physics-callback-v2/review/REVIEW.md) includes the stdout false-acceptance demonstration and hardened pure parser checks, with no additional reviewer engine run.

[Failed v1](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/experiments/godot-physics-callback-v1/README.md) retains three failed direct processes plus three version queries; no deferred process and no accepted comparison. First subprocess returncode -6 is distinct from stderr's signal 11 diagnostic. Exact source snapshots and output bytes remain historical; they are not relabeled as current success.

Current runner SHA256 `2b00a96795564d2dc067928ceaa2f3c541ecc699873c80d9f9ae2d54a54f4803`; GDScript `51b43cf26885774284459aa67d46d603945e389b2b5352bfd760a2b2c5be4d2e`; contract `26f80627f6afea5413b664c3a4097118c437655b81fdfaa8ec47866b10aa6dde`. [Shared executable provenance](godot-runtime-provenance.md) still applies. These finite results establish neither damage exactly-once delivery nor all backend/thread/platform behavior.

> 公开衍生说明：本次仅省略安装位置、安装指纹或执行记录标识，并调整现址/固定历史链接；技术观察、失败、计数与原有证据范围保留。正文中的“本次”及身份相等陈述均属于原记录时点，本轮未重新检验，未运行旧实验，原始摘要声明不改写为新字节。文中描述性记录别名不是可执行目录名。
