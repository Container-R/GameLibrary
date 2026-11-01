# 独立来源审查：生成工具的顺序依赖与失效依赖

2026-11-01。**接受为构建工程角色的短机制补充**。已读现有角色全文和 gate；CI生产输入的案例没有展开工具本身变化如何触发增量重生成，故此接口有实质新增价值。CMake例子须独立标为原创假设，不归给 Cygames。

## 实际核对来源

独立读取官方 [3.31 add_custom_command](https://cmake.org/cmake/help/v3.31/command/add_custom_command.html)（返回标题3.31.12）Generating Files、COMMAND、DEPENDS，以及 [CMP0112](https://cmake.org/cmake/help/v3.31/policy/CMP0112.html)。另读固定官方文档源：

- [Help/command/add_custom_command.rst 102–206](https://github.com/Kitware/CMake/blob/6acf7153156bb45038be62e79a32ed5a6ea2d00e/Help/command/add_custom_command.rst#L102-L206)。
- [Help/policy/CMP0112.rst](https://github.com/Kitware/CMake/blob/6acf7153156bb45038be62e79a32ed5a6ea2d00e/Help/policy/CMP0112.rst)，全文。

独立核对官方 v3.31.12 annotated tag，解引用到 `6acf7153156bb45038be62e79a32ed5a6ea2d00e`。这是固定文档源审查，不是 CMake/Ninja 实现审计或安装版本认证。最初另打开4.2版本页面，不用其版本替代本题3.31.12依据。

## 支持的窄语义

完整 `$<TARGET_FILE:asset_packer>` 在 COMMAND 中建立目标级构建顺序，但不自动给自定义命令建立工具重编触发的文件级依赖。将项目 executable target 放入 DEPENDS 会增加该文件级边，同时提供目标级依赖。CMP0112讨论目录/名称等组件表达式；不得把完整 TARGET_FILE 的结论推广到所有 target 表达式，或说 NEW 政策取消了完整 TARGET_FILE 的顺序依赖。

因此 gate 的“输出已存在，只重编工具且路径/参数/规则表不变”可作条件判别：仅有顺序边不足以保证按工具变化重生成；增加上述文件边修补这一具体失效条件。不能表述成已观察到旧资产、无依赖时绝对不会因任何其他原因重跑，或给出构建速度收益。

## 起草时保留的接收条件

- 同目录、单个 OUTPUT、显式规则表、本机构建可运行的项目 executable；还应说明输出确由被构建的 consumer target 消费。仅声明 custom command 不是无条件执行任务。
- 对工具重编的预期是文档规定的依赖触发语义，不是任意保留时间戳、缓存或外部替换情形的逐字节变更检测证明。
- `add_custom_target` 不是这里有可执行产物的 tool target；不得自动套用相同文件级作用。
- 工具 target 的依赖不自动枚举插件、外部配置、动态读取文件或所有生成输入。保留 gate 对 DEPFILE、多配置、交叉编译和共享输出的排除。
- 干净构建因缺输出可运行，不能单独证明已有输出下的工具失效边；重生成也不证明新资产语义正确。这是原创接收设计，不是已有测试结果。

无阻断问题。建议保留具体 TARGET_FILE/DEPENDS 对照与两类单独变更，而非扩成泛化工具身份表。未配置项目、执行构建、读取运行档案或修改远端/角色。
