# Resource复制图：来源与证据范围

访问2026-11-01；补充SOL-ENGINE-001，不把已有缓存加载结果重命名为复制实验。

| 原始材料 | 定位 | 范围 |
|---|---|---|
| [Godot4.6 Resource](https://docs.godotengine.org/en/4.6/classes/class_resource.html) | DeepDuplicateMode、duplicate、duplicate_deep、is_built_in、resource_local_to_scene | 官方版本化API文本，不是安装二进制来源认证 |
| [固定resource.cpp](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource.cpp) | _duplicate_recursive、_duplicate、duplicate、duplicate_deep | 比较源码提交35e80b3a8822a9df9be390814b62f44c0a9c69e8；保留脚本与载荷区别，未复制源码 |
| [Godot4.6 @GlobalScope](https://docs.godotengine.org/en/4.6/classes/class_@globalscope.html#class-globalscope-method-is-same) | is_same引用类型说明 | Array引用身份与值相等不同；实际值变化另作观察 |

外部资源与内部子资源的路径政策、STORAGE属性以及重复引用重映射决定此有限图的预期。源码按脚本共享实现依赖处理；不把它解释为所有Resource均无条件隔离。HTML源码打开失败后读取同一固定官方raw源；未使用未经访问的头文件作为已读依据。

执行证据：作者 记录别名 `历史执行记录-01` 与独立复跑 记录别名 `历史执行记录-02` 各一版本进程、三行为进程，按相同冻结协议运行。原始输出与解析 JSON 的关联使用严格类型比较；独立字面检查器不导入作者 oracle。二进制 SHA256 为 `[安装指纹已省略]`，自报版本 `4.6.3.stable.official.7d41c59c4`；仍未认证与比较源码提交的对应关系。协议和完整取证见[实验归档](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/experiments/godot-resource-duplication/README.md)。源码推导与上述有限运行观察分列，不把前者当作二进制身份认证。本文未取得其他引擎、导出包、任意自定义资源或性能结论。原创图和有限变更不来自用户资产；不转载第三方文档图像或完整代码。

> 公开衍生说明：本次仅省略安装位置、安装指纹或执行记录标识，并调整现址/固定历史链接；技术观察、失败、计数与原有证据范围保留。正文中的“本次”及身份相等陈述均属于原记录时点，本轮未重新检验，未运行旧实验，原始摘要声明不改写为新字节。文中描述性记录别名不是可执行目录名。
