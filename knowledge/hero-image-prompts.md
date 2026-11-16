# 主视觉提示词：为什么生成图会 low，以及怎么不 low

> 生成图不是「写一句高级感」就行。画面 low 的病根只有五个，每个都能在提示词里修。

## 一、五个病根

| 病根 | 表现 | 修法 |
| --- | --- | --- |
| 没有主体 | 满屏光斑、粒子、线条，说不出画面里是什么 | 指定一个可命名的物：一个球、一把椅子、一块石板 |
| 没有材质 | 平涂色块、塑料感、廉价 3D | 写死材质：拉丝铝、生陶瓷、粗混凝土、和纸、铸铁 |
| 没有光 | 均匀打亮，没有明暗方向 | 写死光源：单侧柔光箱、午后斜阳、冷调轮廓光 |
| 元素堆砌 | 球 + 线 + 方块 + 网格一起上 | 一张封面一个主体，最多一个配角 |
| 没有负空间 | 主体塞满，文字只能叠在主体上 | 指定留白方向和比例：左侧 45% 空、上方全空 |

**判定标准**：把生成的图给另一个人看，他能用一句话说出「这是什么、什么做的、光从哪来」。说不出，就是废图。

## 二、六要素公式

```
[媒介] of [一个主体]，[景别与裁切]，
[构图与负空间]，[光]，
[材质]，[配色]，[情绪]，
[画质词]，[无文字]，[比例]
```

对应到工具：

```bash
# 直接产出完整提示词
python tools/hero_prompt.py --recipe R14 --aspect 3:4 --variation 1
python tools/hero_prompt.py --recipe R06 --variation 2 --json
```

26 套配方的媒介、主体、光、镜头、材质、配色已写在 `dataset/image-prompts.json`，不要求每次从零想。

## 三、三个变体

三套候选封面不能只换配色。用 `--variation` 拉开景别：

| 变体 | 景别 | 适用 |
| --- | --- | --- |
| 1 | 环境远景，主体小，大面积留白 | 气质轨、文学、机构 |
| 2 | 紧密裁切，主体铺满，材质可读 | 货架轨、商业书、需要冲击力 |
| 3 | 低角度仰拍，主体压迫，暗部包裹 | 宣言、青年文化、强态度 |

## 四、负向词必须带

`dataset/image-prompts.json` 的 `globalNegative` 已包含最容易翻车的词：

```
vector clipart, wireframe, thin hairlines, blueprint, flat UI icons,
infographic placeholder, empty rectangles, dashed circles, graph grid,
flow chart, network diagram, clip art, cheap 3d render, plastic look,
text, letters, watermark, logo
```

生成时整段带上。少一段，画面就会往「PPT 图标」方向跑。

## 五、生成后的四步验收

1. **主体**：能一句话说出画面里是什么。
2. **材质**：放大后能看到表面与边缘，不是纯色块。
3. **留白**：文字要放的位置是否足够安静。不够就换 `--variation` 重出。
4. **色调**：图和封面配色是不是一家人。不是就用 `prepare_hero.py` 降饱和或叠色。

```bash
python tools/prepare_hero.py hero-raw.png --size a4 --out hero.jpg \
  --focus "50% 35%" --desat 20 --tone "#0B1A2E" --tone-op 0.3
```

## 六、上版

```bash
python tools/generate_cover.py --recipe R14 --layout L05 \
  --title "…" --subtitle "…" --hero hero.jpg \
  --hero-tone "#0A0E18" --hero-tone-op 0.32 --hero-focus "50% 42%" \
  --out cover.html
```

- 全出血版式（L05 / L13）配深色主视觉时，生成器会自动反白文字并加深色渐变衬底。
- 分栏版式（L01 / L06）不需要满版图，主视觉只占一栏，留白由版面承担。
- 生成图达不到 300dpi 时，屏幕交付照常；付印前必须按 `--print` 门禁重出更大尺寸。
