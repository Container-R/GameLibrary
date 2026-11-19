# Godot 资源 UID 与路径：来源和证据范围

- Godot Engine，[UID changes coming to Godot 4.4](https://godotengine.org/article/uid-changes-coming-to-godot-4-4/)。早期支持、原生资源文件头、导入资源、脚本和着色器的 .uid、未提交 .uid 后路径回退。文中官方例子提到旧路径复用会接到别的资源；以当前实验核对具体 .tres 示例。
- Godot Engine，公开的 [4.6.3-stable 标签所指提交 35e80b3a... 的 resource_format_text.cpp](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/resources/resource_format_text.cpp#L452-L493)。文件中解析 ext_resource：先读文本 path，有登记映射时替换；未登记的相应分支记录无效 UID，之后再启动资源读取。工具版在初次扫描有特定警告抑制，不能仅用警告文本判定所有错误。
- Godot Engine，[ResourceUID](https://docs.godotengine.org/en/4.6/classes/class_resourceuid.html)，4.6，查询登记和路径。
- 二进制自报 Godot 4.6.3-stable (official)，只验证 [附录中的文本资源例](../实验/Godot资源身份与路径回退/README.md)，与源码固定版本分别取证。新版编辑器在特定操作下重写路径的行为不在实验内。
