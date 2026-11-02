# Chromium行内昵称隔离：四行本地观察提案

2026-11-02，**未执行，待独立协议/代码审查及主编另行授权**。这是一次浏览器观察的草稿，不属于已完成ICU观察，也不证明完整多语言排版。现有Chromium据主编自报155.0.8059.79、Python Playwright已存在；作者未探测/启动它们。实际版本只允许在获准观察中记录技术自报，不认证安装来源。

## 要观察的唯一问题

同一LTR模板 `Player {name}: 12 points`，昵称原始逻辑字符串在未隔离与bdi隔离两种结构中不变，但数字与应用冒号的位置可能不同。昵称仅两个合成值：希伯来字母U+05D0/U+05D1/U+05D2（אבג）和ASCII Alex。无真实用户、换行、方向控制字符、FSI封套或攻击文本。

四行固定顺序：he-raw、he-bdi、ascii-raw、ascii-bdi。raw为普通inline span且unicode-bidi:normal；隔离为bdi dir=auto且unicode-bidi:isolate。每行方向ltr，页面1000×500 CSS像素、device scale1，Arial,sans-serif声明、24px/1.6、nowrap、白底黑字。字体声明不保证具体字体已安装；不得下载字体或调整字体追逐预期。昵称及尾部均由JS textContent写入，不把输入拼成HTML。

## 冻结预期（不是观察结果）

W3C指导的Spillover effects/未知方向片段说明提供隔离动机。结合普通强RTL字母、随后数字与中性分隔的方向规则，提出下列可失败假设；不认领已查看指导嵌图或浏览器渲染：

|行|DOM逻辑文本|从左到右的三个片段预期|
|---|---|---|
|he-raw|Player אבג: 12 points|数字12、冒号、昵称|
|he-bdi|Player אבג: 12 points|昵称、冒号、数字12|
|ascii-raw|Player Alex: 12 points|昵称、冒号、数字12|
|ascii-bdi|Player Alex: 12 points|昵称、冒号、数字12|

用DOM Range分别取得昵称、冒号及数字的矩形；每个矩形必须有限且非空、三者垂直区间重叠，横向满足表中不重叠次序。两个同昵称行textContent逐字相同，字符本身不得反转或插入控制符。相邻边界可相等，不规定像素坐标或字宽。另记录computed direction/unicode-bidi与声明字体，不把Range当glyph正确性认证。

保存四行整页截图，人工必须实际查看：四行可辨、无缺字框/截断、希伯来昵称保持正常呈现而非人为逆序、冒号和数字的位置与表一致。机器几何满足最多标为AWAITING_VISUAL_REVIEW；人工通过另写带截图/观察摘要hash的审查记录，不修改原输出。若假设不成立、缺字、沙箱不支持或截图不可判，失败/不足即停止；不修oracle追随结果。

## 环境和单次执行形态

未来获单独授权后，命令形式为 `python runner.py NEW_DIRECTORY`；目录必须不存在，重试或另一操作者执行必须另建目录，不能复用旧结果。单次最多一个worker、一个Chromium persistent context、四行条件、一次截图，无自动重试。程序查找已有chromium而不安装，不额外调用版本探测命令。

从已审五键helper原字节复制isolation.py。supervisor创建专属environment根并prepare HOME/XDG_CACHE_HOME/XDG_CONFIG_HOME/XDG_DATA_HOME/TMPDIR，Popen前validate；worker继承后再核，browser launch前再次核。profile与browser-cache新建于同一拥有根。worker所在组由supervisor拥有，正常或失败均有限清理；leader已退出也不跳过组清理。根创建失败不得启动；部分子目录创建失败仍清理自有根；进程收尾未确认则保留根并失败，不假称已删除所有后代。五键不是文件系统sandbox，也不能证明所有程序写入只在这些目录。

必须 `chromium_sandbox=True`，不传--no-sandbox、不退回无沙箱运行。浏览器启动20秒，普通页面操作10秒，worker整体70秒；组清理后leader等待最多10秒，另用至多3秒确认该进程组已不存在。信号发送、leader回收和组消失分别记录；无法确认或检查出错则保留环境根并失败。该检查不保证脱离组的后代已退出。沙箱失败记录安全错误类型并停止，没有放宽路径。

fixture无网络资源，CSP default-src none，页面通过set_content注入本地审过的固定HTML；browser context offline且service_workers=block，route("**/*")全部abort。任何捕获到的页面请求使本条件失败，仅记录计数不记URL。此为页面资源拦截，不是操作系统网络隔离，也不能以计数0证明浏览器进程完全没有网络调用；没有测试外部服务。无下载/扩展/用户profile/凭据访问。

## 记录、首错与发布边界

INPUT-MANIFEST绑定协议、HTML、runner、helper，运行前后检查同字节。已有before时，无论成功、观察不符、异常或超时，收尾阶段都尽可能记录after及清单字节身份，并标明未变、变化或核验失败；缺失文件也是核验失败，保留最初错误而另记后置问题。没有取得before时明确未开始，不伪造after。正式receipt先写pending正常关闭再同目录rename；pending不是结果，不声称断电持久性。正式机器状态只能FAIL或AWAITING_VISUAL_REVIEW。新目录拒绝复用，失败不保留旧PASS。观察失败时尽可能保留已测行与截图，不伪造未执行行；异常只记安全类型/预定义原因，不保存含主机路径的浏览器traceback。子过程原始stderr被抑制，代价是失败定位有限，不能据空公开诊断说浏览器没有诊断。

公开允许：源输入hash、输出和截图hash、相对文件名、技术版本字符串、逻辑文本、矩形、环境校验/清理状态。不记录实际五键映射、进程身份、主机名、安装或编译产物指纹。准备时未运行任何fixture、浏览器或模型；未生成运行回执。

本次不验证字体塑形、所有Unicode、所有浏览器/原生游戏组件、输入法、玩家身份、安全封套或纯文本控制符策略。相对位置观察也不证明文案易读或无障碍合格。

## 实际读取的来源

- 既有GATE及规范五键段，已审isolation.py完整原字节；不修改其历史。
- [W3C Inline markup and bidirectional text in HTML](https://www.w3.org/International/articles/inline-bidi-markup/)，2026-11-02重读Quick answer、Spillover effects、If you don't know the direction of the phrase。未查看来源图像。GATE固定UBA rev50为既有算法背景，本稿不宣称重读整个UBA。
- [Playwright Python BrowserType](https://playwright.dev/python/docs/api/class-browsertype)：launch_persistent_context的chromium_sandbox默认false，故显式true；env和executable_path说明。自选安装Chromium兼容性不保证。
- [Playwright Python BrowserContext route](https://playwright.dev/python/docs/api/class-browsercontext#browser-context-route)：页面请求路由及Service Worker不被该路由覆盖的限制，故明确block；不当作系统网络防火墙。两API滚动文档本次读取，非固定安装版本认证。
