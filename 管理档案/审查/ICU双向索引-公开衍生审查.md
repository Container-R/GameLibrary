# ICU BiDi 历史观察投影：独立有限审查

**接受下列最终两文件作为有限历史观察的公开衍生说明。** 不批准原始运行包、receipt、runner或安装身份随附发表，不认证执行真实性，也不将本次静态审查称为新的原生运行。

## 精确最终绑定

审查对象为拟议支持目录`管理档案/支持资料/ICU双向索引历史观察/`：

- `README.md` SHA256：`34d2887a7e707f71ffd91f0f6398e7f4ca6222115f7d254c69451235b88f436b`
- `observation-summary.json` SHA256：`7bfe9ff3e157c2e36821b05f3b2879d895165537bc37d852d9f44ca73f046e0d`

已完整读两份初始候选和最终文件。最终JSON相对初始候选只将status改为`historical_observation_projection`；此状态不是published或运行PASS。README只改配套文件名、修正来源提醒归属并加实际可达的返回正文链接。没有数值/失败/来源扩张。初始JSON与README任务绑定分别为`7e65baaa859e193b922a971eec0b0016ec6385af8b9194eb4b147ad2b3dd1f97`及`9f3b8b2dc024c4d65ff3603eb9e811c18a14d211977df10a2b190119a3421a78`。

## 公开内容与隐私

全文JSON字段及README均未见私有执行目录、环境变量值、PID、逐运行身份、安装库/解释器文件指纹或私有receipt/manifest摘要。实际从两份原记录抽取这些被省略的身份字面量作反查，最终两公开文件中无命中；本报告不复制这些原值或内部原记录位置。此为所选记录的有限反查，不宣称穷尽任意编码数据。

保留的三项源代码摘要实际匹配历史实现文件及两次source manifest；两个original_output摘要实际匹配各自原stdout。它们不是安装二进制摘要，也不是公开衍生JSON自己的摘要。README和checksum_meaning清楚说明原输出内部保留、没有提供公开可下载原包，不能据这些hash重演或验证省略字段；不暗示读者仅有公开投影即可独立认证全部历史执行。

## 实际静态核对

没有导入或运行原runner、consumer、checker，没有加载ICU或查询当前安装环境。仅读取授权的原记录并另写有限静态比较：

- 两份stdout逐行JSON与parsed一致，其记录摘要关系成立；三源文件摘要、原输出摘要、空stderr与退出0声明相符。
- 每份52事件、19attempt/19return、8个严格整数状态0、2个close返回、1加载与版本76.1.0.0吻合。两份重复同2配置，不是4个独特配置或另一个实现。
- 两行输入、选项、map、朴素/ICU输出、长度、n+1容量和终止码元逐字段相符。独立按数组搬运并以严格UTF-16解码重算：补充字符的朴素数组非法、ICU写出数组合法，BMP两者合法。这不是新ICU测试或显示观察。
- 历史source前后和所选文件前后相等布尔声明与原记录一致；未重新读取当前库/解释器。两个map自逆和未调用level getter的限制保留，UTF-16完整不升级为字形/字素/光标/语言/无障碍或引擎正确性。

四份纯mock错误记录实际读取：原首因被覆盖、后续首因保留，以及创建后错误分类/清理尝试修正均为失败退出且没有成功摘要；不并入两份原生成功轨迹。另读归档合成记录每模式11项、字面合成每模式14项，数量与控制/拒绝说明一致。本次未重跑这些测试，也没有把mock信号调用当作原生timeout或cleanup故障注入。

## 原始源码抽查与已修正问题

独立从官方仓库重开固定提交`8eca245c7484ac6cc179e3e5f7c1ea7680810f39`：

- [ubidi.h](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/common/unicode/ubidi.h)1685–1768、2086–2125：visual方向/容量与writeReordered字符完整性。代理项警告位于相邻logical-map说明，不是visual-map条目中同一句。最终README已准确分开。
- [ubidiln.cpp](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/common/ubidiln.cpp)1210–1240：实际visual-map函数的奇数run递减码元索引分支。
- [ubidiwrt.cpp](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/common/ubidiwrt.cpp)178–205：默认逆向写出按字符回退后正向复制码元段。

本次没有重新展开整个Unicode属性/run推导，也没有由固定源码推断历史安装构建身份。原说明对此已有限定。返回链接目标实际存在；不在本审查中冒称重做整本读者文章或真人可用性测试。

没有剩余必须修改项；后续任何数值、失败描述、范围或新增附件变化需重新审查。发表与远端写入仍由主代理负责，本代理没有远端操作或改写原始记录。
