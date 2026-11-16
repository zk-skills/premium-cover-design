# 字体系统

封面只用 3 个层级：展示（Display）、正文（Body）、元信息（Meta）。层级超过 3 层会破坏封面节奏。

| 语义 | 角色 | 字体栈 | 典型用途 |
| --- | --- | --- | --- |
| `sans` | 现代无衬线 | `"Helvetica Neue", Inter, "Segoe UI", "Source Han Sans SC", "Noto Sans SC", "Microsoft YaHei", sans-serif` | 报告 / 科技 / 信息类主字体 |
| `serif` | 现代衬线 | `"Source Han Serif SC", "Noto Serif SC", "Songti SC", STSong, Georgia, "Times New Roman", serif` | 文学 / 人文 / 品牌类主字体 |
| `mono` | 等宽 | `"JetBrains Mono", "SFMono-Regular", Consolas, "Courier New", monospace` | 编号 / 数据 / 档案 / 元信息 |
| `heavy` | 超粗展示体 | `"Arial Black", "Helvetica Neue", Impact, "Source Han Sans SC", "Microsoft YaHei", sans-serif` | 粗野主义 / 构成主义 / 实验类 |
| `display` | 装饰展示体 | `"Baskerville", "Didot", "Source Han Serif SC", "Songti SC", Georgia, serif` | 独立出版 / 复古印刷类 |

## 层级规则

- 展示字号：封面的主导元素，通常为版面短边的 12%–22%（超大标题可到 30%）。
- 正文/副标题：展示字号的 25%–40%，不与展示字号竞争。
- 元信息：9–13px，等宽或无衬线，字距 +0.08em，不承担阅读任务。
- 中文标题长度必须实测：超过 12 字时优先换行或降级，而不是溢出。
- 竖排仅用于中文文学/诗集类（配方 R06 等已标注），需 `writing-mode: vertical-rl`。
- 所有字体必须为本地可得或可内嵌，禁止在封面文件中引用外部 CDN 字体（离线与印刷要求）。
