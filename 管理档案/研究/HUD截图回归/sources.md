# 来源定位与适用范围

- Epic Games，[Take Automation Screenshot](https://dev.epicgames.com/documentation/en-us/unreal-engine/BlueprintAPI/Automation/TakeAutomationScreenshot) 的说明明确普通节点不包含 UI；官方另列 [Take Automation Screenshot Of UI](https://dev.epicgames.com/documentation/en-us/unreal-engine/BlueprintAPI/Automation/TakeAutomationScreenshotOfUI) 节点。
- Epic Games，[Screenshot Comparison Tool](https://dev.epicgames.com/documentation/unreal-engine/screenshot-comparison-tool-in-unreal-engine) 中 Functional Screenshot Test Actor 说明存在场景与 UI 两条入口；设置表区分 Maximum Local Error 与 Maximum Global Error，Ground Truth Screenshot 小节说明对比基准。引擎自动分块不等于业务定义的固定窗口。
- Microsoft Playwright，[PageAssertions.toHaveScreenshot](https://playwright.dev/docs/api/class-pageassertions#page-assertions-to-have-screenshot-1) 的 threshold 与 maxDiffPixels/maxDiffPixelRatio 参数说明像素颜色判别与累计预算的区别。正文用独立 RGB 精确比较示例，不是 Playwright 执行。
