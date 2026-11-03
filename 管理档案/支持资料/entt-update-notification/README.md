# EnTT 普通字段写入与更新通知：三条件观察

一个缓存只监听 `on_update<Speed>` 时，直接改 `get<Speed>` 返回的普通字段，会不会刷新它？一次 `patch` 通知又是否意味着数值真的改变？本包保留固定 EnTT v3.13.2 的小程序、执行前预期与实际观察，用来回答这两个有限问题。

## 实际观察

每个条件各自新建 registry、实体和 `Speed{3}`，构造后才订阅一个同步监听器。监听器记录当前字段并刷新初始为3的缓存。

| 操作 | 字段 | 回调次数 | 回调读值 | 缓存 |
|---|---:|---:|---|---:|
| 普通引用直接赋1 | 1 | 0 | 空 | 3 |
| patch内赋1 | 1 | 1 | [1] | 1 |
| patch内赋3 | 3 | 1 | [3] | 3 |

两次实际尝试各构建一次、运行一次，各输出上述三行。它们是**同操作者、同环境、同输入重复**，不是独立实现或独立复跑，也不是六种条件。两轮外部 runner 退出均为0，正式回执均为pass；构建和原生 stderr、构建 stdout 均为空。原生 stdout 两轮逐字相同。

原始文件保存在 [run-1](run-1/receipt.json) 和 [run-2](run-2/receipt.json)；[外部退出记录](EXTERNAL-EXITS.json)是执行者记录的外层结果，不由消费者推断。每轮目录还保留 native.stdout、native.stderr、build.stdout、build.stderr 原字节。消费者只确认三行匹配；单独 consumer_only 结果不能替代外部退出和最终回执。

[协议](PROTOCOL.md)是执行前冻结快照，开头“尚未执行”记录的是当时状态，不是本README的当前结果。未将旧协议追改成事后成功说明。固定输入清单 SHA256 为 `65186c150b7bd98a96dcec89a6c9395d597a605395e7f56e5bc6a33b5f1740aa`。

[独立结果审查](RESULT-REVIEW.md)已核对两轮原始观察与输入身份，但审查者没有再次运行原生程序。报告引用的[执行决定](EXECUTION-DECISION.md)现随包原字节提供；本包仅附已列明的公开输入、流与回执，不冒充包含完整运行目录。

## 来源与准备

固定官方提交为 `78213075654a688e9da6bc49f7f873d25c26d12c`。见 [UPSTREAM-SOURCE.json](UPSTREAM-SOURCE.json)、[源码审查](SOURCE-REVIEW.md)和保留原字节的 [MIT许可证](source/LICENSE)。源码审查公开副本只省去内部选题稿定位；仍是执行前来源结论，不伪称运行记录。

本包**未附上游大头文件和已编译程序**。复现前，从下列固定官方链接取得原始头，保存为包内 source/entt.hpp，不能用随版本滚动的最新文件替换：

- [官方单头](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/single_include/entt/entt.hpp)
- [原始字节下载](https://raw.githubusercontent.com/skypjack/entt/78213075654a688e9da6bc49f7f873d25c26d12c/single_include/entt/entt.hpp)
- [官方许可证](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/LICENSE)

头文件 SHA256 必须为 `31be51708c7325ecb7877182fa9ee68a20fb2121ce6bcd6c1687506f0fb1c8b5`。可用 `sha256sum source/entt.hpp source/LICENSE` 对照来源清单，再用 `sha256sum INPUT-MANIFEST.json` 对照上面的冻结身份。runner还逐项检查清单全部输入。PUBLIC-MANIFEST.json列出本包实际附带文件，不会把省略的头冒充已经附带。

## 复查与复现

先复制本包到自己的新工作目录；不要在历史观察目录中原位运行。下面命令均从这份工作副本根目录执行。离线复查已有三行不需要编译或补头：

```
python -B checker.py run-1
python -B checker.py run-2
```

若自行选择重新运行，先准备上述固定头、Python 3与支持C++17的编译器，以及支持进程组的POSIX环境；本单元没有跨平台验证。新目录名必须不存在：

```
python -B runner.py reproduction-1
```

不要用-O启动runner。它每次最多一个60秒构建和一个10秒原生调用，构建诊断即停，不自动更换编译选项或重试。编译argv、五位置清环境和有界收尾见协议。准备失败不等于原生条件失败；现有观察不保证别的工具链也无诊断。没有网络追踪、性能或沙箱保证。

## 执行前发现与有限纯测试

[v1拒稿](PRE-REVIEW.md)保留三个纯mock发现：只等leader未确认组消失；修改后的复制checker会先被导入、后被拒绝；构建期间修改输入清单未被发现。第二项不是错误PASS，而是身份门太晚；第三项的pass只发生在模拟路径，不是实际EnTT观察。

[v2闭合](PRE-REVIEW-v2.md)记录修订：有限组消失检查、导入前全部输入检查、清单原字节前后绑定。fixture、字面预期和checker未因结果调整。原版输入位于 history/v1，v1见证脚本与输出放在其 independent 子目录，使相对导入指向旧实现；它们不应拿来当v2成功回归。

历史实际纯测试为：v1普通模式7方法，-O仅消费者1方法；v2普通模式8方法，-O仅消费者1方法。输出中的模拟PASS不是原生结果。原始脚本和输出均保留，没有在打包时重跑。

若要自行复查纯测试，需先补固定头；v1还需将同一已核头复制到 history/v1/source/entt.hpp。以下命令仅运行mock/解析测试，不应启动编译器或fixture：

```
python -B independent/test_preexec_v2.py
python -B -O independent/test_preexec_v2.py Review.test_literal_and_rejections
python -B history/v1/independent/test_preexec.py
python -B -O history/v1/independent/test_preexec.py Review.test_literal_and_rejections
```

旧协议中的内部选题稿名仅属历史编辑背景，不是本包复现依赖；当前协议已改为包内来源入口。审查报告中初版 pure 输出路径按本包布局应在 history/v1/independent 查找，v2输出仍在 independent。不把历史文档中的旧路径当未附带的公开链接。

## 边界

本例只观察默认storage、普通int字段、一个正常返回且不重入的监听器。没有测试线程、异常、销毁、定制storage或业务级缓存维护。直接写导致缓存仍为3是这个示例所选通知政策的后果，不是EnTT自带缓存出错；patch通知也不是数值差分检测。两轮不能证明任意游戏缓存一致、所有版本行为、编译产物身份或长期运行可靠性。

[返回：改了组件字段，为什么缓存还没收到更新通知](../改了组件字段，为什么缓存还没收到更新通知.md)

此返回链接按最终支持资料目录布局设置；孤立复制本包时不含该相邻正文，最终整合后需另核其可达性。
