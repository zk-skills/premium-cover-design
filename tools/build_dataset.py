# -*- coding: utf-8 -*-
"""Merge parsed source + design tokens into the canonical dataset, and emit knowledge markdown."""
import io, json, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "dataset")
KNOW = os.path.join(ROOT, "knowledge")

def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)

parsed = load(os.path.join(SRC, "parsed.json"))
enrich = load(os.path.join(SRC, "tokens.json"))

recipes = []
for r in parsed["recipes"]:
    e = enrich.get(r["id"], {})
    r = dict(r)
    r["tokens"] = {k: e.get(k) for k in ("bg", "ink", "accent", "sub", "accent2") if e.get(k)}
    r["fonts"] = e.get("fonts", {})
    r["texture"] = e.get("texture", "none")
    r["density"] = e.get("density", 0.4)
    r["keywords"] = e.get("keywords", [])
    r["vertical"] = bool(e.get("vertical", False))
    recipes.append(r)

# category metadata
CAT_META = {
 "现代出版与编辑设计": dict(id="c1", desc="最值得作为默认设计方向。强调专业性、秩序感、字体表现和信息层级，尤其适合报告、书籍、研究成果和知识文章。"),
 "文学与人文艺术": dict(id="c2", desc="强调意境、象征、叙事和情绪表达。它不需要把内容直接画出来，而是通过视觉隐喻让读者产生联想。"),
 "高端商业与专业出版": dict(id="c3", desc="重视可信度、权威性、信息组织和视觉成熟度。"),
 "实验艺术与先锋视觉": dict(id="c4", desc="不追求传统意义上的规整，而是通过视觉冲突、非传统布局和艺术媒介创造记忆点。"),
 "摄影与视觉叙事": dict(id="c5", desc="适合需要强烈情绪、故事感和真实世界质感的出版物。"),
 "自然、科学与专业插画": dict(id="c6", desc="以知识性、精确度、观察力与科学美学为核心。"),
}
categories = [dict(name=n, **CAT_META.get(n, {})) for n in parsed["categories"]]

# 扩展组合方案：在原 12 套基础上补充 6 套，覆盖原表未覆盖的主题搭配
EXTRA_HYBRIDS = [
 {"no":13,"name":"Tech Poetic","primary":"R14","secondary":"R11","expression":"冷峻三维 + 疏朗留白",
  "technique":{"texture":"primary","displayFont":"secondary","layoutHint":"L15"},
  "use":"AI 时代的人文观察、科技产品的手册与宣言",
  "example":{"title":"《机器之后的安静》","desc":"以诗意极简的疏朗留白承载科技编辑的冷峻三维结构，适合技术与人文交叉的主题。"}},
 {"no":14,"name":"Archival Architectural","primary":"R23","secondary":"R16","expression":"老照片 + 透视结构",
  "technique":{"texture":"primary","displayFont":"primary","layoutHint":"L09"},
  "use":"城市史、建筑史、纪念册与口述史",
  "example":{"title":"《城市的第二层》","desc":"档案美学的旧纸与编号，配建筑现代主义的透视结构，适合城市空间的历史叙事。"}},
 {"no":15,"name":"Data Documentary","primary":"R15","secondary":"R21","expression":"数据曲线 + 电影级画面",
  "technique":{"texture":"primary","displayFont":"primary","layoutHint":"L05"},
  "use":"数据型年度纪实、议题型报告、纪录片式专题",
  "example":{"title":"《流动的人口》","desc":"数据智能的节点网络压在电影摄影的明暗层次之下，适合既要有数据又要有人在场的内容。"}},
 {"no":16,"name":"Botanical Scientific","primary":"R25","secondary":"R24","expression":"标本线稿 + 精密标注",
  "technique":{"texture":"primary","displayFont":"primary","layoutHint":"L09"},
  "use":"自然科普、植物图鉴、健康与营养",
  "example":{"title":"《一株植物的档案》","desc":"植物艺术的标本线稿与科学插画的解剖标注结合，用于可被查阅的自然科普。"}},
 {"no":17,"name":"Brutalist Finance","primary":"R04","secondary":"R13","expression":"强对比大字 + 精密图表",
  "technique":{"texture":"primary","displayFont":"primary","layoutHint":"L07"},
  "use":"观点型财经内容、行业争议、财经评论",
  "example":{"title":"《谁的杠杆》","desc":"粗野主义的强对比大字压着金融研究的精密图表，适合有明确立场的数据类内容。"}},
 {"no":18,"name":"Risograph Scientific","primary":"R19","secondary":"R24","expression":"套色错版 + 解剖线稿",
  "technique":{"texture":"secondary","displayFont":"primary","layoutHint":"L08"},
  "use":"面向年轻读者的科学传播、实验性展陈",
  "example":{"title":"《身体的折页》","desc":"独立印刷的套色错版承载科学插画的解剖线稿，用于降低科学内容的距离感。"}},
]

# 扩展内容类型映射
EXTRA_MAPPING = [
 {"content":"品牌与产品手册","style":"Institutional Luxury","layouts":["L01","L06"],"mediums":"建筑摄影、精致排版"},
 {"content":"展览与画册","style":"Contemporary Editorial","layouts":["L05","L08"],"mediums":"高质量摄影、拼贴"},
 {"content":"学术论文集","style":"Swiss Editorial","layouts":["L07","L01"],"mediums":"网格、数据图形"},
]

# name lookup by zh name for hybrids
by_cn = {r["nameCn"]: r for r in recipes}
def rec_by_id(rid):
    for r in recipes:
        if r["id"] == rid: return r
    raise KeyError(rid)
by_en = {r["name"]: r for r in recipes}
# 源文档中部分交叉引用使用了库外名称，此处做显式别名归一，避免悬空引用
ALIAS = {
    "极简奢华": "R12", "Minimalist Luxury": "R12", "奢华": "R12",
    "抽象艺术": "R10", "Abstract Art": "R10",
    "Independent Print": "R19", "独立印刷": "R19", "Independent Print Art": "R19",
    "Swiss Brutalism": "R04",
    "Swiss Editorial Design": "R01",
    "粗野主义": "R04", "Brutalism": "R04",
    "Modernist Minimal": "R03",
    "超现实主义": "R08", "Surrealism": "R08",
    "诗意极简": "R11", "观念艺术": "R10", "植物艺术": "R25", "文学装帧": "R06", "日式文学": "R06",
}
def resolve(nm):
    if nm in ALIAS: return ALIAS[nm]
    if nm in by_cn: return by_cn[nm]["id"]
    if nm in by_en: return by_en[nm]["id"]
    for r in recipes:
        if nm in r["nameCn"] or nm in r["name"]: return r["id"]
    return None


# 原 12 套组合补齐可执行手法与推荐布局，使其与扩展组合规格一致
HYBRID_TECHNIQUE = {
 1:  ({"texture":"primary","displayFont":"primary","layoutHint":"L12"}, "文学与科学的交叉读物、诗集与自然随笔"),
 2:  ({"texture":"primary","displayFont":"primary","layoutHint":"L05"},  "影像型深度报道、纪录片式专题"),
 3:  ({"texture":"primary","displayFont":"secondary","layoutHint":"L03"},"历史档案与观点评论、口述史"),
 4:  ({"texture":"primary","displayFont":"primary","layoutHint":"L15"}, "奢华品牌画册、概念性高端刊物"),
 5:  ({"texture":"primary","displayFont":"secondary","layoutHint":"L07"},  "自然与设计的跨主题、自然类品牌手册"),
 6:  ({"texture":"primary","displayFont":"primary","layoutHint":"L11"},"数据艺术展陈、实验型数据报告"),
 7:  ({"texture":"primary","displayFont":"primary","layoutHint":"L15"}, "情绪摄影集、生活方式类独立刊物"),
 8:  ({"texture":"secondary","displayFont":"primary","layoutHint":"L01"}, "AI 与未来科技白皮书、技术趋势报告"),
 9:  ({"texture":"primary","displayFont":"secondary","layoutHint":"L01"},"复古题材的现代呈现、怀旧主题出版"),
 10: ({"texture":"primary","displayFont":"secondary","layoutHint":"L06"}, "建筑与空间类高端画册、城市形象册"),
 11: ({"texture":"primary","displayFont":"primary","layoutHint":"L15"}, "思想性自然写作、观念类随笔"),
 12: ({"texture":"primary","displayFont":"secondary","layoutHint":"L14"},"实验文学、先锋诗歌与艺术小志"),
}

hybrids = []
for h in parsed["hybrids"]:
    h = dict(h)
    h["primaryId"] = resolve(h["primary"])
    h["secondaryId"] = resolve(h["secondary"])
    _tech, _use = HYBRID_TECHNIQUE.get(int(h["no"]), ({"texture":"primary","displayFont":"primary","layoutHint":None}, ""))
    h["technique"] = _tech
    h["use"] = _use
    hybrids.append(h)

for h in EXTRA_HYBRIDS:
    item = {"no": h["no"], "name": h["name"], "primary": rec_by_id(h["primary"])["nameCn"],
            "secondary": rec_by_id(h["secondary"])["nameCn"], "expression": h["expression"],
            "primaryId": h["primary"], "secondaryId": h["secondary"], "technique": h["technique"],
            "use": h["use"], "example": h["example"]}
    hybrids.append(item)

layouts = parsed["layouts"]
mapping = parsed["mapping"]
for m in EXTRA_MAPPING:
    mapping.append(dict(m))
hyb_by_name = {h["name"]: h for h in hybrids}
for mp in mapping:
    sid = resolve(mp["style"])
    mp["styleKind"] = "recipe"
    mp["hybridId"] = None
    if sid is None and mp["style"] in hyb_by_name:
        mp["hybridId"] = hyb_by_name[mp["style"]]["no"]
        mp["styleKind"] = "hybrid"
        sid = hyb_by_name[mp["style"]]["primaryId"]
    mp["styleId"] = sid
    mp["layoutIds"] = [l["id"] for l in layouts if l["name"] in mp["layouts"]]

# 视觉参考库（第三层）：参考图 + 拆解
refs = load(os.path.join(SRC, "references.json"))
analysis = load(os.path.join(SRC, "ref-analysis.json"))
for r in recipes:
    rf = refs.get("recipes", {}).get(r["id"], {})
    an = analysis.get("recipes", {}).get(r["id"], {})
    r["reference"] = {"title": rf.get("title", ""), "url": rf.get("url", ""), "file": rf.get("file", "")}
    r["refAnalysis"] = an
for l in layouts:
    rf = refs.get("layouts", {}).get(l["id"], {})
    an = analysis.get("layouts", {}).get(l["id"], {})
    l["reference"] = {"title": rf.get("title", ""), "url": rf.get("url", ""), "file": rf.get("file", "")}
    l["refAnalysis"] = an



# 布局基准字号（cqw）：标题字号的设计值，自动缩放以此为基准
BASE_TITLE = {"L01":10.5,"L02":9,"L03":15,"L04":6.4,"L05":10.5,"L06":9.6,"L07":8.4,"L08":8.6,
              "L09":7.6,"L10":9,"L11":10,"L12":7.2,"L13":10.5,"L14":8,"L15":6.8,"L16":9.6}
for l in layouts:
    l["baseTitle"] = BASE_TITLE.get(l["id"], 10.5)

FONT_STACKS = {
 "sans": "'Helvetica Neue',Inter,'Segoe UI','Source Han Sans SC','Noto Sans SC','Microsoft YaHei',sans-serif",
 "serif": "'Source Han Serif SC','Noto Serif SC','Songti SC',STSong,Georgia,'Times New Roman',serif",
 "mono": "'JetBrains Mono',SFMono-Regular,Consolas,'Courier New',monospace",
 "heavy": "'Arial Black','Helvetica Neue',Impact,'Source Han Sans SC','Microsoft YaHei',sans-serif",
 "display": "Baskerville,Didot,'Source Han Sans SC','Songti SC',Georgia,serif",
}
SIZES = {
 "a4":    {"label":"A4 竖版",      "mm":"210mm 297mm", "w":1240, "h":1754},
 "a4l":   {"label":"A4 横版",      "mm":"297mm 210mm", "w":1754, "h":1240},
 "book":  {"label":"书籍 160x240mm","mm":"160mm 240mm","w":945,  "h":1417},
 "pub34": {"label":"出版封面 3:4",  "mm":"180mm 240mm", "w":1350, "h":1800},
 "square":{"label":"方形 1:1",      "mm":"200mm 200mm", "w":1400, "h":1400},
 "story": {"label":"竖版 4:5",      "mm":"160mm 200mm", "w":1080, "h":1350},
 "wide":  {"label":"宽屏 16:9",     "mm":"320mm 180mm", "w":1920, "h":1080},
}
TEXTURES = {"paper": {"f":0.9,"o":0.05}, "grain": {"f":0.75,"o":0.12},
            "rough": {"f":0.035,"o":0.09}, "print": {"f":1.3,"o":0.14}, "none": None}

dataset = {
    "meta": {
        "title": "高级出版物封面设计语言与组合范式库",
        "subtitle": "Premium Cover Design Recipes · 组合范式 · 视觉参考库",
        "version": "V1.0",
        "recipeCount": len(recipes),
        "hybridCount": len(hybrids),
        "layoutCount": len(layouts),
        "fontStacks": FONT_STACKS,
        "sizes": SIZES,
        "textures": TEXTURES,
    },
    "categories": categories,
    "recipes": recipes,
    "hybrids": hybrids,
    "layouts": layouts,
    "mapping": mapping,
    "flow": parsed["flow"],
    "rules": parsed["rules"],
    "hasReferences": True,
}
with io.open(os.path.join(SRC, "design-recipes.json"), "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

def W(path, text):
    with io.open(os.path.join(KNOW, path), "w", encoding="utf-8") as f:
        f.write(text)

# ---------- design-recipes.md ----------
out = ["# 高级出版物封面设计语言 · 设计配方库", "",
       "> 26 套完整可执行配方。每套含：风格描述 / 表现手法 / 布局方式 / 构图方案 / 字体 / 色彩 / 材质 / 适合方向 / 参考示例 / AI 设计指令 / 设计令牌。", ""]
cur = None
for r in recipes:
    if r["category"] != cur:
        cur = r["category"]
        out += ["", "## %s" % cur, ""]
    out += ["### %02d. %s｜%s" % (r["no"], r["name"], r["nameCn"]), ""]
    if r["tag"]:
        out += ["`%s`" % r["tag"], ""]
    out += ["- **设计定位**：%s" % r["positioning"]]
    if r["desc"]:
        out += ["- **风格释义**：%s" % r["desc"]]
    out += ["", "| 设计维度 | 具体方案 |", "| --- | --- |"]
    for k, v in r["dims"].items():
        out.append("| %s | %s |" % (k, v))
    out += ["", "**设计令牌**：底色 `%s` · 主墨色 `%s` · 强调色 `%s` · 辅助色 `%s` · 纹理 `%s`" %
            (r["tokens"].get("bg"), r["tokens"].get("ink"), r["tokens"].get("accent"), r["tokens"].get("sub"), r["texture"])]
    out += ["", "**参考示例**", ""]
    for e in r["examples"]:
        out.append("- %s %s" % (e["title"], e["desc"]))
    if r["instruction"]:
        out += ["", "> **AI 设计指令**：%s" % r["instruction"], ""]
W("design-recipes.md", "\n".join(out) + "\n")

# ---------- style-combinations.md ----------
out = ["# 跨风格组合方案（18 套）", "",
       "前面 26 套是基础配方。混合风格用于覆盖普通风格难以处理的主题：主风格决定调性与秩序，辅助风格只提供一个明确的手法或媒介，不做平均混合。", "",
       "H01-H12 来自原始设计配方文档；H13-H18 为在原表基础上补充的扩展组合，补齐科技与人文、建筑与档案、数据与纪实、植物与科学、财经观点、科学传播六类缺口。", "",
       "每套组合都带可执行手法，用 `tools/generate_cover.py --hybrid Hxx` 可直接产出成品：",
       "主风格提供色板与版式骨架，辅助风格按需提供主视觉手法 / 纹理 / 展示字体，组合自带推荐布局。", "",
       "| # | 组合名称 | 主风格 | 辅助风格 | 典型表现 | 手法来源 | 推荐布局 | 适用 |",
       "| --- | --- | --- | --- | --- | --- | --- | --- |"]
TECH = {"texture": "纹理", "displayFont": "展示字体"}
for h in hybrids:
    tech = h.get("technique") or {}
    src = "、".join(TECH[k] + "←辅" for k in ("texture", "displayFont") if tech.get(k) == "secondary") or "全部←主"
    out.append("| H%02d | %s | %s | %s | %s | %s | %s | %s |" % (
        h["no"], h["name"], h["primary"], h["secondary"], h["expression"], src,
        tech.get("layoutHint") or "—", h.get("use") or "—"))
out += ["", "## 使用示例", ""]
for h in hybrids:
    if h.get("example"):
        out.append("- **H%02d %s**（%s + %s）：%s" % (
            h["no"], h["name"], h["primary"], h["secondary"], h["example"]["desc"]))
out += ["", "## 调用方式", "", "```bash",
 "python tools/generate_cover.py --hybrid 13 \\",
 "  --title \"机器之后的安静\" --subtitle \"当算法退场，人如何重新观看\" \\",
 "  --kicker \"人文观察\" --meta1 \"技术与人文实验室\" --meta2 \"2026\" \\",
 "  --out cover.html", "```", ""]
W("style-combinations.md", chr(10).join(out) + chr(10))

# ---------- composition-patterns.md ----------
out = ["# 布局与构图方案独立索引（16 套）", "",
       "布局与风格解耦，可自由组合。", "", "| ID | 名称 | 说明 |", "| --- | --- | --- |"]
for l in layouts:
    out.append("| %s | %s | %s |" % (l["id"], l["name"], l["desc"]))
W("composition-patterns.md", "\n".join(out) + "\n")

# ---------- content-style-mapping.md ----------
out = ["# 内容类型 → 风格 / 布局 / 表现手法 映射矩阵", "",
       "用于自动决策的第一入口。", "", "| 内容类型 | 主风格 | 推荐布局 | 推荐表现手法 |", "| --- | --- | --- | --- |"]
for m in mapping:
    out.append("| %s | %s | %s | %s |" % (m["content"], m["style"], "、".join(m["layouts"]), m["mediums"]))
W("content-style-mapping.md", "\n".join(out) + "\n")

# ---------- design-decision-rules.md ----------
out = ["# 自动设计决策规范", "", "## 决策流程", ""]
for i, s in enumerate(dataset["flow"], 1):
    out.append("%d. **%s**%s" % (i, s["step"], ("：%s" % s["detail"]) if s["detail"] else ""))
out += ["", "## 约束", ""]
for i, r in enumerate(dataset["rules"], 1):
    out.append("%d. %s" % (i, r))
W("design-decision-rules.md", "\n".join(out) + "\n")

# ---------- typography-systems.md ----------
FONTS = [
 ("sans", "现代无衬线", '"Helvetica Neue", Inter, "Segoe UI", "Source Han Sans SC", "Noto Sans SC", "Microsoft YaHei", sans-serif', "报告 / 科技 / 信息类主字体"),
 ("serif", "现代衬线", '"Source Han Serif SC", "Noto Serif SC", "Songti SC", STSong, Georgia, "Times New Roman", serif', "文学 / 人文 / 品牌类主字体"),
 ("mono", "等宽", '"JetBrains Mono", "SFMono-Regular", Consolas, "Courier New", monospace', "编号 / 数据 / 档案 / 元信息"),
 ("heavy", "超粗展示体", '"Arial Black", "Helvetica Neue", Impact, "Source Han Sans SC", "Microsoft YaHei", sans-serif', "粗野主义 / 构成主义 / 实验类"),
 ("display", "装饰展示体", '"Baskerville", "Didot", "Source Han Serif SC", "Songti SC", Georgia, serif', "独立出版 / 复古印刷类"),
]
out = ["# 字体系统", "", "封面只用 3 个层级：展示（Display）、正文（Body）、元信息（Meta）。层级超过 3 层会破坏封面节奏。", "",
       "| 语义 | 角色 | 字体栈 | 典型用途 |", "| --- | --- | --- | --- |"]
for k, name, stack, use in FONTS:
    out.append("| `%s` | %s | `%s` | %s |" % (k, name, stack, use))
out += ["", "## 层级规则", "",
        "- 展示字号：封面的主导元素，通常为版面短边的 12%–22%（超大标题可到 30%）。",
        "- 正文/副标题：展示字号的 25%–40%，不与展示字号竞争。",
        "- 元信息：9–13px，等宽或无衬线，字距 +0.08em，不承担阅读任务。",
        "- 中文标题长度必须实测：超过 12 字时优先换行或降级，而不是溢出。",
        "- 竖排仅用于中文文学/诗集类（配方 R06 等已标注），需 `writing-mode: vertical-rl`。",
        "- 所有字体必须为本地可得或可内嵌，禁止在封面文件中引用外部 CDN 字体（离线与印刷要求）。"]
W("typography-systems.md", "\n".join(out) + "\n")

# ---------- color-systems.md ----------
out = ["# 色彩系统", "", "每套配方定义 4 个语义色，封面中不允许出现第 5 种颜色。", "",
       "| 令牌 | 作用 | 规则 |", "| --- | --- | --- |",
       "| `bg` | 底色 | 承载大面积面积感，可为纯色或极浅纸色 |",
       "| `ink` | 主墨色 | 标题与主要文字，必须与 `bg` 对比度 ≥ 4.5:1 |",
       "| `accent` | 强调色 | 唯一的高饱和色，用于焦点（图形 / 编号 / 关键数据），与 `bg` 对比度 ≥ 3:1 |",
       "| `sub` | 辅助色 | 次级信息、分割线、图注，与 `bg` 对比度 ≥ 3:1 |",
       "| `accent2` | 次强调色 | 仅在配方明确为多色体系时使用（如 R19 / R20 / R17） |", "",
       "## 规则", "",
       "- 配色来自配方，不做临时替换；确需替换时三项同时改，保持体系性。",
       "- 强调色面积占比不超过版面 15%。",
       "- 深底封面（`bg` 亮度 < 0.2）时，`ink` 应为纸白而非纯黑。",
       "- 印刷场景（Risograph / Archival）额外加入套色偏移与印刷噪点，不做数字渐变。"]
W("color-systems.md", "\n".join(out) + "\n")

# ---------- visual-mediums.md ----------
out = ["# 视觉媒介与表现手法", "",
       "配方里的「表现手法」决定主视觉用什么媒介落地。正式封面只有两条路：位图主视觉，或纯文字。", "",
       "## 一、三种媒介，两种能当主视觉", "",
       "| 类型 | 含义 | 实现方式 | 能否当主视觉 |", "| --- | --- | --- | --- |",
       "| 摄影／生成图 | 真实质感、光、空间、物件 | 按配方出提示词，生成后裁切调色，`--hero` 上版 | 能，默认选择 |",
       "| 纯文字 | 极限留白、概念、宣言 | `--text-only`，靠字体与色彩成立 | 能，但字体必须有性格 |",
       "| 图形 | 几何分割、装饰、辅助结构 | CSS／SVG 画辅助元素 | 不能，面积不超过主视觉 30% |", "",
       "硬规则：图形元素只承担分割、指向、包裹、承托的功能，不承担「画面」本身。用线段、方块、虚线圆拼出的图形当主视觉，就是线框稿。", "",
       "## 二、配方与主体倾向", "",
       "具体提示词参数在 `dataset/image-prompts.json`，用 `tools/hero_prompt.py` 调出。", "",
       "| 配方组 | 媒介 | 典型主体 | 关键材质与光 |", "| --- | --- | --- | --- |",
       "| R01–R05 | 静物摄影、材料平铺 | 球体与钢板、混凝土、模块样板 | 哑光漆、拉丝金属、硬侧光 |",
       "| R06–R11 | 自然与概念摄影 | 枯枝、陶器、纸、水面、砖 | 和纸、黏土、柔光、逆光 |",
       "| R12–R16 | 建筑、数据、科技 | 石立面、黄铜山脊、玻璃体、光纤 | 石材、玻璃、冷轮廓光 |",
       "| R17–R20 | 印刷与数字实验 | 套色纸、撕纸拼贴、铬、全息 | 粗颗粒、套印偏移、镜面反射 |",
       "| R21–R26 | 摄影、艺术、雕塑 | 夜路、纸褶、档案卡、标本、植物、铝带 | 胶片颗粒、微距、金属高光 |", "",
       "## 三、生成图的验收", "",
       "1. 能一句话说出画面里是什么。", "2. 放大能看到材质与边缘，不是纯色块。",
       "3. 文字要放的位置足够安静。", "4. 色调和封面配色是一家人。", "",
       "四条有一条不成立就重出，不靠后期硬救。方法见 `hero-image-prompts.md`。", "",
       "## 四、辅助图形的边界", "",
       "允许：", "", "- 一条分割信息层的线。", "- 一个与主题相关、面积不超过主视觉 30% 的辅助图形。",
       "- 一条承托标题或切分版面的曲线、斜切。", "- 一套重复纹理或网格。", "",
       "禁止：", "", "- 用细线、空心方块、虚线圆、进度条堆出一张「画面」。",
       "- 装饰元素超过 3 个。", "- 无来源的英文、编号、坐标、日期。"]
W("visual-mediums.md", "\n".join(out) + "\n")

print("dataset + knowledge written. recipes=%d hybrids=%d layouts=%d mapping=%d" %
      (len(recipes), len(hybrids), len(layouts), len(mapping)))
print("unresolved hybrids:", [ (h["name"], h["primaryId"], h["secondaryId"]) for h in hybrids if not h["primaryId"] or not h["secondaryId"] ])
print("unresolved mapping:", [ (m["content"], m["styleId"]) for m in mapping if not m["styleId"] ])
