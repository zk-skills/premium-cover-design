# 流程四：HTML 封面生成

## 1. 优先用工具生成

不要从零手写 HTML。先用 `tools/generate_cover.py` 产出成品，再按需微调。

```bash
python tools/generate_cover.py --recipe R01 --layout L01 --size a4 \
  --title "2026 全球数字经济发展报告" \
  --subtitle "结构、变量与拐点的系统分析" \
  --kicker "产业观察" --meta1 "产业研究院" --meta2 "2026" \
  --fit --out cover.html
```

产出结构（单文件，样式内联）：

```html
<div class="cover lay-L01" style="--c-bg:…;--c-ink:…;--c-accent:…;--c-sub:…;
     --f-display:…;--f-body:…;--f-meta:…;--fs-title:10.5cqw;--fs-sub:3.15cqw;--c-scrim:…">
  <div class="cv-texture">…程序化噪点…</div>
  <div class="cv-frame">
    <div class="cv-kicker">题眉</div>
    <div class="cv-title"><h1>标题</h1><p class="cv-sub">副标题</p></div>
    <div class="cv-figure"><img src="data:image/jpeg;base64,…" alt=""></div>
    <div class="cv-meta"><span>机构</span><i class="rule"></i><span>年份</span></div>
  </div>
</div>
```

## 2. 坐标系与画布

版式用容器查询单位，标题字号 `cqw`、纵向间距 `cqh`，换画布尺寸不用重调。

| 预设 | 像素 | 毫米 |
| --- | --- | --- |
| `a4` | 1240×1754 | 210×297 |
| `a4l` | 1754×1240 | 297×210 |
| `book` | 945×1417 | 160×240 |
| `pub34` | 1350×1800 | 180×240 |
| `square` | 1400×1400 | 200×200 |
| `story` | 1080×1350 | 160×200 |
| `wide` | 1920×1080 | 320×180 |

## 3. 槽位、布局与书籍信息

| 槽位 | 内容 | 作用 |
| --- | --- | --- |
| `.cv-kicker` | 题眉 / 系列 | 建立层级，不抢主位 |
| `.cv-tagline` | 宣传语 | 书籍封面顶部，与 kicker 二选一 |
| `.cv-title` | 标题 + 副标题 | 视觉主体 |
| `.cv-figure` | 主视觉 | 生成图或摄影，`<img>` 内嵌 |
| `.cv-meta` | 机构 / 年份 / 编号 | 底部信息条 |
| `.cv-bookfoot` | 作者 + 出版社 Logo | 书籍封面页脚 |

布局用 `.lay-Lxx`，构图原型用 `.cp-Cxx`，字体组合用 `.tp-Txx`，定义见 `templates/cover.css`。
**布局与风格解耦**，同一配方可换任意构图与字体。

书籍封面推荐参数：

```bash
python tools/generate_cover.py --recipe R12 --size pub34 \
  --title "三品|合一" --subtitle "破局内卷的品类增长战法" \
  --tagline "贾伟最新力作！" --author "贾伟 著" --org "洛可可品类增长学园 组编" \
  --press "机械工业出版社" --press-en "CHINA MACHINE PRESS" --logo logo.png \
  --typepair T12 --composition C04 --out cover.html
```

标题里的 `|` 表示强制换行；`--logo` 支持 png/jpg，自动转 base64 内嵌。

## 4. 中文标题长度的硬性处理

这是封面最容易翻车的地方，必须实测而不是目测：

1. 标题字号用 `cqw`，行高不低于 0.9，否则笔画互相咬合。
2. 生成时加 `--fit`，工具会用真实排版测量溢出并二分求出最大可容纳字号，回写到文件。
3. 缩到 50% 仍放不下时，**不要继续缩字**：改用更宽松的布局（L04 / L15）或改写标题。
4. `L12` 竖排布局中，长标题会自动折成多列，必要时同样改写。

## 5. 色彩与纹理

- 每套配方只有 5 个语义色：`--c-bg` / `--c-ink` / `--c-accent` / `--c-sub` / `--c-accent2`，不引入第 6 色。
- 强调色面积不超过版面 15%。
- 底色亮度 < 0.25 时自动加 `darkink` 类，标题转为纸白。
- 纹理用 SVG `feTurbulence` 程序化生成（paper / grain / rough / print 四档），不依赖位图。
- 满版摄影（L05）与图文重叠（L13）时，标题背景自动叠一层径向渐变衬底 `--c-scrim` 保证可读。

## 6. 手写微调时的红线

- 保留语义化类名与 CSS 变量，便于二次设计。
- 不引入外部请求：不用 CDN、不用外链字体、不用远程图片。
- 字体只用系统可得字体栈（见 `knowledge/typography-systems.md`）。
- 保持 `@page{size:…;margin:0}` 与画布尺寸一致。

## 7. 生成后必须跑门禁

```bash
python tools/verify_cover.py cover.html --recipe R01 \
  --title "2026 全球数字经济发展报告" --kicker "产业观察" \
  --meta1 "产业研究院" --meta2 "2026"
```

12 项全绿再跑视觉评分：

```bash
python tools/score_cover.py cover.html
```

评分低于 70 分，换字体组合或构图原型重做，不要靠调颜色掩盖。
