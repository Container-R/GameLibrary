# Godot 资源身份与路径回退

[返回正文](../../../GameLibrary/%E5%BC%95%E6%93%8E%E4%B8%8E%E5%B7%A5%E5%85%B7/%E8%B5%84%E4%BA%A7%E5%B7%A5%E5%85%B7/%E8%B5%84%E4%BA%A7%E6%A0%87%E8%AF%86%E4%B8%8E%E5%BC%95%E7%94%A8/Godot%20%E8%B5%84%E6%BA%90%E6%94%B9%E5%90%8D%E5%90%8E%E4%BB%8D%E8%83%BD%E8%BF%90%E8%A1%8C%EF%BC%8C%E6%80%8E%E6%A0%B7%E7%A1%AE%E8%AE%A4%E6%B2%A1%E6%9C%89%E6%8E%A5%E9%94%99%E8%B5%84%E6%BA%90.md)

本次在 Linux 上使用 Python 3 与 Godot 4.6.3 stable official，在本目录执行（可用 `GODOT` 指定可执行文件）：

```bash
set -o pipefail
python3 -B run_godot_uid_moves.py | diff -u observed.json -
```

脚本为每个用例在操作系统临时目录下新建自己的项目、缓存、配置与数据目录，分别启动 headless 编辑器导入和独立读取。程序用红色或蓝色的首个渐变颜色标记两个同类型资源，并核对导入没有改写父资源。后两个用例只在临时项目里移除或替换已登记资源，故意造成旧索引；不接触真实项目。其他平台请按各自的 Godot 用户目录规则重新隔离。不执行导出、多个同时持有同一 UID、其他资源格式、初次导入的性能，或 UI 渲染。多数机器每例需要数秒，多个用例串行。
