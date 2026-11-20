# 原生崩溃符号身份：GNU ELF 试件

宿主 GNU/Linux x86-64，GCC 14.2.0，GNU ld／addr2line 2.44。运行：

```sh
bash elf_probe.sh | cmp - observed.tsv
```

脚本只构建自己的两份同名小型库和分离调试文件，不执行这些库或制造崩溃。固定链接 ELF 虚拟地址 0x6000，使用 GNU addr2line 读取函数和行号，并另用 GNU readelf 区分 ID 相等、冲突和缺失。缺失 ID 对照保留未核实，不宣称是 NDK 识别流程。脚本规范化临时构建路径后在本工具链独立两次输出完全一致；其他平台工具版本和路径可能改变实际 ID 与调试行布局，应保留配对结论和原始输出。

范围不包括 Android、APK 解包、ASLR、原始 tombstone 或生产崩溃。
