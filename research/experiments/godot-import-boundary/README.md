# 干净检出：可重建的是缓存，不是丢失的导入配置

本夹具针对Godot4.6.3资产交接的一个具体失败模式：把资产旁的`.import`误当成`.godot/`缓存一起忽略，可能仍能加载场景，却改变导入纹理的语义。代码与16×8矩形SVG均原创，无字体、外链、插件、下载或第三方资产。

## 运行及输入边界

```sh
python run.py
```

运行器使用已安装的Godot编辑器构建，先检查`--import`等CLI选项。实际版本、二进制SHA-256、平台、Python版本、种子文件/运行器hash见`results/summary.json`。每个引擎调用的完整命令与隔离HOME/XDG目录记录在`*-command.json`，原始stdout/stderr记录在同名`.log`。禁止-O；每轮先移除旧成功summary，超时、非零退出、stderr、ERROR或判据失败均不能生成成功summary。

`seed/`是原创最小输入：SVG、项目、场景和探测脚本。程序在临时工作目录生成元数据，不把本机旧`.godot/`带入测试，也不改动种子。`results/configured-inputs/`保存经真实引擎导入后冻结的完整配置输入，包括`asset.svg.import`和`probe.gd.uid`，可核对交接清单；它不是待复制的`.godot/`缓存。

## 参数来源与基线生成

官方4.6 [ResourceImporterTexture.svg/scale](https://docs.godotengine.org/en/4.6/classes/class_resourceimportertexture.html#class-resourceimportertexture-property-svg-scale)定义默认1.0为原设计大小，较高值产生更大图像。使用明确宽16、高8的SVG，配置2.0作为资产交付意图。

1. 种子项目实际`--headless --import`生成合法sidecar，保存为`baseline-default.svg.import`。
2. 运行器只将唯一一行`svg/scale=1.0`替换成2.0；替换次数不是1则失败，避免猜测配置格式。修改前后文件均保存。UID/remap/其他参数不手工编造。
3. 删除临时基线的整个`.godot/`（不是用户工程），保留源文件和sidecar，再导入。实际加载纹理必须是32×16才接受基线。
4. 基线顶层输入文件复制到两个独立项目目录。两边初始都无`.godot/`；kept保留完整输入，omitted只少`asset.svg.import`，其他文件内容hash相同。脚本`.uid`在两边保留，不混入第二种失效。

清理临时基线缓存只用于确保导入参数真正应用，不是建议随意删除团队项目元数据。

## 两个受控案例与独立判据

每个案例一次真实导入加一次新的运行进程；此前还有两次基线导入和一次基线加载。导入与运行分开，避免内存ResourceLoader缓存掩盖干净检出差异。

| 案例 | 导入前 | 重新生成的配置 | 直接加载纹理 | 场景Sprite2D.texture |
|---|---|---|---|---|
| kept | 空缓存，保留scale2.0的sidecar | scale2.0 | 32×16 | 32×16 |
| omitted | 空缓存，只遗漏该sidecar | 默认scale1.0 | 16×8 | 16×8 |

两边实际资源均为`CompressedTexture2D`，`resource_path`均为`res://asset.svg`；场景依赖包含该路径，并且场景实例上的纹理与ResourceLoader返回资源一致。判据读取实际资源宽高，不仅解析`.import`参数或检查`.ctex`存在。两边都成功加载正是本例的重要结果：可加载不等于正确复现资产意图。

输入证明见`kept-initial-manifest.json`与`omitted-initial-manifest.json`：运行器要求差集恰好一个`asset.svg.import`，所有共同输入hash相同，导入开始前缓存目录不存在。运行器也要求导入后存在生成`.ctex`，但不比较缓存文件的字节hash。

UID作为单独观察：加载时读取实际sidecar UID，检查ResourceUID登记及源路径映射；kept必须保留基线UID。omitted不要求UID变化。此次记录中两边UID相同而尺寸不同，说明**UID相同也不是导入语义一致的充分条件**；这不是所有资源、路径或版本的UID生成保证。

## 实际执行与解释

2026-10-31实际Godot`4.6.3.stable.official.7d41c59c4`，Linux x86_64，Python3.12.14。基线与两受控案例均通过上述判据。初次完整执行成功后，补充每次调用命令/环境的归档记录，再执行相同两案例；最终manifest对应附带命令证据的运行器。未引入额外参数扫描或GPU测试。

错误假设“只提交SVG与场景就能恢复原来的非默认导入设置”被本反例否定。正确案例从无缓存开始重建并满足原有纹理语义，说明在该具体资源与工具版本中，无需提交旧缓存即可恢复；**并非证明所有导入器都跨版本或跨机器完全可复现**。

## 资产交接/CI可用检查

建议把交接验收拆成三项，而不是只问项目能否打开：

1. **输入完整**：原资产、原生场景/资源、项目配置、实际需要的导入sidecar和UID元数据；有自定义导入器时还需插件/工具版本。清单应明确哪些是受控输入，哪些是生成产物。
2. **干净导入成功**：在不携带作者缓存的新目录中，使用明确版本执行编辑器导入；保留错误和警告，不把普通运行程序当成导入阶段。
3. **关键语义保持**：按资源类别检查纹理尺寸/导入类型、场景引用、动画轨道或音频参数等真正影响工程行为的属性。只有本例纹理尺寸和引用已实测，其他类别是建议的扩展验收项。

官方建议提交`<asset>.import`而不提交`.godot/`缓存。某些源资源还使用旁置`.uid`，原生场景资源可能在文件头保存UID；不能一条`*.uid`忽略规则全部丢弃。此夹具保留脚本UID，不声称已复现丢失脚本UID的后果。

## 明确不覆盖

无GPU渲染、截图或像素质量判据；headless中能加载资源并读取尺寸，不等于真实画面/显存性能验证。无导出包、LFS/网络获取、跨机器、跨Godot版本、VRAM压缩、DCC、自定义导入器或并行构建；不保证缓存逐字节相同。没有移动/重命名资产，也不测试UID fallback失败，不能推导“删sidecar必然断引用”。场景使用路径引用以隔离参数丢失。

临时目录路径可因运行改变；不要求不同运行的随机或派生元数据完全相同。比较的是同一批次两副本的受控输入差异及实际资源语义。

## 官方出处

访问2026-10-31，目标文档4.6：

- [Import process](https://docs.godotengine.org/en/4.6/tutorials/assets_pipeline/import_process.html)，Files generated：保留导入sidecar、生成缓存及自动重新导入；ResourceLoader访问边界。
- [Version control systems](https://docs.godotengine.org/en/4.6/tutorials/best_practices/version_control_systems.html)，Files to exclude：4.1及以后缓存忽略建议，不能套用3.x/4.0。
- [ResourceImporterTexture](https://docs.godotengine.org/en/4.6/classes/class_resourceimportertexture.html)，svg/scale：参数语义。
- [ResourceUID](https://docs.godotengine.org/en/4.6/classes/class_resourceuid.html)，has_id/get_id_path/create_id_for_path：映射观测及不能假定所有重生UID随机变化。
- [ResourceFormatLoader](https://docs.godotengine.org/en/4.6/classes/class_resourceformatloader.html)，_get_resource_uid：sidecar UID的格式边界。
- [Texture2D](https://docs.godotengine.org/en/4.6/classes/class_texture2d.html)，get_width/get_height：实际尺寸读取。
- [Command line tutorial](https://docs.godotengine.org/en/4.6/tutorials/editor/command_line_tutorial.html)，--import：等待导入结束后退出。安装二进制的--help另有记录。

## 独立复核

[独立审查](review/README.md)在相同二进制和机器复制冻结输入，完整重跑基线及两个案例：4次实际导入、3次实际场景/资源探测。五份源码及引擎哈希一致，唯一初始文件差异和尺寸结果复现。复核输出单独保存在review/fixture/results，不覆盖作者结果；重复运行不扩大案例种类或平台范围。
