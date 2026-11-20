# 原生崩溃符号身份：来源记录

- GNU [GDB Separate Debug Files](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Separate-Debug-Files.html)：同一产物的 original／stripped／split debug 可保留相同 Build ID。[GNU ld --build-id](https://www.sourceware.org/binutils/docs/ld/Options.html#index-_002d_002dbuild_002did) 将链接身份与当前文件字节校验和区分。
- NDK 固定 [c148270 的 ndkstack.py](https://android.googlesource.com/platform/ndk/+/c1482703cfcfcd6127acfc2e97b8e0428a0149a3/ndkstack.py#155)：155–169 是直接 ELF 双方有 ID 时的冲突拒绝和缺失时的同名回退；185–205 APK 条目由容器偏移选取；731–753 把帧 PC 分开送入符号器。不推广到所有候选路径或版本。
- AOSP 固定 [2156447 的 Unwinder.cpp](https://android.googlesource.com/platform/system/unwinding/+/215644709bd7bbda4c05a9db4d55e96be61bcf64/libunwindstack/Unwinder.cpp#309)：原生帧里的 rel_pc、ELF 起始偏移和可选 Build ID 有不同含义。
- Android [Include native symbols in your release build](https://developer.android.com/build/include-native-symbols) 与 [ndk-stack](https://developer.android.com/ndk/guides/ndk-stack)：函数与文件行号覆盖、未剥离库及 ABI。
- [自制 ELF 反例](../实验/原生崩溃符号身份/README.md)：Linux GNU 工具实际运行；不是 NDK、真实崩溃或 APK 行为测试。
