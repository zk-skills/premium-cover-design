# README · premium-cover-design

面向 AI 调用的出版物封面设计 Skill。六步工作流：接收内容 → 多轮调研 → 多轮创意 → 定风格排版 → 定元素 → 组合择优。署名、出版社、分类题眉也在设计范围内，提供 5 套署名区原型与 3 种题眉位置。

## 六步工作流

| 步 | 动作 | 产出 | 对应文件 |
| --- | --- | --- | --- |
| 1 | 接收需求与内容分析 | 内容画像卡 + 信息缺口 | `workflows/content-analysis.md` |
| 2 | 多轮调研（主题 / 竞品 / 工艺） | 关键词地图 + 竞品坐标 + 设计假设 | `workflows/02-research-analysis.md` |
| 3 | 多轮创意（发散 / 收敛 / 组合） | 10 个隐喻 → 3 个方向 → 3 套方案 | `workflows/03-creative-exploration.md` |
| 4 | 定风格、构图、字体、色调、署名区 | 方案定稿卡 | `knowledge/` 各库 |
| 5 | 定图片、背景、元素 | 元素清单表 | `workflows/05-elements-planning.md` |
| 6 | 组合、门禁、评分、择优 | HTML / PDF / PNG | `tools/` |

顺序不能跳。第 2、3 步都要跑满轮次，不允许从文案直接套模板。

## 三层结构

| 层 | 内容 | 位置 |
| --- | --- | --- |
| 第一层 · 设计语言库 | 26 套艺术方向的字体、色彩、材质、表现手法 | `knowledge/art-directions.md` |
| 第二层 · 设计配方库 | 完整风格组合 + 18 套混合风格 + 16 套布局范式 + 内容映射 | `knowledge/design-recipes.md` 等 9 份 |
| 第三层 · 视觉案例库 | 41 张参考图的逐张拆解（图片资产已移除以压缩体积）+ 商业书双轨案例 + 3 张原型示范 | `knowledge/visual-reference-library.md`、`knowledge/book-cover-tradeoffs.md`、`examples/prototypes/` |

## 目录

```
premium-cover-design/
├── SKILL.md                        Agent 入口：触发条件、流程、命令、门禁
├── README.md                       本文件
├── knowledge/                      19 份知识文件（含在线字体、字体组合、构图原型、文字介质、署名区原型、商业书双轨、形状语言、清晰度）
├── workflows/                      9 份执行流程（含调研、创意、元素）
├── templates/
│   └── cover.css                   版式引擎：16 布局 + 8 构图原型 + 32 字体组合 + 5 署名区原型
├── dataset/
│   ├── design-recipes.json         全库结构化数据
│   ├── fonts-online.json           79 个在线字体 + 32 组组合（主力）
│   ├── fonts.json                  5 个本地字体（仅离线兜底）
│   ├── references.json             参考图索引
│   ├── ref-analysis.json           参考图拆解
│   ├── tokens.json                 26 套配色的设计令牌
│   ├── image-prompts.json          26 套配方的主视觉提示词参数
│   └── source-recipes.txt          原始设计配方文本
└── tools/
    ├── generate_cover.py           主生产工具：配方 + 布局 → 单文件 HTML
    ├── fit_cover.py / .js          标题自适应缩放
    ├── verify_cover.py             15 项质量门禁（含主视觉来源、形态与清晰度）
    ├── hero_prompt.py              配方 → 主视觉提示词（三种景别变体）
    ├── prepare_hero.py             主视觉裁切、降饱和、叠色、dpi 体检
    ├── check_fonts.py              字体体检：本地字形 / --online 在线可用性与缺字
    ├── score_cover.py              视觉表现评分（层级/标题/字体/构图/克制，支持双轨）
    ├── shelf_test.py               货架缩略图：240px / 120px + 明度/饱和/暖色比例
    ├── check_image_quality.py      图片与 Logo 有效 dpi、放大倍数、清晰度结论
    ├── text_to_svg.py              标题转曲：描边/金属渐变/材质填充/叠印/单字旋转
    ├── build_type_specimen.py      生成 8 种文字介质样张
    ├── verify_cover_browser.js     真实布局检查（溢出/安全区/主次关系）
    ├── sweep_all.js                26 配方 × 16 布局全量回归（需自备主视觉）
    ├── parse_source.py             源文本 → 结构化数据
    ├── enrich.py                   设计令牌编写
    ├── fix_tokens.py               令牌对比度适配（保色相，只调明度）
    └── build_dataset.py            合并数据并生成知识文件
```

## 快速开始

```bash
# 1) 产出封面
python tools/generate_cover.py --recipe R01 --layout L01 --size a4 \
  --title "2026 全球数字经济发展报告" \
  --subtitle "结构、变量与拐点的系统分析" \
  --kicker "产业观察" --meta1 "产业研究院" --meta2 "2026" \
  --fit --out cover.html

# 2) 跑门禁（12 项，含在线字体来源与缺字风险）
python tools/verify_cover.py cover.html --recipe R01 \
  --title "2026 全球数字经济发展报告" \
  --kicker "产业观察" --meta1 "产业研究院" --meta2 "2026"

# 2.1) 字体体检：79 个在线字体是否可用、指定书名是否缺字
python tools/check_fonts.py --online
python tools/check_fonts.py --online --sample "三品合一破局内卷"

# 3) 视觉表现评分（五项各 20 分）
python tools/score_cover.py cover.html

# 4) 标题转曲：金属渐变 / 材质填充 / 描边镂空
python tools/text_to_svg.py --text "三品合一" \
  --font /usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc --font-index 2 \
  --size 240 --gradient "#E8D5A8,#6E5228" --output hero.svg

# 或直接用组合方案 + 构图原型 + 字体组合
python tools/generate_cover.py --hybrid 13 --title "机器之后的安静" \
  --subtitle "当算法退场，人如何重新观看" --kicker "人文观察" \
  --meta1 "技术与人文实验室" --meta2 "2026" \
  --typepair T09 --composition C08 --out cover.html

# 书籍封面：署名区 A03 咬合 + 题眉 inline
python tools/generate_cover.py --recipe R12 --size pub34 \
  --title "三品合一" --subtitle "破局内卷的品类增长战法" \
  --author "贾伟 著" --org "洛可可品类增长学园 组编" \
  --press "机械工业出版社" --press-en "CHINA MACHINE PRESS" \
  --credits A03 --kicker-pos inline --credits-scrim "rgba(10,12,16,.62)" \
  --hero hero.jpg --out cover.html

# 图片与 Logo 清晰度（按成品显示尺寸算 dpi）
python tools/check_image_quality.py hero.png logo.png \
  --mm 141,50 --display-px 1060,374

# 浏览器类检查需要 Playwright（可选；Skill 未内置 node_modules，用时自行安装）
npm i -D playwright && npx playwright install chromium
```

## 商业书的双轨

商业／经管书先判轨，再定标题权重。同一套阈值会误伤其中一轨。

| | 气质轨 | 货架轨 |
| --- | --- | --- |
| 渠道 | 礼品、课程、专业机构 | 电商、机场、商超 |
| 标题占短边 | 12–22% | 26–40% |
| 评分命令 | `score_cover.py x.html --track premium` | `score_cover.py x.html --track mass` |
| 缩略图 | 240px 下书名 ≥16px | 240px 下书名 ≥26px，另跑 `shelf_test.py` |

三套候选至少覆盖两轨。规则、2×2 标题网格、暖色渐变边界与案例拆解见
`knowledge/book-cover-tradeoffs.md`。

## 署名区与题眉

作者、组编、出版社、分类小字不能永远排成「左上角分类、左下作者、右下社标」。5 套原型按结构关系选，不做单纯位移：

| 原型 | 结构关系 | 适合 |
| --- | --- | --- |
| A01 底栏对齐 | 作者与社标同基线 | 报告、机构、多数商业书 |
| A02 标题同轴 | 信息行与标题共轴 | 瑞士编辑、白皮书 |
| A03 图文咬合 | 署名承接主视觉下缘 | 满版出血、电影感 |
| A04 书脊竖排 | 竖列与标题边缘平行 | 文学、诗集、传记 |
| A05 题签印戳 | 实底标签贴边 | 档案、复古、独立出版 |

题眉必须和标题或署名同区，不允许孤悬左上或右上。书籍画布默认 `inline`，并入署名信息带；报告跟随布局；文学可用 `side`。三套候选至少覆盖两种原型，社标保持水平、尺寸优先于创意。规则见 `knowledge/credits-system.md`。

## 形状语言与清晰度

- **形状**：不要默认全是矩形、直线。至少一个曲线、斜切、3–8° 旋转、椭圆裁切或有机边；每个形状要有功能。见 `knowledge/shape-language.md`。
- **清晰度**：主视觉印刷 ≥300dpi，Logo 矢量优先或 ≥600dpi 等效，放大 >2× 不接受。见 `knowledge/image-clarity.md`。

```bash
python tools/check_image_quality.py hero.png logo.png \
  --mm 141,50 --display-px 1060,374
```

最终回复必须写明「配方 × 构图 × 字体 × 介质 × 署名区」和清晰度结论，不能只发链接。

## 安装

放进任一 Skill 目录即可被调用：

- 项目级：`<项目>/.agents/skills/premium-cover-design/`
- 用户级：`~/.codex/skills/premium-cover-design/`
- OpenViking：`ov skills add` 或 `add_skill` 工具

## 验证状态（2026-11-12）

| 项目 | 结果 |
| --- | --- |
| 26 配方 × 16 布局全量回归 | 416 组合，0 问题 |
| 署名区 A01–A05 | 5/5 渲染通过，无重叠、无安全区越界 |
| 47 张示例门禁 | 44 配方示例 + 3 原型示范，0 失败 |
| 导出产物 | HTML / PDF / PNG / SVG / Markdown / JSON / CSS 均有效 |
| 在线字体 | 79/79 可借 Google Fonts 加载；11 个简体全覆盖、42 个东亚汉字、4 个繁体、22 个拉丁 |
| 外部资源 | 只允许字体 CDN，其他外链门禁失败 |

## 已知限制

- SVG 导出基于 `foreignObject`，仅保证 Chromium 内核正常显示。
- 程序化噪点纹理使 A4 2× PNG 约 9MB、PDF 约 18MB；对体积敏感时把纹理降为 `paper` 或关闭。
- 主视觉必须来自生成图或摄影。纯代码矢量母题已移除；没有主视觉图时生成器直接报错，纯文字封面用 `--text-only`。
- 浏览器类门禁依赖 Playwright；未安装时静态 9 项仍可用，浏览器 3 项标记为「跳过」，需人工核对溢出与安全区。
