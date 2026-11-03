# 单顶点几何图：候选隔离生成协议

当前仅准备，不运行第二轮。需主审与独立审查后明确批准执行。

首轮未显式准备环境，见 INITIAL-EXECUTION-LIMIT.md；首轮原件保留，不改写。新轮是不同执行身份，不能追认首轮为合规生成。

## 固定输入与数学

固定同一 generate.py，不修改首轮点、颜色、文字或布局。输入manifest绑定生成器、本协议、外层；manifest自身摘要写回执行结果。生成器计算120度单位圆两端点、等权弦中点和60度旋转结果，assert两距离1/2与1；屏幕X/Y相同每单位260像素，只反转屏幕Y。输出原创SVG和geometry.json。不运行蒙皮或导入资产。

已有点名、坐标、图例文字、圆弧/直弦、半径虚实线区别方法，颜色不是唯一依据。维持既有正文公式与表格作为替代文本；不宣称已测可读性或无障碍达标。

## 执行前门

外层拒绝输入和目录祖先symlink，读取全部三输入并核SHA256。独占新 isolated-runs/<run-name>，拒绝复用；运行根既存也必须0700。新work、private-logs与环境目录均0700，复制全部输入后再核SHA256。

白名单环境只设预定PATH、C.UTF-8 locale、UTC以及新建HOME、所有列明XDG项、TMPDIR/TMP/TEMP；不继承调用者环境。XDG_RUNTIME_DIR为0700。每个目录先实际短文件写入/删除核可写，再开始生成或渲染子进程。预定PATH是源配置，不是采集到的安装位置。

固定两步：
1. python3 generate.py，10秒。
2. inkscape skinning-chord.svg --export-type=png --export-filename=skinning-chord.png，30秒。

只用已有软件，不安装、不查询版本或字体安装路径、不联网。每步Popen(start_new_session=True)，超时SIGKILL整个进程组并wait直接子进程。有限POSIX进程组管理不是安全sandbox，不保证清理主动脱离组的程序。不用当前协议声称已实测超时路径。

## 结果与停止

开始即保存failed回执；复制核对、目录可写、两个命令成功和预期非空SVG/JSON及PNG签名检查通过才标passed。任一步失败保留，不自动重跑。安全回执仅记录输入/输出摘要、实际返回码、输出/错误流是否为空、阶段和通用失败类别；原始日志只留private-logs，不发布绝对路径、PID、主机或字体指纹。SVG 与 geometry.json 由固定生成器输出，PNG 由 Inkscape 渲染；发表前还须核对实际图文件及其元数据，不能单凭生成器推断渲染器输出不含环境信息。

外层成功不是图形视觉验收。随后必须实际看PNG，检查文字可读、点/线/标签位置、边界裁切和几何关系；数学核对与视觉核对各自报告。新轮结果不得覆盖initial-unisolated。公共图示只用最终通过的明确身份；初次限制在历史记录保留。
