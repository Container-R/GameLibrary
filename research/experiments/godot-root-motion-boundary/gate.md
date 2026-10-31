# Native root-motion source gate — 2026-10-31

## 现有证据逐字记录（先于任何新计划）

来源：gamelibrary-publish-rig/solutions/animation/turn-in-place-foot-sliding.md

```text
verification_method: 官方版本文档与日本原始项目职责材料核对；既有4项Python二维接触模型测试；Rig依赖交接与六行接收表未执行，未运行引擎或真实角色资产
```

来源：gamelibrary-publish-rig/research/experiments/root-motion/README.md，全文：

```text
# 转身接触点变换：最小几何反例

运行环境：2026-10-31，Linux，Python 3.12.14，标准库 math/unittest。执行 `python3 research/experiments/root-motion/test_contact_transform.py`，4 项通过，见 [原始输出](test-output.txt)。

原创二维刚体模型：世界脚点 W = P + R(θ)L。给定地面锚点 A，局部目标 L = R(-θ)(A-P)。没有骨骼、关节限制、求解器、引擎回调、重定向或联网。

实测：
1. 根旋转90°且局部脚点作相应逆变换，世界点仍在(1,0)。
2. 同一局部姿态却应用两次90°旋转，世界点偏差为√2个长度单位。
3. 两端姿态各自满足接触，不代表局部脚点线性混合与根旋转插值后仍满足接触；例中偏差为1−1/√2。
4. 根平移/旋转后使用逆变换求局部锚点，点约束在数值容差内成立。

用途是反驳“两个端点都正确，所以混合必然不滑”和“再转一次角色不会影响脚底”两种假设。它不证明某个引擎实际使用线性脚点混合，也不证明逆运动学一定可达；真实腿长、地形、碰撞及求解顺序必须在目标项目中测试。没有性能基准或动画质量评分。
```

以上只有4项Python二维模型测试。未存在该文章的Godot根运动实测。以下全部为新来源门槛与未执行计划。

## 已读取来源及精确界限

访问2026-10-31，Godot4.6官方文档：
- https://docs.godotengine.org/en/4.6/classes/class_animationmixer.html — root_motion_track，MANUAL，advance，get_root_motion_position/rotation。骨路径对应变换被视觉抵消，getter返回delta且为const；示例由用户代码把结果应用到CharacterBody3D。MANUAL用advance驱动。
- https://docs.godotengine.org/en/4.6/classes/class_animationtree.html — Description：播放与过渡由Tree处理，所连Player只管理动画资源。不能同时让Player自动播放形成第二驱动源。

GitHub插件实际读取固定比较源码：
https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/animation/animation_mixer.cpp

- 1046–1053 `_blend_init`：新一轮混合初始化重置根delta字段。
- 1234：轨道路径匹配决定root_motion标志。
- 1870–1905：root-motion分支把缓存写到返回字段；普通骨/Node3D姿态应用位于互斥分支，而不是该分支额外移动角色父节点。
- 2091–2096：两个getter直接返回成员，没有清除或累计消费动作。

**源码支持的判断：** 在一次求值后且没有下一次求值/缓存重置等变化时，重复getter是读取当前delta，不是从事件队列取走一次性运动。提取不是让任意角色控制器自动移动；用户适配器仍需决定何时应用。这里只分析这些分支，不声称穷尽全部动画生命周期、混合/循环/seek行为。

## 实机能力与来源身份

仅查找路径和读取可执行文件hash，没有启动Godot。现有 `/usr/local/bin/godot` SHA256实际读回为 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`。

共享说明 `research/source-notes/godot-runtime-provenance.md`：已归档安装构建自报4.6.3.stable.official.7d41c59c4，engine hash7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3；公开4.6.3-stable对应35e80b3a8822a9df9be390814b62f44c0a9c69e8，两者身份不一致。比较源码不等于该binary经认证的精确源码；不得声称官方真实性、恶意或引擎缺陷。执行时应重新记录真实版本/hash，不能只复制旧元数据。

## 最小有价值的原生实验提案（尚未执行）

建议两个新进程，均使用原创一骨Skeleton3D、Node3D父节点、AnimationPlayer资源容器、AnimationTree和单AnimationNodeAnimation。无需网格、外部rig、图像、DCC或安装。直接构造Animation资源的POSITION_3D与ROTATION_3D轨道，路径同一个root骨；两秒非循环clip，位置由(0,0,0)到(4,0,0)，绕Y轴旋转由0到90°，线性/球面插值。显式RESET为零位姿；MANUAL，Tree唯一播放者；初始化advance(0)后取基线。

### 两个配置

1. **正常姿态对照**：root_motion_track为空，advance(0.5)。预期root骨位置(1,0,0)、旋转22.5°；父Node3D不动。用来证明原创轨道确实驱动目标，不以“输出始终零”冒充提取成功。
2. **提取配置**：root_motion_track选定root骨，advance(0.5)。预期提取delta位置(1,0,0)、旋转22.5°；骨保持RESET位姿，角色父节点不动。连续读取两次position/rotation，中间不advance，两个读值相等且第二次非零。随后advance(0.25)，预期新delta为(0.5,0,0)/11.25°，不是从起点累计到1.5/33.75°。

应用观察使用独立的简单Node3D展示接收者；不冒充碰撞控制器。在第一delta下，保持未应用者为identity，单次应用者获得x=1/yaw22.5，故意两次应用同一delta者x=2/yaw45。为避免混合坐标导致歧义，平移用明确父坐标分量相加，旋转只同轴四元数相乘；这验证此固定适配器重复应用的结果，不定义一般3D根运动积分规则。原生getter与Node3D读回是真的引擎观察，不以纯Python矩阵值替代。

每步记录求值编号、调用顺序、参数、两次getter实际向量/四元数、骨局部姿态、父变换与三个应用接收者变换。四元数使用旋转等价/向量作用或绝对dot比较，不把q与-q当不同旋转；浮点容差预先冻结。记录源码/输入/binaryhash、完整stdout/stderr、实际退出码和运行ID，错误/超时不留当前PASS。若构造/初始seek导致预期不成立，保留首次失败并分析，不静默调整到任何输出都能通过。

## 新增价值、风险、停止条件

新增的是“原生提取接口的观察不等于自动移动/破坏式消费”：它直接约束玩法程序和动画系统的运动适配接口，现有4项几何模型没有建立这个事实。

风险：Tree首次求值/RESET路径、骨track格式、初始化与root_motion_local配置、自动处理是否被关停。须先冻结选择root_motion_local=false，避免把本例推广为任意旋转/平移组合；不要测试循环/混合/seek/IK等额外维度。最小无网格骨架足以观察数值，但不是实际足底质量或角色约束验证。

停止条件：目前仅门槛，不执行。获准后只完成上述两配置与独立复核；若API/初始化无法明确辨认，保存错误和源定位，返回受阻，不另造模型充当Godot证明。不得外推Unity/Unreal、真实IK、物理碰撞、联机确定性或自动恰好一次消费。

## 基线纠正（执行前）

21:32 UTC重新读取canonical6492be88对应gamelibrary-publish-rig正文与root-motion README。先前使用gltf旧stage的verification_method已纠正；当前元数据明确4项Python模型+未执行Rig表。README模型范围没有变化。不得把旧stage当作当前已发布基线。
