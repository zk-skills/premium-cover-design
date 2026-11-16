# 流程五：导出格式

## 主格式：HTML

单文件、样式内联、在线字体 CDN，内置 `@page` 规则，可直接打印为成品尺寸。

由 `tools/generate_cover.py` 产出的文件已满足全部要求，不要为了导出另存格式而破坏它。
唯一的网络请求来自 Google Fonts；导出 PNG/PDF 前必须等 `document.fonts.ready`，
否则会截到回退的思源黑/宋。离线场景改用 `--font-mode local` 内嵌本地字体子集。

## 派生格式

| 格式 | 方式 | 注意 |
| --- | --- | --- |
| PDF | 浏览器打印 → 另存为 PDF | 页面尺寸须等于成品尺寸，边距 0，勾选「背景图形」 |
| PNG | canvas 2 倍密度栅格化 | 必须用 `data:` URL 载入 SVG；`blob:` URL 会污染画布导致导出失败 |
| SVG | `foreignObject` 封装 | Chromium 可渲染；Illustrator 等软件对 `foreignObject` 支持有限 |
| Markdown | 规格表 | 内容 / 配方 / 布局 / 令牌 / 复现步骤 |
| JSON | 结构化令牌 | 供程序或设计系统消费 |
| CSS | 令牌片段 | 供既有项目复用配色与字体 |

## 命令行派生

```bash
# 设计令牌（JSON / CSS）
python - <<'PY'
import json, io
d = json.load(io.open('dataset/design-recipes.json', encoding='utf-8'))
r = next(x for x in d['recipes'] if x['id'] == 'R01')
print(json.dumps({'recipe': r['id'], 'tokens': r['tokens'], 'fonts': r['fonts'],
                  'texture': r['texture']}, ensure_ascii=False, indent=2))
PY
```

## 交付清单

一次完整交付应包含：

1. `封面.html` —— 成品（可编辑源文件，单文件可独立打开）。
2. `封面.pdf` —— 印刷 / 归档件。
3. `封面@2x.png` —— 评审 / 传播件。
4. `封面-规格.md` —— 设计规格交接文档。
5. `封面-tokens.json` —— 设计令牌（可选，供程序消费）。
6. 门禁报告 —— `verify_cover.py` 的输出。

## 打印设置

- 纸张尺寸：与画布预设一致（A4 → 210×297mm；书籍 160×240mm → 160×240mm）。
- 边距：无。
- 缩放：100%（版式已按成品尺寸绘制）。
- 背景图形：开启（配色与纹理依赖背景）。
- 出血：如需实际出血，在画布外扩 3mm 并把关键元素移入安全区。

## 已知限制

- SVG 导出基于 `foreignObject`，只保证 Chromium 内核可正常显示；需要 Illustrator 级兼容时改用 PNG 或重新绘制矢量。
- 程序化噪点纹理会显著增大文件体积（A4 2× PNG 约 9MB、PDF 约 18MB）。对体积敏感时把纹理档位从 `grain`/`rough` 降为 `paper` 或关闭。
- 主视觉必须来自生成图或摄影。没有主视觉图时生成器直接报错；纯文字封面用 `--text-only`。
