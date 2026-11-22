# 音游判定时钟：来源与边界

| 主张 | 一手资料与位置 | 边界 |
| --- | --- | --- |
| 浏览器提供同一输出定位在音频上下文与单调性能时间的两种值 | W3C，[Web Audio API 1.0 Recommendation, 2021-06-17, AudioContext.getOutputTimestamp()](https://www.w3.org/TR/2021/REC-webaudio-20210617/#dom-audiocontext-getoutputtimestamp)。contextTime 秒、performanceTime 毫秒；处理首块前可以为 0/0，示例说明以相近点做估算，不能用与 currentTime 的差做可靠输出时延。 | 设备渲染时间仍为估计，不是耳道/显示；上下文时间不是谱面位置。未运行浏览器音频。 |
| 引擎可以用分块读数、距上次混音的时间和驱动延迟估计输出 | [Godot 4.5，Sync the gameplay with audio and music](https://docs.godotengine.org/en/4.5/tutorials/audio/sync_with_audio.html)，Using the sound hardware clock to sync；[Godot 4.6，AudioServer.get_output_latency](https://docs.godotengine.org/en/4.6/classes/class_audioserver.html#class-audioserver-method-get-output-latency) 说明依驱动变化，不宜每帧调用。 | 教程页面标 WIP；借用带版本的估算示例和抖动/回退提示，不宣称所有后端、设备、变速或耳道精度，未运行 Godot 声音。 |
| 输入事件时间可独立于应用出队处理时刻使用 | SDL3，[SDL_KeyboardEvent](https://wiki.libsdl.org/SDL3/SDL_KeyboardEvent) Structure Syntax 与 [SDL_GetTicksNS](https://wiki.libsdl.org/SDL3/SDL_GetTicksNS)。 | 对应 SDL 初始化域的纳秒计数；不是物理触点。纳秒单位不证明实际精度，也不与其他 API 仅靠换单位即可相减。 |
| 同帧的两个输入仍可有不同判定；换音频输出需要新锚点 | [合成时钟试件](../实验/音游的判定与输出时钟/README.md) 与 JSON。 | 手工锚点与偏差，不是实测硬件延迟、设备切换或真实语言运行时行为。 |

调阅日期：2026-11-22。
