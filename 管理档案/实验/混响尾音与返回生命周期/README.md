# 混响尾音与返回生命周期：复现和试听

[试听 WAV](audition.wav) · [源码](probe.py) · [读回与浮点轨 RMS](observed.json)

使用 Python 3 标准库。合成信号，不使用外部采样。复跑：

```sh
set -eu
tmp=$(mktemp -d)
python3 -B probe.py "$tmp" > "$tmp/observed.json"
cmp "$tmp/observed.json" observed.json
cmp "$tmp/audition.wav" audition.wav
```

程序还在输出目录生成七段独立 WAV。每段 1.2 秒，串联间隔 0.25 秒，16 kHz 单声道 PCM16，统一增益，不分段归一化。下列毫秒都是本段内时刻：

1. A 在 110 ms 停止送入，保留返回。
2. 同一干声和混响计算，在 110 ms 将湿声返回归零。
3. 110 ms 开始，用 80 ms 将湿声返回线性淡出。
4. 110–270 ms 静音，但处理继续；重开时没有新输入。
5. 若清空全部 FIR 历史且无新输入，等价波形与 2 相同。程序复用等价波形，不声称调用了引擎重置。
6. 350 ms 开始第二次敲击 B，与 A 共享线性混响返回。
7. 同 6，但从 110 ms 切掉共享湿声返回，两源干声保持原样。

RMS 由 PCM 量化前的浮点轨计算，窗口半开。实际 WAV 样本写入又读回，与所编码的 PCM 逐字比较；试听 SHA-256 为 `080d89e8fb61657ebd68978b5e03fe6d77f9759c2cb42cf703be000ba67274dc`。结论限本合成 FIR；没有测试主观听辨、商业引擎、实际房间或资源保持开销。
