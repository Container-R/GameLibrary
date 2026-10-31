# 同路径未收取请求：第二次cache_mode是否建立了独立加载？

2026-10-31，只读来源门槛。未创建/执行新夹具，未修改主目录或远程。

## 结论：源码支持一个实质且不同的可证伪问题

固定官方源码显示：**同一原始路径字符串已有用户加载token时，新的threaded请求递增用户引用计数并直接返回旧token，没有比较或重新应用新cache_mode。** 该路径不要求任务仍在工作；结果已LOADED但尚未get收取时，也会走同一分支。因此应称“未收取请求的合并/复用”，而不是未经证据就称“两个worker同时竞争”。

这不是文档对所有版本的永久保证，也不是本地二进制已认证执行该源码。当前仅通过控制流建立待测预期。

## 实际读取的来源与精确分支

通过已授权GitHub插件重新读取 `godotengine/godot` 的固定提交：
`35e80b3a8822a9df9be390814b62f44c0a9c69e8`。
文件 `core/io/resource_loader.cpp`，定位如下（未复制实现）：

|位置|直接支持的局部事实|
|---|---|
|[516–518](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource_loader.cpp#L516-L518)|公开request把参数传给_load_start；返回token有效则OK。|
|[521–538](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource_loader.cpp#L521-L538)|按p_path查用户token；存在则user_rc递增并复用。新token初始user_rc=1。|
|[566–583](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource_loader.cpp#L566-L583)|路径验证后，用户token复用提前返回；没有在此分支核对新type_hint、cache_mode或子线程设置。|
|[601–625](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource_loader.cpp#L601-L625)|只有走到新建任务才保存本次参数；REUSE已有缓存可直接建立LOADED任务。|
|[697–719](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource_loader.cpp#L697-L719)|status先找用户token；没有token时INVALID_RESOURCE，不能解释为所有已取得Resource引用都失效。|
|[742–760、791–806](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource_loader.cpp#L742-L806)|get取得结果后递减user_rc；减至0才移除用户路径登记。|
|[818–836、907–912](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource_loader.cpp#L818-L912)|完成路径从token对应任务取resource；没有按第二个调用方重建独立策略。|

同时实际读取[Godot4.6 ResourceLoader公开文档](https://docs.godotengine.org/en/4.6/classes/class_resourceloader.html)，定位load_threaded_request/get/status和CacheMode。文档说明按路径取状态/结果、未完成get可能阻塞、各cache模式含义；当前这些方法段**没有明确承诺同路径重复请求获得各自独立模式、独立句柄或自动策略升级**。不能把源码现象称为违反了不存在的文档保证。

源码中的user_rc不是Resource本身所有者总数；收完请求登记与释放所有已获得资源不是同一件事。也不从原始p_path键推导不同写法/UID路径别名的行为，本轮只用完全相同路径字符串。

## 与刚完成的所有权实验有何不同

已读 `research-drafts/godot-resource-candidate/README.md` 与run.py/main.gd：前实验每进程只发一次请求，正确隔离IGNORE与IGNORE_DEEP的对象图语义。这里检查的是**调用方请求的政策是否真正生效**。即使选择了正确的DEEP参数，如果它被合并进旧REUSE请求，调用方也不能仅凭返回OK批准“这是私有候选”。

因此建议不再重复红/蓝依赖修改，而缩成原生Gradient根对象的身份测试。它回答“谁拥有这个未收取请求及其策略”，而不是再次回答“根新不等于依赖新”。

## 最小实际引擎方案（待批准，未执行）

两个隔离新进程，同一个原创二点Gradient `.tres`；先同步REUSE取得活动Gradient并一直持有。

- **进程A**：第一次threaded请求REUSE，跨帧观察至LOADED但不get；随后对完全相同路径第二次请求IGNORE_DEEP。
- **进程B**：第一次IGNORE_DEEP，跨帧观察至LOADED但不get；随后第二次REUSE。

两者只改模式顺序，type_hint相同、use_sub_threads=false。故意等到首个请求已LOADED，再发第二个，消除“必须worker正在运行才发生”的错误解释。不强求IN_PROGRESS样本，不用sleep或大资源制造时序。

按源码预期，两次请求都返回OK。随后记录状态，get第一次并持有R1，记录状态，get第二次并持有R2，再记录状态。预先冻结验收：

|观察|A：REUSE→DEEP|B：DEEP→REUSE|
|---|---|---|
|R1与R2|同一活对象|同一活对象|
|二者与活动Gradient|同一对象|不同对象|
|第一get后状态|LOADED，仍有一次未收取登记|LOADED，仍有一次未收取登记|
|第二get后状态|INVALID_RESOURCE，无该路径用户请求登记|同左|
|活动、R1、R2持有引用|继续可读原始点色|继续可读原始点色|

不必故意第三次get制造错误；不做第三次加载或释放时机实验。这里get次序也不对应“分别取回第一个调用方与第二个调用方的独有ticket”：公开接口只有路径，返回的归属是实验需要辨明的问题。

通过应同时要求实际请求返回值、真实状态序列、同进程非零整数对象ID/精确相等、资源类型与原始点色、磁盘字节未变化。请求/get计数应在实际调用点递增，避免只有预设常量。保持所有资源活引用，禁止用跨进程ID或有损JavaScript Number比较来制造相等/不同。

## 可以形成的工程建议，而非供应商默认承诺

若观测吻合，一个加载broker不能只把“路径相同”当作调用方隔离需求相同。建议先归一化并审查请求政策，发现冲突时明确拒绝、排队至前一组请求收取完成，或由单一broker统一拥有请求并分发已声明的共享结果。**只把应用层字典key改成(path,mode)仍不够**：若仍同时向这个按原始路径合并的API提交，底层不会因此产生两个模式独立的用户token。

上述是原创建议，尚未实现或验证broker。不能推导所有资源加载器都按first-request-wins，也不能证明取消、重试、错误token或不同路径别名的处理。

## 风险与停止条件

- 固定源码与当前安装程序的精确对应仍未确认；新实验需重新记二进制摘要与Engine自报，不能由official字符串认证。既有本地SHA为f64d4ed1…，仅作比较，不代替新测量。
- 每进程一个明确完成的首请求与一个未收取重复请求；只有最终两个get。无真实worker并发要求，无吞吐/延迟、GPU、内存泄漏或线程安全结论。
- 若本地行为不同，保存失败与状态，先检查实际请求顺序/参数/源码身份；不要修改预期冒充通过，也不立即断言引擎bug。
- 完成两个进程和独立原始身份/状态核对后结束；不扩展成重复次数压力测试或全部cache模式矩阵。
- 当前阶段停在本门槛，等待批准。若执行，应补入现有资产加载文章的“请求所有权”一节，而非增加泛化资源管理文章。
