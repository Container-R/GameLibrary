# 不要求长按的确认：来源和范围

- Microsoft [Xbox Accessibility Guideline 107: Input](https://learn.microsoft.com/en-us/xbox/accessibility/xbox-accessibility-guidelines/107)，Overview、Toggles and auto holds 与 Implementation guidelines：持续时间本身可能构成操作门槛，支持为持续输入提供替代。指南不是本文一次性丢弃、二阶段动作、版本校验或幂等的规定。
- W3C WAI [Dialog (Modal) Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)，Keyboard Interaction：对难以撤销的步骤，可优先把初始焦点设在破坏性最低的动作；关闭控件也应能通过焦点序列到达。本文借用对话框原则，不称任何原生游戏或平台认证。
- [可执行的合成试件](../实验/长按丢弃的点按确认/README.md)验证去重、绑定身份和修订保护，未调用实际输入、读屏、控件、设备或网络事务。
