# Godot4.6.3：同路径的新控件不是原 opener

> **身份边界：** 本文版本字符串是本地程序自报；`official` 字样及同机构建复跑不认证官方来源。源文件摘要指原创夹具，不是引擎构建源码。[统一取证说明](../../source-notes/godot-runtime-provenance.md)记录公开标签与自报提交未对应的问题。

这是现有模态焦点恢复方案的窄范围引擎实验，不是 Unity UI Toolkit 集成验证或新的完整模态实现。2026-10-31，实际 Godot `4.6.3.stable.official.7d41c59c4`、Linux x86_64、Python3.12.14；被测可执行文件和四份原创夹具源文件 SHA-256 在 `results/summary.json`。

## 产品契约与可证伪问题

原 opener 表示业务记录A。它被移出场景树后，相同 NodePath 上出现表示业务记录B的新 Button。本产品规则要求恢复原记录身份，否则回到 SafeReturn；**不允许把同路径的新记录当成原目标**。另一个产品若明确允许按业务键重绑定新控件，应实现不同策略，不能照搬实例相等规则。

这里的 Modal 是普通 Control 构成的应用级对话框，不是原生 Window、exclusive popup 或引擎自动导航围栏。实验只处理关闭之后的恢复身份，不验证打开期间的输入隔离。

## 运行

```sh
python run.py
```

运行器先做实际引擎能力门槛，再运行 naive、guarded 各一个独立进程。环境HOME/XDG隔离，禁止 `-O`（实际拒绝记录见 `results/optimized-rejection.txt`），正常路径随后删除旧summary；早期拒绝可能保留历史summary；检查已安装引擎的CLI参数，拒绝超时/非零退出/stderr/引擎错误/缺失或重复结果。失败时不发布成功summary；阶段原始输出写 `.log`。程序不下载引擎。

## 真实调用与观察

1. 三种进程都创建实际 Button。通过 `grab_focus()` 使旧Opener、随后Close取得焦点；独立判据必须看到真实 `focus_entered` 和 `Viewport.gui_get_focus_owner()` 的相应实例ID，不能只记录“已请求”。gate运行还在后续 `_process` 确认Close仍是owner，能力门槛不成立则不继续策略运行。
2. 策略运行将 `restore()` 放入真实引擎 `call_deferred` 队列。在同一同步调用内，移除旧Opener，记录 `is_inside_tree()==false`，再 `queue_free()`，创建同名新Opener。检查新旧ID不同、路径相同，新控件属于活树、树可见且有效focus mode为FOCUS_ALL。
3. 隐藏逻辑对话框；延迟恢复实际执行时重新按路径解析。两种运行都保持 request_revision==revision==1，避免版本守卫抢先拒绝而掩盖身份守卫。
4. naive只按路径聚焦新控件；guarded比较原实例ID，观察不匹配后聚焦SafeReturn。身份拒绝是应用策略，不是引擎自动功能。
5. 读取请求返回时、后续deferred观察回调、以及随后 `_process` 的实际owner；检查严格序号和恰好一次恢复调用。`call_deferred`可能在同帧idle阶段完成，因此不宣称跨过一整帧或模拟网络延迟。

## 已执行结果

三个真实进程均退出0：

| 运行 | 要求并实际观察到的结果 |
|---|---|
| gate | 旧Opener和Close依次真实获焦，后续process中Close仍持焦 |
| naive | 同路径的新记录B真实获焦；相对于本例身份保持契约，预期错误成功复现 |
| guarded | 一次identity_mismatch，SafeReturn真实获焦；新记录B从未获得focus_entered |

独立Python判据比较单进程内实例ID，不要求不同进程ID相同。每个策略结果都同时检查恢复回调顺序、请求版本仍有效、最终owner和真实信号。原始日志及解析结果分别在 `results/{gate,naive,guarded}.{log,json}`；没有把代码中的期望目标当成引擎返回值。

## 能力和证据边界

这使“对象身份不是路径名字”的应用层论点获得了实际 Godot Control/Viewport 行为证据。引擎正常执行了应用请求，naive错误不是Godot缺陷。身份守卫被独立触发；没有同时触发版本过期或作用域不匹配条件。

未覆盖：Unity、实际键盘/手柄或导航事件、按钮点击、视觉焦点样式/对比度/裁剪、读屏、屏幕可见性、隐藏控件申请焦点的全部行为、原生模态窗口、完整导航隔离、多用户、异步多线程、同一实例被重新绑定业务记录的情形。`is_visible_in_tree`只是树状态，不是人能看到的证明。没有验证固定帧率或性能，因此不做无意义的多fps扫描。

旧对象通过remove_child离树的事实已直接观察；queue_free并不立即销毁，本实验不靠“已经释放内存”成立。实例ID是进程内身份，不是存档/网络稳定键。实际生产的可恢复目标仍应结合业务身份、视图代次和新聚焦意图；本夹具只隔离其中一种失效。

## 官方4.6来源

访问2026-10-31，官方版本路径4.6，实际二进制4.6.3单独记录：

- [Control](https://docs.godotengine.org/en/4.6/classes/class_control.html)：`grab_focus`、`focus_entered`/`focus_exited`、`get_focus_mode_with_override`。有效焦点模式可受递归设置影响，不能只读本地focus_mode。
- [Viewport.gui_get_focus_owner](https://docs.godotengine.org/en/4.6/classes/class_viewport.html#class-viewport-method-gui-get-focus-owner)：当前实际Control或null。
- [Node](https://docs.godotengine.org/en/4.6/classes/class_node.html)：`is_inside_tree`、`remove_child`、`queue_free`及延迟删除边界。
- [Object](https://docs.godotengine.org/en/4.6/classes/class_object.html)：`get_instance_id`当前会话身份；`call_deferred`的idle执行与同线程入队顺序。

代码原创，无第三方实现复制；不包含游戏资产。

## 独立复核

[独立审查](review/README.md)在相同环境复制冻结源码，重复能力门槛和两策略共3进程，源码与二进制指纹一致。复核日志在review/fixture/results，不覆盖作者results。作者与复核各3进程是同一组的重复，不是6种场景或跨平台验证。

**调用新鲜度：** [历史摘要与本次退出状态必须分开](../../source-notes/runner-invocation-freshness.md)。早期拒绝可能保留旧成功文件，不能只读 PASS 判断最新调用。
