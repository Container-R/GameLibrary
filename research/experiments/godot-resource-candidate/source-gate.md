# 资产加载深度门槛：新根对象是否真的隔离了可变依赖？

2026-10-31，来源与当前文章只读检查；未运行引擎、未写夹具、未安装软件或下载游戏素材、未修改主目录/远程。

## 建议执行的唯一问题

**已经持有一份活动资源时，对同一根资源使用 `load_threaded_request(..., CACHE_MODE_IGNORE)` 得到不同根对象，是否仍与活动资源共享外部依赖？若修改候选的该依赖，活动资源是否在“接受候选”之前已经改变？`CACHE_MODE_IGNORE_DEEP` 在同一最小依赖图上是否隔离该修改？**

这不是泛化的旧回调ticket问题，不声称发现引擎竞态缺陷。关键是**对象图所有权**：根对象不同并不推出整个可变图独立；“完成加载后才发布候选”也不能回滚此前经共享依赖造成的改变。候选校验若严格只读，不一定需要深复制；只有要对候选做修正/预处理或允许可变资源时，此边界才直接影响活动内容。

## 与已读内容的差别

实际读取 `gamelibrary-publish-narrative/`：
- `solutions/engine/asset-import-intent-contract.md`：空缓存检出与sidecar缺失改变尺寸，实际测的是磁盘导入意图；没有测运行时多次加载的对象别名。
- `solutions/modeling/gltf-interleaved-attribute-contract.md`：字节跨度与几何意图的契约，未验证引擎加载所有权。
- `solutions/platform/cloud-save-resume-boundary.md` 的Reloading/候选检查：明确建议独立候选；此建议不等于任何资源加载API已替宿主深度隔离对象图。
- `research/source-notes/ink-save-content-compatibility.md`：候选故事实例与内容语义，固定源码分析；本题不重复存档版本或剧情迁移。
- `research/source-notes/godot-runtime-provenance.md`：本地程序与官方固定提交未建立精确构建对应，后续必须保持此边界。

## 实际读取的一手来源

滚动文档： https://docs.godotengine.org/en/4.6/classes/class_resourceloader.html ，读取2026-10-31，4.6系列。

另通过GitHub插件读取以下**固定提交**文件：`35e80b3a8822a9df9be390814b62f44c0a9c69e8`，此前公开4.6.3-stable标签解析结果。下面是本轮实际检查的章节/代码段，不宣称审查整个引擎或以源码代替运行结果：

|固定文件及位置|能支持什么|
|---|---|
|[ResourceLoader.xml 111–138、168–181](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/doc/classes/ResourceLoader.xml#L111-L181)|IGNORE不重用/存储根及内嵌子资源，但外部依赖使用REUSE；IGNORE_DEEP向外部依赖递归传播。threaded_get在未完成时可能阻塞，状态建议跨帧轮询。|
|[resource_format_text.cpp 1432–1453](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/resources/resource_format_text.cpp#L1432-L1453)、[517–519](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/resources/resource_format_text.cpp#L517-L519)|文本加载器把普通IGNORE的外部模式设为REUSE；DEEP则保留递归模式；外部依赖加载明确传入该模式。|
|[resource_loader.cpp 516–538、568–592](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource_loader.cpp#L516-L592)|threaded请求进入_load_start；已有同路径用户token可先被复用。因此本候选实验不并发发起相同路径的不同模式请求，以免混入另一个问题。|
|[GradientTexture1D.xml 12–14](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/doc/classes/GradientTexture1D.xml#L12-L14)|纹理明确引用Gradient属性，能构造有实际资产意义的两层图。|
|[Gradient.xml 21–27、62–69](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/doc/classes/Gradient.xml#L21-L69)|可读取/设置指定点的颜色，适合独立于GPU画面的数值观察。|

这里只转述必要API与分支，没有复制实现或保存整份第三方源码。来源为官方工程同源证据，不算多个独立机构复核。公开固定源码只是语义参照，不能认证已安装程序来自它。

## 拟定的两个真实引擎进程，尚未执行

采用原创 `.tres`：根 `GradientTexture1D` 引用外部 `Gradient` 文件，两个端点明示红与白。无图片、字体、插件、自定义加载器或网络。只读取Gradient点色，不采样GPU纹理或宣称显示结果。

每种模式独立新进程/临时项目：

1. 普通同步REUSE加载根作为活动资源，持续持有根及外部Gradient引用，确认初始颜色为红，记录两层instance ID。不得依赖全局预加载或先前进程缓存。
2. 对同一路径只发起**一次**threaded请求：进程一IGNORE，进程二IGNORE_DEEP；`use_sub_threads=false`。要求请求返回OK。
3. 在帧回调逐次观察状态；只在LOADED后取结果一次。记录真实状态序列，不要求一定观察到IN_PROGRESS，微小资源可能已加载完成；不要靠sleep或大资源制造时间差。
4. 比较活动/候选根与Gradient的真实对象身份，核对两者当前颜色；对候选Gradient调用set_color(0,蓝)，再读取活动Gradient与候选Gradient的颜色。
5. 不把候选赋给活动根、不重写磁盘资源。额外记录活动根引用仍是原对象，源文件摘要未改变，以免把显式发布或磁盘热更新混进来。

**可证伪预期**：

|模式|根身份|外部Gradient身份|只修改候选Gradient后活动点色|
|---|---|---|---|
|IGNORE|不同|相同|蓝：没有发布候选也已受到影响|
|IGNORE_DEEP|不同|不同|红；候选为蓝|

根不同且外部共享是关键反例，不能只检查返回资源非空。若只验证颜色而不检查对象身份，无法定位是共享依赖还是其他更新机制；若只检查身份而不实施有限修改，也没有展示实际影响。两种模式构成同一问题的对照，不扩张成全部缓存模式矩阵。

## 风险、结果解释与停止条件

- 持有两个资源保证测的是活对象共享，不是释放后instance ID复用。所有修改在主线程、加载完成后进行；本例没有并发写数据竞争，不应冠以“线程安全漏洞”。
- 如果 `.tres` 在无头加载中出现错误或资源类型与预期不同，先保存原始诊断，停在能力/夹具问题；不能换成纯Python伪资源后声称引擎验证。
- 帧预算与外部子进程超时仅用于限制实验；不保证能取消所有阻塞的OS调用。不要用测得的完成帧数推导延迟或性能。
- 记录实际二进制摘要、自报版本、Engine版本字典和命令。现有身份记录为SHA256 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`、自报`4.6.3.stable.official.7d41c59c4`，**新运行须重新测，不直接继承**。与公开35e80b3a源码对应仍未知，不认证official字样。
- 完成两个进程及独立原始结果核对就结束。不测试导出包、跨版本、GPU像素、外部文件并发改写、任务取消、加载速度、REPLACE、重复请求合并、任意资源图或内存释放保证。
- 若观察与预期不同，应保留失败判据和实际图身份，返回固定源码/构建差异检查；不改写成成功，也不立即断言引擎bug。

**门槛结论：值得实施这一个有实际引擎对象图证据的窄对照。** 它加强“候选资源必须具备需要的隔离范围”这一交接，而不是再造抽象generation ticket；目前只是源码支持的待验证预期。可以补入现有资产导入/加载边界文章，不以新增文章或目录计成果。
