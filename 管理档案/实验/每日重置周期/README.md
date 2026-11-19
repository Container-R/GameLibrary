# 每日重置周期：复现实验

[返回正文](../../../GameLibrary/网络与在线服务/在线服务/游戏日历与周期/游戏每日重置遇到夏令时，怎样划定领取周期.md)

Python 3.12.14（系统 tzdb 2026b），本地 SQLite 3.53.1。输入为合成的加州每日 05:00 非付费活动及两个重置钟点异常。

- `check_calendar.py` 用实际 ZoneInfo 转换，直接在同一个时区对象中相减和换 UTC 后相减是不同对照。找未来第一个有效分钟/选重复钟点早一次只是试件政策；只搜索最多三小时，超范围显式报错。历史时区规则随库版本可能不同。
- `check_claim.py` 实际本地 SQLite 内存库，导入与春季日历一致的固定边界。完成、回执、跨期重试、唯一键与故障回滚在同一个单连接示例里运行。未测试并发、分布式消息、系统时钟重同步或真实游戏服务。

```sh
set -e
python3 -B check_calendar.py >/tmp/gl-daily-calendar.json
cmp /tmp/gl-daily-calendar.json calendar-observed.json
python3 -B check_claim.py >/tmp/gl-daily-claim.json
cmp /tmp/gl-daily-claim.json claim-observed.json
```
