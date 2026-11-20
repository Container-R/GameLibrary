# 存档写入代次：SQLite 实验

在此目录运行 `python3 -B probe.py`。无需安装依赖；脚本只使用合成数据、两个 SQLite 连接和运行时创建的临时目录。参考输出使用 SQLite 3.53.1；同版本可用 `python3 -B probe.py | cmp - observed.json` 比较。

比较 `after_takeover_before_new_save` 与 `after_old`，不要只看 `after_new`。前者证实 B 未写新内容时已经接管；后者记录旧写及提前插入的回执是否随回滚消失。`reused_writer_controls` 的三次写入分别测试仅检查名字、检查旧代次、检查当前代次。后三次都回滚，以保证同一起点。

本实验未启动 PostgreSQL；分表锁定读方案以该数据库的文档为依据。

`epoch_limit` 另对照 SQLite 溢出转换：不设上限会转成浮点并在下次加一不变，有界接管先到最大整数、再返回零行。
