# Box2D两凸形状的表面间距与见证点查询

给已经选中的两个物体画一把间隙量尺，看起来只需连接两个最近点。但圆心可能偏离刚体原点，两个刚体又有不同的旋转；拿错一个坐标系，线段就会画到物体之外。遗漏圆角半径，量到的是内部核心；把零距离时的两点长度当成间隙，还可能在两个外壳已经重叠时画出一条“尚有余量”的线。

本文面向能读取几何和刚体姿态的玩法程序员，完成一个 `MeasureSurfaceGap(A, B)` 包装：取得同一当前状态中的两份凸几何，构造距离输入，把正间距、世界见证点与方向交给量尺或近接提示，并管理重复查询的缓存。接口固定于 **Box2D v3.2.0，提交 `178495ba35695aefe9c321e569d2277f06db3b90`**。下文实现为应用伪代码，数值例子为解析推演，不是引擎运行日志。

这里的“表面间距”是两个**实心凸形状的非负间距**：分离时是两个外壳之间的最短距离；接触或重叠时不再有正间隙。它不是穿透深度。一个圆完全进入矩形内部时，也不能用这项结果回答“圆边界离矩形边界还有多远”。本方法只处理已经确定的一对形状，不搜索整个世界、不应用碰撞过滤，也不判断两次采样之间是否撞过东西。[1][2]

## 从同一状态取出几何与姿态

先约定测量的时刻 T。例如，在物理更新和本帧姿态修改完成后，进入只读测量阶段，复制两份几何和姿态，再允许世界继续变化。不要给 A 读取物理姿态，却给 B 使用尚未提交的移动目标或渲染插值姿态。分别读取字段也不会自动产生快照；整个读取阶段必须由应用保证没有几何替换、销毁或并发写入。

包装使用以下应用数据：

```text
ShapeSnapshot = {
    identity: (应用形状槽位, 世代号),
    geometryRevision,
    geometry: Circle | Capsule | ConvexPolygon,
    world: b2WorldTransform,
    stateStamp                         // 此次共同读取阶段的标记
}
```

`identity` 区分同一槽位先后出现的形状，`geometryRevision` 在几何内容或点索引布局变化时更新；应用保证仍可能复用的身份与版本不会因计数回绕而误认成旧值。二者都是应用字段，不是 Box2D 距离结构自带的身份。`stateStamp` 用于检测错配和标记调试结果，不能代替实际的只读阶段。

已经注册到世界的形状，可以沿下面的公开接口读取。`ReadApplicationIdentityAndRevision` 表示应用形状记录中保存的身份与版本，读取它和读取引擎几何处于同一稳定阶段。

```text
CaptureShape(shapeId, stateStamp):
    if not b2Shape_IsValid(shapeId): return InvalidInput
    kind = b2Shape_GetType(shapeId)
    switch kind:
        b2_circleShape:  geometry = Circle(b2Shape_GetCircle(shapeId))
        b2_capsuleShape: geometry = Capsule(b2Shape_GetCapsule(shapeId))
        b2_polygonShape: geometry = ConvexPolygon(b2Shape_GetPolygon(shapeId))
        otherwise: return UnsupportedShape

    bodyId = b2Shape_GetBody(shapeId)
    world = b2Body_GetTransform(bodyId)
    identity, revision = ReadApplicationIdentityAndRevision(shapeId)
    return ShapeSnapshot(identity, revision, geometry, world, stateStamp)
```

先检查类型，再调用匹配 getter：这些 getter 返回几何拷贝，类型不符会触发断言。[3] 圆心、胶囊端点和多边形顶点都保留在所属刚体的局部坐标中，配套姿态应为这个 body 的世界变换，而不是质心位置。形状的偏心已经写在几何里，无需另外把 body 原点换成圆心。

本包装只接入圆、胶囊和合法凸多边形。它不把 chain segment 变成“带单面语义的距离形状”；即使内部距离路径能将线段表示成两点代理，距离函数也没有因此提供链的单面接触规则。[4] 如果输入来自纯几何工具而非物理世界，也可以直接创建上述快照，不必先建立 body。Box2D 的几何接口本来就可独立于刚体模拟使用。[2]

## 用局部点和半径表达实际外壳

`b2ShapeProxy` 保存 1 至 8 个点，以及一个非负外部半径。距离算法使用的是点集的**凸核心**，然后考虑半径包裹出的外壳。[1] 一个点加半径是圆；两个端点之间的线段加半径是胶囊；凸多边形顶点加半径得到圆角多边形。

这一表示会保留核心的边和内部，不是仅有若干孤立顶点。按方向取最远点的支撑点搜索，对点集及其凸包会给出相同最大点积，所以任意凹轮廓的凹口、洞都不会保留下来。[4] 输入是否意在表示这个凸包，必须在资产或模板层确定，不能把一串凹轮廓点交进来后继续按原轮廓解释结果。

下面把受支持几何复制成代理。多边形必须已经通过合法的 Box2D 多边形构造流程，例如 `b2MakeBox`，或成功的 `b2ComputeHull` 再接 `b2MakePolygon`。后者先检查 hull 是否创建成功；仅有有限点和合法点数，不等于已构造出可用于模拟的 polygon。[1][2]

```text
MakeLocalProxy(geometry):
    switch geometry.kind:
        Circle:
            points = [geometry.center]
            radius = geometry.radius
        Capsule:
            points = [geometry.center1, geometry.center2]  // 显式两元素数组
            radius = geometry.radius
        ConvexPolygon:
            if geometry.count < 3 or geometry.count > 8:
                return InvalidInput
            points = copy geometry.vertices[0 .. geometry.count)
            radius = geometry.radius
        otherwise:
            return UnsupportedShape

    if points.size < 1 or points.size > 8: return InvalidInput
    if 任一点不是有限数: return InvalidInput
    if radius 不是有限数 or radius < 0: return InvalidInput
    return b2MakeProxy(points, points.size, radius)
```

不要等 `b2MakeProxy` 替调用方拒绝九点输入：固定实现将点数截到 8，后面的点会被舍弃。[4] 低层代理可以只有一个或两个点，而物理 polygon 要求至少三个点及足够面积；这两项输入合同不能互相替代。上面仍保留一、两点路径，是为了圆和胶囊，不是放行退化 polygon。

半径是几何尺寸，不是求解容差或树中 AABB 的额外余量。姿态则只表示旋转和平移，没有缩放。非均匀缩放后的圆一般也不再是圆；若需要改变体型，应先生成确实表达新体型的受支持几何，并更新几何版本。

以下用一对有旋转和偏心的形状贯穿测量。所有长度采用同一项目单位：

| 输入 | A：圆角矩形 | B：偏心圆 |
|---|---|---|
| 局部核心 | `(-2,-1)、(2,-1)、(2,1)、(-2,1)` | 圆心 `(1,0)` |
| 外部半径 | 0.25 | 0.5 |
| 世界原点 | `(10,5)` | `(11,8)` |
| 逆时针旋转 | 90° | 180° |

A 可以由 `b2MakeRoundedBox(2, 1, 0.25)` 构造。在固定实现中，两个半尺寸描述核心，半径再向外增加厚度；不要把核心缩成另一种“外轮廓尺寸固定”的圆角盒。[5] B 的圆心经过自身旋转和平移后是 `(10,8)`，并不是 body 原点 `(11,8)`。

## 把B变到A中，而不是把两份点都改成世界点

距离输入只有一份相对姿态 `input.transform`：**B 的局部坐标到 A 的局部坐标的变换**。代理仍保存各自原来的局部点。[1]

令两个世界姿态为 `T_A=(R_A,p_A)` 和 `T_B=(R_B,p_B)`。B 的局部点 b 对应的世界点为 `R_B b+p_B`；再施加 A 的逆变换，得到：

```text
b_in_A = R_Aᵀ(R_B b + p_B - p_A)
       = R b + p

R = R_Aᵀ R_B
p = R_Aᵀ(p_B - p_A)
```

转置 `R_Aᵀ` 在这里就是旋转的逆。固定版本入口会按这份相对姿态将 B 的所有点转入 A，然后在 A 中执行距离计算。[4] 因而，不能先自行把 B 点转入 A，再把同一相对姿态传进去，否则会重复变换。

实际世界姿态采用 `b2WorldTransform`，应使用匹配的 helper：[6]

```text
relative = b2InvMulWorldTransforms(A.world, B.world)
input.proxyA = MakeLocalProxy(A.geometry)
input.proxyB = MakeLocalProxy(B.geometry)
input.transform = relative
input.useRadii = true
```

只有当两个输入本来都是局部 `b2Transform` 时，才用 `b2InvMulTransforms`。固定版本可选大世界模式中，世界平移为 double，但局部向量、相对平移及旋转仍为 float。world helper 先减两个世界位置，再将差转成 float；先把两个巨大世界位置各自转成 float 再相减，会在做差之前丢失小间距。这种相对计算减少了对世界原点的依赖，但不保证任意大相对距离、极小形状或极端尺度下都精确。[6]

贯穿例中，相对旋转为 `180°−90°=90°`，相对平移为 `R(-90°)·(1,3)=(3,-1)`。B 的局部圆心 `(1,0)` 经相对旋转成为 `(0,1)`，再平移得到 A 中的 `(3,0)`。A 的矩形核心仍是原来的四个点。现在问题简化为：在 A 中，矩形 `[-2,2]×[-1,1]` 与点 `(3,0)` 相距多少。

输入校验还必须覆盖世界位置有限、旋转有限且归一化，以及计算出来的相对姿态有效。可分别使用 `b2IsValidWorldTransform` 和 `b2IsValidTransform`。[6] 全零结构的旋转 `(c,s)=(0,0)` 不是恒等旋转；需要无旋转时用 `b2Rot_identity`，需要恒等变换时用相应 identity 常量。

## 最近点为什么能落在矩形边的内部

对上述矩形，任意核心点的 x 坐标都不大于 2，所以它到 `(3,0)` 的距离至少为 1。边内点 `(2,0)` 恰好达到这个下界，因而最近核心点是 `(2,0)` 与 `(3,0)`。只枚举输入顶点会选到 `(2,1)` 或 `(2,-1)`，得到 √2，量错的原因不是浮点误差，而是漏掉了边。

`b2ComputeShapeDistance` 使用 GJK（Gilbert–Johnson–Keerthi）凸形状距离算法，不是穷举顶点对。[4] 可以把两凸核心的最近点问题写为“在差集里找离原点最近的点”。固定实现的差向量为 `w=wA−wB`，其中两个点都已在 A 中。沿某个方向，它取 A 在该方向的支撑点，以及 B 在反方向的支撑点，再相减。搜索中维护的单形是由这些差点组成的点、线段或三角形。

线段或三角形上的最近点可以写成几个差点的加权和。将同一组权重分别应用于它们对应的 A 点和 B 点，就还原出两个核心上的见证点：它们共同说明这段距离由哪两个位置取得。固定实现确实这样处理一、二点单形；三点包住原点时返回零距离，并把两见证点设为同一个位置。[4]

在贯穿例中，`(2,0)` 就是右边两个顶点 `(2,-1)`、`(2,1)` 各取一半的组合。这解释了“查询用顶点构造，输出却在边内”的合理性。见证点不是持久的顶点身份；移动形状后，最近特征和权重都可以改变。

### 开启半径，才量到外壳

设普通输出路径取得核心见证点 a、b，核心距离为 d，A 指向 B 的单位方向为 n。分离核心的几何关系中，`n=(b−a)/d`。开启 `useRadii` 后，固定实现的后处理为：[4]

```text
gap    = max(0, d - rA - rB)
pointA = a + rA * n
pointB = b - rB * n
```

本例 `d=1`，所以 `gap=1−0.25−0.5=0.25`，两个外壳见证点在 A 中分别为 `(2.25,0)` 和 `(2.5,0)`，有效方向为 `(1,0)`。关闭 `useRadii` 会保留核心距离 1 与核心点 `(2,0)、(3,0)`；这不是另一种精度设置，而是改变了被测几何，不再满足表面量尺的需求。

正距离时，这些点可用于描画最短连接线。零距离时则应换一条消费路径。普通后处理可能把负的间距钳成零，却仍向外偏移两点；两点甚至可能交换先后位置。核心重叠或搜索方向极小时，还会在半径后处理之前提前返回零。[4] 因此，“零结果一定还有两个外壳上的最近点”不是所有分支共同保证的合同。

## 用结果类型限制消费者能做什么

把原始结构直接交给渲染或玩法，容易使调用方在每次使用时重新猜字段含义。更稳妥的接口明确区分：

- `PositiveGap`：API 报告正间距，提供这次测量的两见证点、世界方向和距离。
- `ZeroDistance`：API 未报告正间距，表面见证点和方向字段为空；原始结果可单独留给诊断。
- `InvalidInput / UnsupportedShape / InvalidResult`：读取、构造或数值检查失败，不把它们转换成零距离。

头文件明确规定零距离时 normal 无效。[1] 即使某个零值分支恰好残留了非零 normal，也不应让高层将它用于分离箭头。`ZeroDistance` 同时也不能认证“发生了多少穿透”或严格实数意义的边界接触。

以下为默认每次冷启动的完整测量包装。`Fail` 是应用辅助操作，返回给定错误；带缓存的可选版本将在后文替换缓存选择及返回处理。几何已经满足前述合法输入要求，`stateStamp` 相同还必须有真实稳定读取阶段作保障。

```text
MeasureSurfaceGap(A, B):
    if A.stateStamp != B.stateStamp: return Fail(InvalidInput)
    proxyA = MakeLocalProxy(A.geometry); 失败则返回该错误
    proxyB = MakeLocalProxy(B.geometry); 失败则返回该错误
    if not b2IsValidWorldTransform(A.world): return Fail(InvalidInput)
    if not b2IsValidWorldTransform(B.world): return Fail(InvalidInput)

    relative = b2InvMulWorldTransforms(A.world, B.world)
    if not b2IsValidTransform(relative): return Fail(InvalidInput)
    input = b2DistanceInput {
        proxyA, proxyB, transform=relative, useRadii=true
    }

    cache = b2_emptySimplexCache
    out = b2ComputeShapeDistance(&input, &cache, NULL, 0)
    if out.distance 不是有限数 or out.distance < 0:
        return Fail(InvalidResult)

    if out.distance == 0:
        return ZeroDistance {
            distance=0, stateStamp=A.stateStamp,
            surfaceWitnesses=absent, normalWorld=absent,
            rawDiagnostics=out
        }

    if out.pointA、out.pointB 或 out.normal 含非有限数:
        return Fail(InvalidResult)
    pointAWorld = b2TransformWorldPoint(A.world, out.pointA)
    pointBWorld = b2TransformWorldPoint(A.world, out.pointB)
    normalWorld = b2RotateVector(A.world.q, out.normal)
    if 任一转换结果含非有限数: return Fail(InvalidResult)

    return PositiveGap {
        distance=out.distance, stateStamp=A.stateStamp,
        pointAInA=out.pointA, pointBInA=out.pointB,
        pointAWorld, pointBWorld, normalWorld
    }
```

这里有三个容易漏掉的细节。第一，**两个输出点都经过 A 的世界变换**，因为 `pointB` 也在 A 中；法线只旋转，不加平移。[1][6] 第二，变换用的是本次快照中的 `A.world`，不能查询结束后再取一个已经移动的姿态。第三，distance 原样保留 API 的标量，不用两点长度“修复”它。

本例 A 的世界映射为 `(u,v)→(10−v,5+u)`。因此世界见证点为 `(10,7.25)`、`(10,7.5)`，世界 A→B 方向为 `(0,1)`。若把 `pointB=(2.5,0)` 当成 B 局部点，再用 B 的 180°旋转和世界原点去变换，会画到 `(8.5,8)`，与实际外壳位置无关。这也是为什么仅在 A 位于世界原点时直接画返回点的示例，不能原样迁入任意姿态。[7]

有限性检查用于挡住明显异常，不给结果附加误差认证，也不承诺任何有限浮点输入都不会在内部运算中溢出。项目仍须限定可用的几何尺寸、相对距离与长度比例。该 API 没有通用“已收敛”成功字段；`iterations` 是诊断量，不能通过“非零”或“小于 20”把一次查询认证为精确计算。[1][4] 对近退化几何和接近零的输入，仍需在项目所用构建与长度比例下做针对性测试。

### 量尺与近接提示分别消费

示例把业务阈值设为 `h=0.3`，表示 API 报告的间距不大于 0.3 时提示“接近”。h 必须有限且非负，其取值由项目单位和体验要求决定，不借用某个世界查询的内部容差。

```text
result = MeasureSurfaceGap(A, B)
if result 是错误:
    隐藏本次量尺和旧提示，记录错误，将近接状态设为 Unknown
else:
    near = (result.distance <= h)
    显示本次 near 状态
    if result 是 PositiveGap:
        连接 result.pointAWorld 与 result.pointBWorld
        标注 result.distance
    else:
        隐藏连接线和方向箭头，显示“无正间隙”
```

初始状态的 0.25 不大于 0.3，所以提示“接近”；若阈值改为 0.2，就不提示。零值也在阈值内，但不因此获得合法的推出方向。若需求是接触点及可正可负的 separation，应根据明确的形状对选择接触流形接口；这些接口提供的信息种类不同，也不自动等于任意凸体的最小脱离平移。[8] 若需求是运动过程的安全前进量，应另用运动查询，而不是把当前 gap 当作任意运动方向上的可走距离。

## 重复测量时，缓存跟随有序形状对

每次使用 `b2_emptySimplexCache` 已经是完整首版。缓存只是一项可选 warm start：官方说明，姿态相近的重复查询可能受益，没有承诺固定加速比例。[1][2]

`b2SimplexCache` 保存的是单形点数和 A、B 两组顶点索引，不含旧距离、旧姿态、形状身份或几何版本。下次调用从当前 proxy 中按这些索引重新取点。固定实现只断言缓存点数不超过 3，没有替应用判断索引属于哪个形状，也没有逐个验证它们仍小于当前 proxy.count。[4] 即使底层点数组仍有 8 个槽，旧索引也可能落在当前有效点数之外，或者指向完全不同的几何。

因此，可选缓存使用应用维护的有序键：

```text
PairKey = (A.identity, B.identity,
           A.geometryRevision, B.geometryRevision,
           mode=SurfaceGap)
PairCache = { valid=false, key, simplex=b2_emptySimplexCache }
```

A、B 的先后有意义，不能先排序成无序对。将这组状态接入前一节包装时，按以下流程替换缓存选择与返回处理：

```text
// pairState 由这一个查询序列独占；不得来自任意序列化字节。
key = PairKey(A.identity, B.identity,
              A.geometryRevision, B.geometryRevision, SurfaceGap)
cache = b2_emptySimplexCache
if pairState.valid and pairState.key == key and 本次允许连续复用:
    s = pairState.simplex
    if 0 <= s.count <= 3 and
       对每个 i < s.count 都有 s.indexA[i] < proxyA.count 且
                              s.indexB[i] < proxyB.count:
        cache = s

out = b2ComputeShapeDistance(&input, &cache, NULL, 0)
result = 按前一节完成标量检查、结果分派和世界转换
if result 是错误:
    pairState.valid = false
else:
    pairState = { valid=true, key=key, simplex=cache }
return result
```

输入阶段报错也使 `pairState.valid=false`。索引检查只是附加防护，不能替代正确更新身份和版本：重排四个顶点后，旧索引仍可能全在范围内，却已失去原来的意义。

应用在以下时机清空缓存，或使键改变而自然冷启动：形状销毁再建、交换 A/B、改变点数、点顺序或点坐标、替换形状种类。本文还把半径改变计入几何版本，切换核心／表面测量模式也换键，这是便于管理的保守政策；仅改半径并不意味着核心顶点索引本身必然失效。

同一对形状仅有正常的相邻姿态变化时，不必每次增加几何版本。仍按新姿态构造相对变换，再使用原索引热启动。若调用对象随机跳换或姿态作不连续的大幅切换，首版政策直接冷启动，不发明一个通用“移动超过多少必须清空”的阈值。不同并发调用不能共用同一可写 PairCache；需要各自状态，或由调用方串行化它们。

## 把零值、姿态和缓存放回同一个例子

保持两份几何及旋转不变，只把 B 的世界原点写成 `(11,5+x)`。相对平移为 `(x,-1)`，偏心圆心在 A 中为 `(x,0)`。对 `x>2` 的状态，最近核心点仍是 `(2,0)` 与 `(x,0)`，核心距离为 `x−2`。下面是解析几何及普通半径分支的代数预期，不是原生逐位返回记录：

| B 世界原点 | x | 核心距离 | 表面 gap | 普通分支在 A 中的 pointA / pointB | 包装给消费者的结果 |
|---|---:|---:|---:|---|---|
| `(11,8)` | 3 | 1 | 0.25 | `(2.25,0)` / `(2.5,0)` | PositiveGap，世界点及方向可用 |
| `(11,7.75)` | 2.75 | 0.75 | 0 | `(2.25,0)` / `(2.25,0)` | ZeroDistance，表面字段为空 |
| `(11,7.5)` | 2.5 | 0.5 | 0 | `(2.25,0)` / `(2,0)` | ZeroDistance，表面字段为空 |

第二行是数学上的外壳恰好接触，不能拿纸面算术认证任意构建在边界上必然逐位为零。第三行揭示了消费错误：两个原始点相距 0.25，却是半径偏移后发生交叉产生的长度，gap 仍是零。若用它覆盖 distance，画面会把已重叠的外壳显示成还有 0.25 的空间。

再把 B 原点改成 `(11,6)`，圆心在 A 中是 `(1,0)`，已处于矩形核心内部。这时数学核心距离为零，固定算法有提前零返回路径；不能继续套用上一表的边内点及半径偏移，断言输出一定是两个外壳点。包装仍只交付 ZeroDistance，具体原始点留作诊断。

在初始分离状态交换 A/B，数学间距应相同，见证点两侧与方向随顺序交换，但输出参考系也变成新的 A。实现上必须重新构造相对姿态、清空有序对缓存，并用新 A 的世界姿态转换两个点。若随后把圆角矩形换成三角形，即使应用槽位不变，也要更新几何版本、重新构造 proxy，不能将旧的四点索引继续用于三点输入。

接入测试可以围绕这些有区分力的变化，而不是只测两个原点上的圆：

- 平移、旋转整个场景，检查 gap 保持相同，世界点随场景变换；保留偏心圆心，避免恒等姿态掩盖错误。
- 关闭半径，确认本例变成核心距离 1；恢复表面模式后再回到 0.25。
- 对外壳接触、仅外壳重叠、核心重叠三种输入，确认零结果不会泄露可被消费的表面方向。
- 用同一姿态序列比较冷、暖缓存结果，并测试 A/B 交换、形状重建和点顺序变更；先检查版本政策，再讨论缓存是否值得保留。

正距离、数值条件合适时，可将“两世界见证点距离接近返回 distance”和“连接方向与 normal 一致”作为诊断；不要据此自动覆写返回值，对零结果也不使用这项等式。项目需要以所用浮点构建、几何尺寸和显示精度设定测试容差，没有适用于所有尺度的统一 epsilon。

## 何时值得保留这层包装

只有圆圆一类几何时，直接按圆心距离减半径更简单。引入胶囊、凸多边形及圆角后，统一代理减少了应用自行维护所有类型组合的负担；代价是仍要维护局部几何、同一状态的姿态和结果合同。每个代理最多复制 8 个点，冷缓存也免去了跨帧索引寿命管理。是否进一步缓存代理、增加热启动或降低测量频率，应根据实际调用负载测量，而不是从教学例子推导性能收益。

这层包装的价值在于让消费者拿到明确的信息：正距离时是一段有位置和方向的当前间隙，零距离时只表示没有报告正间隙，错误则独立处理。若工作目标是“当前区域里哪些实体入选”，应使用[Box2D当前区域查询与实体命中集合](Box2D当前区域查询与实体命中集合.md)中的世界查询与聚合方法；若目标变成推出、连续避障或凹形复合体距离，则需要相应的新几何合同，不能仅靠给本包装增加一个阈值解决。

完整流程已在正文。可选的[精确算术与缓存政策复现材料](../../../../管理档案/研究/TASK-2026-0293/复现/README.md)提供本例的原创计算模型与输入输出；它不加载 Box2D，也不执行 GJK 或验证原生冷暖缓存结果。

## 参考资料

以下均为 Erin Catto 与 Box2D 贡献者的官方资料，固定版本为 v3.2.0、提交 `178495ba35695aefe9c321e569d2277f06db3b90`，核读日期 2026-11-06。快照、结果类型、业务阈值及缓存身份政策为本文的应用设计。

1. [`include/box2d/collision.h:24–57`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/collision.h#L24-L57)、[`126–170`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/collision.h#L126-L170)、[`372–440`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/collision.h#L372-L440)：代理、形状局部几何、相对变换、距离输出与缓存合同。
2. [`docs/collision.md:15–139`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/docs/collision.md#L15-L139)、[`257–275`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/docs/collision.md#L257-L275)：独立几何接口、合法多边形构造、距离缓存与运动查询的不同用途。
3. [`include/box2d/box2d.h:413–437`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/box2d.h#L413-L437)、[`732–742`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/box2d.h#L732-L742)、[`834–848`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/box2d.h#L834-L848)，及 [`src/shape.c:1566–1604`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/shape.c#L1566-L1604)：形状类型、几何拷贝及所属 body 的世界姿态。
4. [`src/distance.c:108–247`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/distance.c#L108-L247)、[`249–419`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/distance.c#L249-L419)、[`424–611`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/distance.c#L424-L611)，及 [`src/shape.c:1153–1173`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/shape.c#L1153-L1173)：代理截断、支撑点、缓存索引、单形权重、差集方向、B 转入 A、提前返回和半径后处理。差向量以实际赋值 `wA−wB` 为准。
5. [`src/geometry.c:139–164`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/src/geometry.c#L139-L164)：矩形核心半尺寸与圆角半径。
6. [`include/box2d/math_types.h:12–65`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/math_types.h#L12-L65)、[`92–99`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/math_types.h#L92-L99)，及 [`math_functions.h:18–41`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/math_functions.h#L18-L41)、[`459–520`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/math_functions.h#L459-L520)、[`548–598`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/math_functions.h#L548-L598)：坐标类型、有效性、相对变换、世界点转换与方向旋转。
7. [`samples/sample_collision.cpp:309–328`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/samples/sample_collision.cpp#L309-L328)：ShapeDistance 样例的调用与 A 位于世界原点的前提。
8. [`include/box2d/collision.h:594–650`](https://github.com/erincatto/box2d/blob/178495ba35695aefe9c321e569d2277f06db3b90/include/box2d/collision.h#L594-L650)：接触流形的 separation 与特定形状对入口。

---

[返回物理检测专题](README.md)
