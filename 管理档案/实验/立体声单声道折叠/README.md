# 立体声单声道折叠：复现实验

[返回正文](../../../GameLibrary/声音与音乐/音频制作/混音/立体声音效折成单声道后消失，先查极性、延迟和路由.md)

[实跑说明](native/README.md)详列 FFmpeg 版本、合成音、折叠矩阵和测量区间。源波形和 WAV 可由脚本在临时目录离线生成；仓库保留可直接比较的 JSON。这里不以响度模型或听众实验验证清晰度，不包括任何真实录音。

```sh
set -e
tmp=$(mktemp -d)
cp native/probe.py "$tmp/"
python3 -B "$tmp/probe.py" > "$tmp/observed.json"
cmp "$tmp/observed.json" native/observed.json
```
