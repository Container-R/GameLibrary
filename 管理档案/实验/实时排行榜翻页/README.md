# 实时排行榜翻页：SQL 与响应顺序对照

用 Python 3 运行 `python3 reproduce.py`，对照 [reproduction-observed.txt](reproduction-observed.txt)。试件用 Python 标准库 SQLite 3.53.1，不需要服务器。实时场景由两个完整版本模拟跨页更新，比较偏移、键集和固定版本；同分场景隔离正确的名次窗口、错误的过滤位置与错误的分数加 ID 窗口，并独立测试向前翻页。没有测试 PostgreSQL、Redis、进程并发、保留 TTL 或查询计划。两次 Python 响应模型只测试版本和请求代次的拒收，不模拟实际浏览器或重试去重。

[返回正文](../../../GameLibrary/网络与在线服务/在线服务/排行榜/实时排行榜的快照翻页与同分名次.md)
