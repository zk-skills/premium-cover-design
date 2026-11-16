# 构图原型库（8 套）

> 16 套 L 布局解决的是“元素放在哪一格”，本库解决的是“画面凭什么抓住人”。
> 每个原型给出重心、留白、标题占比与 CSS 类，直接落在 `templates/cover.css`。

## 与 L 布局的关系

- **L 布局**：规整的网格分配，适合信息型、机构型封面。
- **C 原型**：带张力、裁切、重叠、偏心，适合需要记忆点的封面。
- 两者可叠加，但一张封面只能有一个主导构图。C 原型放在 `lay-Lxx` 之后，会覆盖网格。
- 默认规则：商业经管、文学、艺术类优先用 C 原型；白皮书、年鉴、学术优先用 L 布局。

## 8 套原型

### C01 满版出血｜Edge Bleed

- **气质**：沉浸、电影感、图像优先。
- **重心**：图像中心，标题压在下方或上方留白。
- **留白**：0–10%，图像铺满四边并向外出血 5–8%。
- **标题占比**：画布短边 14%–20%。
- **实现**：`.cp-C01`；`.cv-figure{position:absolute;inset:-5% -6%}`，标题加 `text-shadow` 或局部 scrim。
- **适合**：摄影集、人物、城市、艺术、纪实。
- **风险**：文字压到图像亮部会失去可读性，必须实测对比度。

```css
.cp-C01 .cv-figure{position:absolute;inset:-5% -6%;z-index:0}
.cp-C01 .cv-title{position:relative;z-index:2;align-self:end}
.cp-C01 .cv-title h1{text-shadow:0 .2cqw 2cqw rgba(0,0,0,.38)}
```

### C02 对角切割｜Diagonal Cut

- **气质**：动势、速度、破局。
- **重心**：左下与右上形成的对角轴。
- **留白**：15%–25%。
- **标题占比**：短边 12%–18%，可轻微旋转 1–3°。
- **实现**：`.cp-C02`；图像 `clip-path` 斜切，标题沿切口排布。
- **适合**：增长、转型、青年、运动、科技。
- **风险**：旋转超过 3° 会显得廉价，只用于标题，不旋转正文。

```css
.cp-C02 .cv-figure{position:absolute;inset:0;clip-path:polygon(0 0,100% 0,100% 72%,0 100%)}
.cp-C02 .cv-title{position:relative;z-index:2;align-self:end;transform:rotate(-2deg)}
```

### C03 错位三栏｜Offset Columns

- **气质**：编辑感、内容密度、专业。
- **重心**：标题列与图像列错开 8–12%。
- **留白**：10%–18%。
- **标题占比**：短边 11%–16%。
- **实现**：`.cp-C03`；12 列网格，标题占 1–5 列，图像占 6–12 列并下移。
- **适合**：商业研究、深度报道、行业观察。
- **风险**：两列高度差不足时会退回普通分栏，位移至少 8%。

```css
.cp-C03 .cv-title{grid-column:1/6;transform:translateY(-4cqh)}
.cp-C03 .cv-figure{grid-column:6/13;margin-top:10cqh}
```

### C04 压边标题｜Edge-locked Title

- **气质**：宣言、强主张、海报感。
- **重心**：标题左边缘，向右压出画布。
- **留白**：20%–35%，集中在下方。
- **标题占比**：短边 22%–30%，允许右侧裁切。
- **实现**：`.cp-C04`；标题宽度超过画布，`overflow:hidden` 自然裁切。
- **适合**：商业畅销书、社会议题、宣言、活动。
- **风险**：裁切必须切在笔画之间，不能切断关键字的识别部位。

```css
.cp-C04 .cv-title{position:absolute;left:-2cqw;top:12cqh;width:120cqw}
.cp-C04 .cv-title h1{font-size:var(--fs-title,24cqw);white-space:nowrap}
```

### C05 层叠纸片｜Layered Sheets

- **气质**：手工、独立出版、物质感。
- **重心**：偏右上的图像层，标题压在下层。
- **留白**：18%–28%。
- **标题占比**：短边 12%–16%。
- **实现**：`.cp-C05`；图像旋转 -4°，加投影，并用 `::after` 叠一块强调色纸片。
- **适合**：文学、艺术、独立出版、设计随笔。
- **风险**：层数不超过两层，阴影不超过一档。

```css
.cp-C05 .cv-figure{transform:rotate(-4deg);box-shadow:0 3cqw 5cqw -2cqw rgba(0,0,0,.45)}
.cp-C05 .cv-figure::after{content:"";position:absolute;inset:6% -6% -6% 6%;background:var(--c-accent);z-index:-1}
```

### C06 框中框｜Frame in Frame

- **气质**：克制、档案、博物馆。
- **重心**：画面中央的框内图像。
- **留白**：30%–40%，框外留白是主角。
- **标题占比**：短边 8%–13%。
- **实现**：`.cp-C06`；图像外加 2px 线框和内衬白边。
- **适合**：艺术画册、建筑、学术、纪念集。
- **风险**：框线过粗会变成装饰噪音，保持在 1–2px。

```css
.cp-C06 .cv-figure{border:2px solid var(--c-ink);padding:2.2cqw;margin:0 6cqw}
```

### C07 纵向阅读流｜Vertical Flow

- **气质**：东方、文学、安静。
- **重心**：右侧竖排标题，左侧图像。
- **留白**：25%–40%。
- **标题占比**：短边 10%–15%。
- **实现**：`.cp-C07`；`writing-mode:vertical-rl`，标题与副标题并排两列。
- **适合**：文学、诗集、传统文化、散文。
- **风险**：竖排只适用于中文，英文与数字要转回横排。

```css
.cp-C07 .cv-title{writing-mode:vertical-rl;justify-self:end}
.cp-C07 .cv-title h1{writing-mode:vertical-rl;letter-spacing:.08em}
```

### C08 极端偏心｜Extreme Off-center

- **气质**：当代、冒险、设计感。
- **重心**：右下角标题，左上角小图，中间大片空。
- **留白**：40%–55%。
- **标题占比**：短边 12%–18%。
- **实现**：`.cp-C08`；标题右下对齐，图像缩到 30% 以内放左上。
- **适合**：设计、思想、艺术、品牌。
- **风险**：留白超过 60% 会显得空，必须有一个小而精的主体压住。

```css
.cp-C08 .cv-title{position:absolute;right:7cqw;bottom:14cqh;text-align:right}
.cp-C08 .cv-figure{position:absolute;left:7cqw;top:8cqh;width:30%;height:26%}
```

## 选择规则

| 内容情绪 | 首选 | 次选 |
| --- | --- | --- |
| 强主张、要冲击 | C04 压边、C02 对角 | C01 出血 |
| 冷静、专业、信息密集 | C03 错位、C06 框中框 | L07 模块网格 |
| 沉浸、图像叙事 | C01 出血 | C05 层叠 |
| 安静、文学、东方 | C07 纵向、C05 层叠 | C08 偏心 |
| 当代、设计、留白 | C08 偏心、C06 框中框 | C03 错位 |

## 反模式

- 标题居中 + 副标题居中 + 底部居中 Logo，没有任何错位：默认模板脸，必须至少打破一处。
- 主视觉完整居中、四边等距：没有张力，改用出血或偏心。
- 三个以上视觉焦点：读者不知道先看哪里，删到两个以内。
- 装饰线、编号、英文小字同时出现三种以上：噪音，不是设计。
- 标题与主视觉权重接近：必须明确谁主谁次，字号差至少 2.2 倍或面积差 3 倍。
