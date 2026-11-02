# EnTT v3 新环境流程：独立结果审查

2026-11-02。**接受已审v3输入下的这次有限观察记录。** 主写入者执行一次runner，内部两次新副本构建、两次新native。本审查者只读取记录及重新运行消费者，没有重新调用compiler、runner或native；这是独立结果审查，不是独立操作者原生重跑。

## 精确绑定

- INPUT-MANIFEST：`a2d2d8ac37ca11278e737434549c90ee86f5d94047d8ce2f94ea036f28665b20`
- PROTOCOL-v3：`1ead0f47acd33b85dfac79dd759cae9cd5f33b66d89bcaa4bba0d857f56760db`
- runner：`9054b515ae12a6f69253ec2f47c1ecc20c7e1c11b22a6c06c4e88c33a3ff3021`
- fixture：`5bc3b3ad0ffdc2d22e6c11083ce92c60dccbaf1be149a3745c165ce62fa0463f`
- 两份原始输出 `observations/repeat-1/native.stdout`、`observations/repeat-2/native.stdout` 均为 `504bdd9c35c4bd06a9c589e14c662206ce87768c316495559b299172aa2b3843`，各8行。

完整读两份原始8行与receipt过程/输入记录。独立逐项重算11输入与manifest自身，匹配记录的before/after；两副本各3复制输入及产物本地摘要、四过程stdout/stderr摘要均与前后记录相符。产物摘要只在本地核对，不在本报告列出。固定argv与已审runner字面值相同；过程顺序确实为第一副本build/native、第二副本build/native。

两次build返回0且stdout/stderr空；两次native返回0且stderr空，均无超时。两份stdout实际逐字相同，也与保留的两份v2 stdout逐字相同。普通Python和-O分别对这两份现存原始输出运行已审checker并复核绑定，均接受；这不增加原生执行次数或案例。

## 五键环境证据的精度

四个process记录均为 `VALIDATED_BEFORE_LAUNCH` 与 `environment_cleanup=REMOVED`，组清理记录为 `NO_GROUP`、leader为 `REAPED`。结合冻结runner/helper已审控制流，这些是各阶段准备五键、临启动验证及清理完成的当次记录。实际检查目前四个phase环境根均不存在，包括没有遗留同名符号链接。

这不是本审查者重新观察过去目录存在的瞬间；当前根已删除也不能独立证明过去所有目录或进程写入行为。没有系统调用跟踪，不声称完整文件系统/网络隔离、所有后代退出或零网络调用。helper仍只是五个选定可写位置的有限准备与检查。上述保留条件不影响此次记录符合已审v3控制流程的有限接受。

## 实见的四阶段机制

typed archive为 uint32计数1、uint32活跃数1、entity来源完整值0。来源和seed在不同注册表中均为完整值0，各阶段始终有效；相同整数不表示跨注册表同一对象。

| 阶段 | map完整值 | contains | 目标valid(map) | 活跃数 | 已保存initial的当前有效性 |
|---|---:|---|---|---:|---|
| before_load | 4294967295（null哨兵） | false | false | 1 | 尚未保存 |
| loaded | 1 | true | true | 2 | true |
| externally_destroyed | 1 | true | false | 1 | false |
| reloaded | 1048577 | true | true | 2 | false |

销毁后仍非空的map=1是旧完整句柄，不代表有效。第二次get重新消费同一归档3项，restore后返回索引1/版本1的1048577；旧索引1/版本0的1仍无效。没有因map查询本身重建对象。两次get的消费数均3，其余阶段为null。此结果对应已审官方源机制，不推组件引用迁移、snapshot_loader、版本绕回、跨机结果、产品存档兼容性或业务权限。

## 计数与历史处置

- **v3新增**：2次构建入口、2次native fixture，单一四阶段条件重复两次；不是2个不同配置。
- **v2保留历史**：原2次构建、2次native真实存在，但遗漏当时规范五键中的四键，流程不符合仍成立。
- 因而两个版本合计发生4次构建入口、4次native，但不得写成4次均按v3环境流程执行，也不得以相同输出抹掉v2不符合。
- 本轮独立结果审查新增构建/native均为0。Python普通/-O仅消费现有输出，不计原生重复。

相对记录路径是本地证据定位，不声明已公开。没有更改旧记录、stage或远端；公开派生仍需另行安全审核，不自动上传产物身份或全部receipt。

## 公开路径衍生说明

本副本仅把两处原始输出定位由 observations-v3/repeat-N 改为本包 observations/repeat-N，原流字节不变；另增加本说明。原独立报告 SHA256：`e58b3205c8385c249b1e7af8dc2c6e5c3e566ce8416f94e57b3164062ca17f2b`。报告末尾未公开陈述是原审查时点；本副本不提供新的发布或执行回执。
