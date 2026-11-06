# Box2D当前区域查询与实体命中集合

矩形冲击波结算时，场景里一名敌人可能有躯干、盾牌和感知圈三个形状，另一名敌人可能由多个刚体组成。若每收到一条物理查询回调就扣一次血，前者可能重复受伤；若第一次看见某个敌人就把它标成“处理过”，先碰到感知圈又可能让后面的有效受击形状被跳过。

这里需要构造的不是形状列表，而是一次区域效果的**实体集合**：在选定的当前状态中，只要实体有任意一块合格形状被区域查询接受，就把它纳入集合；同一实体最多结算一次。本文面向已接入 Box2D 的玩法程序员，给出从区域构造、过滤到收集和消费的完整方法。接口和实现固定为 **Box2D v3.2.0，提交 `178495ba35695aefe9c321e569d2277f06db3b90`**；代码是应用接入伪代码，例子是原创推演，不是引擎运行结果。

方法采用一个合法凸区域，并接受该版本 shape-overlap 的几何判定政策。它回答“这一刻有哪些对象入选”。一步内曾经穿过区域、持续进入和离开事件属于另一类任务，可参见[物体穿过触发区却没有事件时，先检查什么](物体穿过触发区却没有事件时，先检查什么.md)。

## 先把“这一刻”和“一个目标”定义清楚

设某次区域效果在时刻 T 结算。一个可实施的阶段顺序是：完成本次物理更新和约定的姿态修改，进入区域查询阶段，收集本次集合，离开收集阶段，再执行效果和后续世界修改。若技能规定在物理更新前结算，也可以安排在更新前；关键是所有参与者使用同一个已经提交给物理世界的状态，而不是混用渲染插值位置、待提交移动目标与物理姿态。

这不是说所有姿态修改都必须等下一次世界更新才可见。该版 `b2Body_SetTransform` 会直接更新当前变换和形状包围盒，必要时移动树代理；shape-overlap 的几何检查读取当前刚体变换。[2][4] 应用应写明哪些修改发生在 T 之前，而不是从画面看起来的位置猜查询输入。

本文对一次效果采用以下业务规则，项目可以替换它们，但必须明确替换后的含义：

- 只接受角色的受击形状 `Hurtbox`，排除感知形状和 sensor。
- 排除施放者自身、友方，以及在 T 时不存活或不能受影响的实体。
- 同一实体的多块受击形状、乃至多个刚体，共用一个应用实体键。任一合格形状被接受，实体就入选一次。
- 入选条件在收集阶段确定；之后不因回调次序重新解释这些条件。

用集合写就是：

`命中实体集合 = { owner(s) | s 被本次 OverlapShape 返回，且 s 与 owner(s) 满足上述业务规则 }`。

这里的 `owner(s)` 指形状所属的玩法实体。Box2D 回调返回的是 `b2ShapeId`，不是敌人 ID；一个 body 可挂多块 shape，多个 body 也可能属于同一敌人。[1][6] 因而，按 shape ID 去重只能去掉同一个形状，按 body ID 去重仍可能让多刚体敌人受伤多次。若玩法改成每个肢体各受伤一次，就应把键改成“实体＋肢体”，那是另一种效果规则。

“全部”也有一个参与范围：世界查询通过宽阶段树寻找形状。disabled body 的形状没有该树代理，不能靠放宽查询掩码把它找回来。[7] 需要作用于尚未加入物理世界或已禁用的角色时，应为这些对象另设业务查询途径，而不是把当前世界查询的空结果当成它们不在区域内。

## 用一个代理表达实际区域

本方法直接调用 `b2World_OverlapShape`。它内部已经完成包围盒筛选、查询过滤和形状距离检查，不需要在外面先调用一次 `OverlapAABB`，再对世界调用一次 `OverlapShape`。[1][2]

查询区域由 `b2ShapeProxy` 表达：1 到 8 个点构成凸核心，再加一个非负外部半径。一个点加半径得到圆，两个端点加半径得到胶囊，矩形可以用四个角和零半径表达。[3] 它不保留任意凹轮廓的凹口，也不表达洞。固定实现的支撑点搜索按方向取最远点，起作用的是点集的凸包；把凹多边形的边界点直接塞进去会填掉凹口。`b2MakeProxy` 还会将过多的点截到上限，不能把九点输入静默当作原来的完整区域。[3]

下面的接入只允许已经定义好的矩形、圆、胶囊模板。校验中心、角度、尺寸和点坐标均为有限数，半径非负，点数在 1 到 8 之间；矩形的两个半尺寸应大于零。以下构造函数以矩形为主例，angle 以弧度传入：

```text
MakeBoxRegion(center: b2Pos, halfWidth, halfHeight, angle):
    若 center、halfWidth、halfHeight、angle 不是有限数：返回 InvalidInput
    若 halfWidth <= 0 或 halfHeight <= 0：返回 InvalidInput

    local = [(-halfWidth, -halfHeight), ( halfWidth, -halfHeight),
             ( halfWidth,  halfHeight), (-halfWidth,  halfHeight)]
    c = cos(angle)
    s = sin(angle)
    points = [(c*x - s*y, s*x + c*y) 对 local 中每个 (x,y)]
    若 points 中有非有限坐标：返回 InvalidInput

    region.origin = center
    region.proxy = b2MakeProxy(points, 4, 0)
    返回 region
```

该版接口有一个独立的 `origin` 参数，代理点都**相对这个 origin**。origin 只提供平移；区域旋转已经写入点坐标，不应再把中心加进每个点。[1] 例如中心 `(10,5)`、半宽 2、半高 0.5、逆时针旋转 90°，传入的四点为 `(0.5,-2)`、`(0.5,2)`、`(-0.5,2)`、`(-0.5,-2)`。加上 origin 后，世界中的四角是 `(10.5,3)`、`(10.5,7)`、`(9.5,7)`、`(9.5,3)`。

同一个约定下，圆可用 `origin=圆心`、点 `(0,0)` 和圆半径；胶囊可用 `origin=中心`、旋转后的两个核心端点和胶囊半径。远离世界原点时，将点保持在查询中心附近，符合该版围绕查询 origin 做相对距离计算的方式；不要先把巨大世界坐标降精度后再相减。[2] 原点附近也可使用 `b2Pos_zero` 和世界坐标点，但两种表示方式只能选一种，不能重复平移。

## 引擎怎样把包围盒候选变成几何结果

理解返回值的范围，才能决定这一套查询是否符合玩法。该固定版本的 shape-overlap 路径依次做这些事：[2]

1. 由查询代理的点和半径构造 AABB，平移到 origin，并保守向外舍入。
2. 遍历各刚体类型的宽阶段树，检查查询盒与树中盒的重叠，做类别位粗筛。
3. 对候选形状检查双方的查询过滤条件。
4. 将目标形状的当前姿态转到查询 origin 的相对坐标中，构造目标距离代理，使用 `useRadii=true` 计算距离。
5. 仅在结果距离不大于 `0.1 × B2_LINEAR_SLOP` 时，调用应用回调。

因此，回调已经越过了引擎的几何接受步骤，应用不用把同一个距离判定再算一遍。但这一步是浮点实现的接受规则，不是严格实数意义下的相交、严格内部或完全包含测试。

### 三种“加厚”解决的是不同问题

**代理的外部半径属于几何。** 圆的半径、胶囊的厚度、圆角多边形的圆角半径都会进入距离输入；线段和 chain segment 在这条路径中使用两个端点和零半径。[3] 若形状核心之间仍有距离，两个外壳却已接触或重叠，开启半径后得到零距离是正常的。距离算法在普通输出分支扣除两边半径并把负值钳为零，也有核心重叠等提前返回分支；它没有交付有符号穿透深度，零距离时法线也不在有效输出约定内。[3]

**宽阶段盒的余量用于保守筛选和树维护。** 目标形状的树代理使用扩大后的盒，余量与形状尺度、上限及创建路径有关；静态体的创建路径也有自己的处理。当前姿态变化后，只要新盒仍被旧 fat AABB 包含，树代理可继续使用旧盒。[4] 它可以包含大量并非真实形状的空间。减少这种余量既不能消除三角形包围盒的空角，也不是修改受击范围的合适入口。

**最后的距离阈值是实现容差。** `B2_LINEAR_SLOP = 0.005 × b2_lengthUnitsPerMeter`，所以长度比例为 1 时，这里的阈值为 0.0005 个长度单位。[4] 一个已进入几何步骤的候选，即便计算出的间距为很小的正数，也可能被接受。这个阈值只在先前被树选出的候选中使用；查询 AABB 并没有另按该阈值构造一个通用距离邻域。因此不能反过来承诺“世界里凡距区域小于 0.0005 的对象都一定返回”。[2]

本文选择的政策是接受这条固定引擎路径的结果。若设计要求“只要还有任意正间隙就绝不命中”、按穿透深度分档，或目标必须完全位于区域内，应另选并验证相应几何谓词。不要把全局 slop 当技能半径调整，也不要拿零距离或见证点间距补出这些额外结论。

### AABB仍适合候选查询

`b2World_OverlapAABB` 通过树测试和过滤后就交给应用，不进行上述形状距离检查。[2] 如果需求只是找附近候选，或规则本来就是按包围盒选取，它可以直接适用。若要另做自定义精测，也可以从这些候选开始，但应用必须自己完成精测再聚合。

例如目标三角形为 `(0,0)`、`(4,0)`、`(0,4)`，半径零，查询矩形为 `[3,3.5] × [3,3.5]`。三角形的紧 AABB 包含矩形，但三角形满足 `x+y≤4`，矩形满足 `x+y≥6`。最近点 `(2,2)` 与 `(3,3)` 相距 √2，真实几何明确分离。这一差别在没有任何 fat AABB 余量时就存在。下面会把这个形状放回多形状实体，说明为什么精测和去重的先后会改变最终目标集合。

## 查询过滤要检查两个方向，业务规则接着检查

为查询选择类别，例如 `AREA_EFFECT=0x10`；目标角色形状使用 `CHARACTER=0x02`。要让区域效果查询角色，可以设：

```text
query.categoryBits = AREA_EFFECT
query.maskBits     = CHARACTER

目标形状的 categoryBits 包含 CHARACTER
目标形状的 maskBits     包含 AREA_EFFECT
```

固定 `b2ShouldQueryCollide` 同时要求：[5]

```text
(shape.categoryBits & query.maskBits) != 0
并且
(shape.maskBits & query.categoryBits) != 0
```

第一项是“查询愿意看这种形状”，第二项是“形状接受这种查询”。只把 query.maskBits 设得很宽，不能绕过目标形状的拒绝。这里的形状过滤也参与形状之间的碰撞，分配类别位时应与项目已有碰撞矩阵一起设计，避免为了伤害查询意外改变其他形状对关系。

`groupIndex` 则属于另一套优先规则。形状对的 `b2Filter` 有该字段：两形状组号相同且非零时，正组直接通过形状对过滤，负组直接拒绝；查询的 `b2QueryFilter` 只有类别和掩码，没有 groupIndex。[5] 以下两个配置可以检验迁移是否想当然：

| 配置 | 形状对过滤 | 从 A 复制类别和掩码得到的查询 Q 对 B |
|---|---|---|
| A 为 `(类别0x1, 掩码0x2)`，B 为 `(类别0x2, 掩码0x1)`，双方组号 −7 | 拒绝 | 两项位检查都非零，通过 |
| A、B 类别不变，双方掩码为 0，双方组号 +7 | 通过 | 位检查为零，拒绝 |

这只比较过滤。形状对过滤通过不保证产生接触，查询过滤通过也不保证几何被接受。前者的组规则仅在**相同且非零**的组号之间优先，负组并不是对所有其他对象都禁碰撞。旧射线接入经验中的这部分过滤比较同样适用于这里；射线的初始重叠、单面性或命中比例规则则不能迁来解释 shape-overlap。

引擎过滤之后，回调还要检查应用规则。角色形状可以都使用 CHARACTER 类别，但 `Hurtbox`、`Perception`、`Decoration` 等角色信息存在应用元数据里。这里主动排除 sensor 是示例规则，并非 shape-overlap 自动排除 sensor；若项目用 sensor 制作受击区域，应改掉这条业务排除，并保留明确的角色判定。[2][6] 自身和友方排除也由应用完成，不从 groupIndex 推导。

## 先筛合格形状，再把实体键放入集合

为每个可能被本查询返回的 CHARACTER 形状登记稳定元数据：

```text
EntityKey = (应用实体槽位, 应用实体世代号)
ShapeBinding = {
    owner: EntityKey,
    role: Hurtbox | Perception | Decoration
}
```

世代号（generation）用于区分“同一个槽位里的旧敌人”和“后来复用该槽位的新敌人”。应用保证一个仍可能被消费的键不会因世代号回绕而指向新实体。所有属于同一玩法实体的形状都写入同一个 owner，包括来自不同 body 的形状。

元数据可以通过 `b2Shape_GetUserData` 取得，也可放在应用自己的形状映射中；前者只提供一个指针，不负责被指对象的内存寿命。[6] 本例约定所有 CHARACTER 形状都必须登记绑定，非受击形状也明确登记其 role。这样，缺失绑定是接入错误，而不是默默漏掉一个可能应受伤的对象。Box2D 的 shape/body ID 是不透明句柄，不应抽出其中的内部索引当永久实体键。[6]

以下为完整收集回调。`entities.Resolve`、`TryInsert`、状态字段均是应用提供的操作，不是 Box2D API。`TryInsert` 对集合已有键返回 AlreadyPresent，对新键返回 Inserted；容器不能扩容或达到项目预算时返回 NoCapacity，不静默丢项，也不让分配异常穿过引擎回调。

```text
CollectContext = {
    caster: EntityKey,
    sourceTeam,                       // 本次施放所用阵营，收集期间不变
    entities,                         // 可按 EntityKey 检查同代活对象
    accepted: Set<EntityKey>,
    failed: false,
    failureReason
}

OnOverlap(shapeId: b2ShapeId, context) -> bool:
    if context.failed:
        return true                   // 已失败的批次不再读取应用数据

    binding = b2Shape_GetUserData(shapeId)  // 应用统一为 ShapeBinding
    if binding == null:
        context.failed = true
        context.failureReason = MissingBinding
        return true

    if binding.role != Hurtbox or b2Shape_IsSensor(shapeId):
        return true                   // 只拒绝此形状，不否定其 owner

    key = binding.owner
    entity = context.entities.Resolve(key)
    if entity == null:
        context.failed = true
        context.failureReason = StaleBinding
        return true

    if key == context.caster:
        return true
    if entity.team == context.sourceTeam:
        return true
    if not entity.alive or not entity.canReceiveAreaEffect:
        return true

    result = context.accepted.TryInsert(key)
    if result == NoCapacity:
        context.failed = true
        context.failureReason = InsufficientStorage
    return true
```

所有分支都返回 true，表示继续遍历。这里要的是完整集合，不使用提前结束查询的分支。[1] 应用拒绝一块 shape 时也返回 true，否则会把“这块不是目标”混成“后面不必再查”。回调不执行伤害、销毁或映射变更，只把已经通过几何和业务条件的实体键加入集合。

关键不变量是：**集合中只出现至少有一块合格形状的实体；不合格形状不会占用实体去重名额。** 归纳地看，每个回调只可能保持集合不变，或加入一个已经通过全部条件的键；集合又不会重复保留同一个键。因此，多块合格形状是逻辑“或”，不是多次效果。完整遍历且没有存储失败时，每个被返回的合格形状都获得了插入机会。

无需另外维护“见过的实体”集合。尤其不要在读到 owner 后立即把它记作已处理，再去检查 role、阵营或自定义几何。一个实体的感知形状被拒绝，不代表它的受击形状也该被拒绝。若采用 AABB 加自定义精测路线，几何判定也必须位于插入之前。

## 完整收集成功，才允许开始结算

Box2D 世界查询返回 `b2TreeStats`，其中是树访问统计，不是实体数量或业务成功标志。[2] 应用需要自己的结果状态，区分“成功得到空集合”和“根本没有完成一次有效收集”。

下面把区域构造与收集接起来。`QueryStageReady` 是应用调度条件：世界有效、不在物理更新或其他不允许查询的调用中，且本阶段无人改变几何、过滤、绑定、绑定内存和参与资格。它不是假设存在一个同名引擎锁接口，也不提供并发快照服务。

```text
CollectArea(worldId, region, filter, caster, sourceTeam):
    if not QueryStageReady():
        return Failure(InvalidStage)
    if not RegionInputValid(region):
        return Failure(InvalidInput)

    context = 新建空的 CollectContext(caster, sourceTeam, entities)
    if not context.accepted.TryReserve(项目预留容量):
        return Failure(InsufficientStorage)

    stats = b2World_OverlapShape(
        worldId, region.origin, &region.proxy,
        filter, OnOverlap, &context)

    if context.failed:
        丢弃 context.accepted
        return Failure(context.failureReason)
    return Success(move(context.accepted)) // 转移集合；空集合在这里才表示成功查询无目标
```

调用时机必须由应用真正保证。固定入口会断言世界未锁定，在继续执行的锁定分支中返回零统计；不能拿这种返回解释成区域内没有角色。[2] 同样，缺失绑定、无效区域和存储失败都不是“没命中”。可以给失败记录区域参数、调用阶段和失败原因，方便定位漏伤来自哪一步。

### 容量满时，不能结算前几个目标了事

官方 OverlapWorld 样例展示了“先收 ID，返回后再处理”的结构，但它最多存 16 个 shape ID，满后继续遍历而不再保存。[8] 这是该样例的选择，不是完整实体集合实现。仅仅检查“回调始终返回 true”还不够，保存结果的每一步也必须成功。

本例使用可增长的实体键集合，并把无法插入的新键标成整批失败。如果项目禁止回调内分配，可以换成预留容量的集合：满时设置失败标志，等查询返回后扩大容量、清空集合，从头重查。重试必须仍处于相同、未被修改的查询状态，使用相同区域、过滤和业务条件；不能将两个时刻的半批结果拼成一个“当前集合”。若无法保持该状态，就报告失败，按项目规则安排一次新的结算，而不是伪装成原来的查询完成。

假设 E、F 已占两个槽位，第三个不同实体 L 到达，容量却只有 2。失败分支应使**本次没有任何效果发生**，而非 E、F 先受伤、L 被遗忘。反过来，E 的第二块形状只返回 AlreadyPresent，不应被误报成容量溢出。预留容量可以减少常见分配，但不能替代对预算耗尽的处理。

### 返回后只消费应用键，不追着旧shape查询

收集成功后，可以先把键按稳定业务顺序排序，再解析为待执行效果。排序是为了明确应用消费顺序；不能依赖树回调顺序，也不能据此声称跨平台物理确定性。[1]

```text
result = CollectArea(worldId, region, filter, caster, sourceTeam)
if result 是 Failure:
    记录失败；不执行本次区域效果；结束

keys = TryCopyKeysToArray(result.set)
若复制失败：记录失败；不执行本次区域效果；结束
按 (应用实体槽位, 应用实体世代号) 原地排序 keys

// 此处仍未施加效果，集合和映射尚未被本次效果改变。
commands = 预留能容纳 keys.size 项的命令数组
若预留失败：记录失败；不执行本次区域效果；结束
for key in keys:
    entity = entities.Resolve(key)
    若 entity 不存在：记录阶段约定被破坏；不执行本次区域效果；结束
    commands.append(AreaEffectCommand(key, 本次效果参数))

// 全部收集和命令准备成功后，才进入消费阶段。
for command in commands:
    entity = entities.Resolve(command.key)
    if entity == null:
        记录 TargetGone               // 早先效果可能已销毁它
        continue
    ApplyAreaEffect(entity, command)   // 每个键最多一次
```

排序、命令准备等可能失败的存储操作都在首次效果之前完成。例子中的资格已经按 T 确定，消费时不再重做几何或阵营筛选；重新解析键只为确认仍是同代对象。如果前面的效果引发连锁销毁，后面的键可能已失效，必须跳过并记录，不能作用到复用槽位的新对象。此时“入选实体数”与“最终成功作用数”可能不同。若玩法要求 T 时入选者都先扣血、再统一处理死亡，就把销毁及连锁反应推迟到整批效果完成；这是应用的结算规则，不是查询接口提供的保证。

只存业务键还有直接的寿命收益：销毁一个 body 会同时销毁它附着的 shapes 和树代理。[9] 若收集了一串 shape ID，处理第一条就销毁 body，之后再向同一 body 的其他旧 shape 取 userData 会遇到失效对象。应用键让查询阶段完成身份转换，消费阶段无需再依赖那串物理形状，但键本身仍不延长实体寿命。

这里采用的稳定收集阶段是一项应用设计政策。官方 AABB 示例甚至会在回调内唤醒刚体，因此应区分接口允许的具体操作，与本方法为稳定结果而采用的只读收集政策。[1] 回调只收集的好处是让几何、归属和资格在整个遍历中具有一致含义，并把销毁等影响寿命的操作留到遍历之外。

## 把多形状、角色排除和容量放进同一个例子

采用前面的矩形 `[3,3.5] × [3,3.5]`，构造参数为 `origin=(3.25,3.25)`、半宽和半高都为 0.25、旋转零、半径零。查询类别为 AREA_EFFECT，掩码为 CHARACTER。以下是教学场景，所有未另行注明的形状都允许该查询，实体存活且可受影响；圆半径均为 0.1。

| 形状与归属 | 当前几何或配置 | 收集时的处理 |
|---|---|---|
| E 的躯干形状 E0 | 前述三角形，Hurtbox，半径零 | 即使进入 AABB 候选，仍会在形状距离步骤被拒绝，不进入应用回调 |
| E 的感知形状 E1 | 圆心 `(3.25,3.25)`，Perception，sensor | 几何接受后进入回调，由业务规则拒绝，不标记 E 已处理 |
| E 的受击形状 E2 | 另一个 body 上的圆，圆心 `(3.25,3.25)`，Hurtbox | 插入 E 的实体键 |
| F 的形状 F0、F1 | 两个 body 上的圆，圆心分别 `(3.1,3.1)`、`(3.4,3.4)`，均为 Hurtbox | 两条合格回调，只保留同一个 F 键 |
| G 的受击形状 | 圆心 `(3.25,3.25)`，但 shape.maskBits 不含 AREA_EFFECT | 引擎过滤拒绝，没有回调 |
| 施放者自己的形状 O0 | 圆心 `(3.25,3.25)`，Hurtbox | owner 等于 caster，业务拒绝 |
| 友方 A 的形状 A0 | 圆心 `(3.25,3.25)`，Hurtbox | 阵营规则拒绝 |
| J 的受击形状 | 几何位于区域内，但 body 已 disabled | 不在本世界查询的代理参与集合中 |

这些圆和区域明确重叠，三角形则有 √2 的间距，例子没有用近边界输入测试浮点容差。按固定实现与所列规则推演，完整入选集合为 `{E,F}`。

假设应用收到的一个可能顺序是 `E1、F0、O0、E2、A0、F1`，集合依次为：

```text
空 → 空 → {F} → {F} → {E,F} → {E,F} → {E,F}
```

感知形状先到不会排除 E，F 的两个 body 也不会产生两次结算。若把顺序换成 E2 先到，结果仍然相同。错误的“先按 owner 标成已处理，再检查 role”会被 E1 抢走 E 的名额；错误的“AABB 首次看见 E 就标记，再精测”则会被 E0 的空角候选抢走名额。两种错误都源于把“已经看过一块形状”当成“已经得到这个实体的最终答案”。

再添加一个正常入选的 L，且集合容量固定为 2，就应进入失败分支，不能把 `{E,F}` 或任何先到的两人作为完整结果。扩容后在同一状态重新查询，结果才应是 `{E,F,L}`。如果将某个可能返回的 CHARACTER 形状的绑定删除，则应得到 MissingBinding，而非一个看似正常、实际少人的成功集合。

这些变体也适合成为项目接入测试：交换回调顺序，给同一实体增加第二个 body，先返回非受击形状，让新键超过容量，销毁并复用一个实体槽位。它们分别检查集合逻辑、映射粒度、过滤次序、完整性和寿命处理，不需要靠肉眼数伤害数字来猜哪层出了错。实际项目还应在自己使用的 Box2D 构建、长度比例和代表性边界场景中验证区域输入与返回结果。

## 何时采用这条方法

一次爆炸、一次恢复脉冲、技能结算点的目标选择，都适合先问当前集合，再按实体处理。这个方案把引擎擅长的空间筛选与形状几何留给引擎，把角色语义和一次性效果留给应用。单个代理不能表达的凹区域、完整包含、严格穿透阈值，以及区间扫掠，不应通过继续堆回调条件冒充已经解决。

主要成本是遍历结果、保存唯一实体键，以及可选的排序和命令准备。实体键集合随实际入选实体数量增长；一名敌人的许多合格形状仍可能产生许多回调，去重只减少结算次数，不会撤销已经进行的空间和几何查询。可以根据实际负载调整类别过滤、预留容量和调度频率，但应在目标场景测量，不从这个示例推导性能保证。

接入完成的标准也很具体：区域点没有重复平移或遗漏旋转；查询与目标的两项位检查都明确；每个可返回形状有有效归属；只有合格形状才能把实体加入集合；存储失败不会变成半批伤害；消费阶段使用仍有效的应用身份。满足这些条件，区域查询才从“收到若干 shape 回调”变成可用于一次玩法结算的实体集合。

完整方法已在正文。可选的[应用集合复现材料](../../../../管理档案/研究/TASK-2026-0292/复现/README.md)提供原创模型、输入与结果；模型预先规定哪些回调已由引擎返回，不执行 Box2D 几何查询。

## 参考资料

以下均为 Erin Catto 与 Box2D 贡献者的官方资料，固定于 v3.2.0 提交 `178495ba35695aefe9c321e569d2277f06db3b90`，核读日期 2026-11-06。源码解释限定于该版本；应用集合、容量和结算政策为本文提出的接入方法。

1. 世界查询声明 [`include/box2d/box2d.h:75–86`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/box2d.h#L75-L86)，回调声明 [`types.h:1306–1310`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/types.h#L1306-L1310)，以及 [`docs/simulation.md:1953–2002`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/docs/simulation.md#L1953-L2002)：坐标、查询选择、遍历顺序和唤醒示例。
2. [`src/physics_world.c:2382–2560`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/physics_world.c#L2382-L2560)：AABB 回调、shape-overlap 过滤与距离接受、当前相对变换、锁定分支、各树遍历和统计；[`src/dynamic_tree.c:884–945`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/dynamic_tree.c#L884-L945) 与 [`src/aabb.h:52–64`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/aabb.h#L52-L64)：候选筛选与查询盒的保守平移。
3. [`include/box2d/collision.h:24–53`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/collision.h#L24-L53) 与 [`390–438`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/collision.h#L390-L438)：代理、相对坐标和距离输出；[`src/distance.c:108–164`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/distance.c#L108-L164) 与 [`424–611`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/distance.c#L424-L611)：点数截断、凸支撑与距离分支；[`src/shape.c:1153–1169`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/shape.c#L1153-L1169)：目标形状的代理构造。
4. [`src/shape.c:36–104`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/shape.c#L36-L104)、[`1131–1142`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/shape.c#L1131-L1142) 与 [`src/broad_phase.c:55–66`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/broad_phase.c#L55-L66)：形状余量及树代理；[`src/body.c:730–783`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/body.c#L730-L783)：SetTransform；[`src/geometry.c:430–451`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/geometry.c#L430-L451) 与 [`include/box2d/constants.h:39–79`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/constants.h#L39-L79)：半径与额外盒余量、长度比例与容差。
5. [`include/box2d/types.h:318–373`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/types.h#L318-L373) 及 [`src/shape.h:118–131`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/shape.h#L118-L131)：形状对 groupIndex 优先与查询双向类别／掩码检查。
6. [`include/box2d/box2d.h:727–752`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/box2d.h#L727-L752)、[`include/box2d/id.h:44–59`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/id.h#L44-L59)、[`src/shape.c:155–188`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/shape.c#L155-L188) 及 [`docs/simulation.md:410–421`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/docs/simulation.md#L410-L421)：形状归属、userdata、不透明句柄与应用关联。
7. [`src/shape.c:171–175`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/shape.c#L171-L175) 与 [`src/body.c:1762–1821`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/body.c#L1762-L1821)：disabled body 的代理参与范围。
8. [`samples/sample_collision.cpp:1785–1821`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/samples/sample_collision.cpp#L1785-L1821) 与 [`2048–2112`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/samples/sample_collision.cpp#L2048-L2112)：OverlapWorld 收集上限、代理构造与返回后的销毁结构。
9. [`src/body.c:345–397`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/body.c#L345-L397) 与 [`src/physics_world.c:1617–1648`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/physics_world.c#L1617-L1648)：销毁附着形状与代理，以及形状 ID 的存在性、世代检查。

---

[返回物理检测专题](README.md)
