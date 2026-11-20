# Android 音频焦点：来源记录

- [Android Developers: Manage audio focus](https://developer.android.com/media/optimize/audio-focus)，2026-11-20，焦点管理原则、Android 12+ 和 Android 15 target SDK 要求、系统自动 duck 条件、Android 8–11 请求与回调示例。确认请求返回和听感不是同一状态；永久丢失后不要用旧回调恢复。以前台服务限制解释失败原因，不建议借服务规避产品前后台策略。
- [Android Developers: AudioFocusRequest](https://developer.android.com/reference/android/media/AudioFocusRequest)，2026-11-20，检查申请/放弃对象、延迟授权、监听器和自动压低语音例外。
- [原创模型](../实验/Android音频焦点状态/README.md)：焦点会话标识和命令修订号是应用侧实现策略，迟到事件是主动注入，不声称平台必然以这些顺序通知。
