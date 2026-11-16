# -*- coding: utf-8 -*-
"""Parse the raw recipe source into structured JSON (recipes / hybrids / layouts / mapping / rules)."""
import json, re, sys, io, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "src", "data", "source-recipes.txt")

def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()

text = read(SRC)
lines = text.split("\n")

# ---------- split into category blocks ----------
cat_pat = re.compile(r"^# 第[一二三四五六]类：(.+)$")
recipes, categories = [], []
cur_cat = None
i = 0
blocks = []  # (category, body_lines)
while i < len(lines):
    m = cat_pat.match(lines[i].strip())
    if m:
        cur_cat = m.group(1).strip()
        categories.append(cur_cat)
        i += 1
        continue
    blocks.append((cur_cat, lines[i]))
    i += 1

# regroup: walk original lines, cut on '## NN.' boundaries
cat = None
buf = []
sections = []  # (cat, [lines])
for ln in lines:
    m = cat_pat.match(ln.strip())
    if m:
        cat = m.group(1).strip()
        continue
    if re.match(r"^## \d+\. ", ln.strip()):
        if buf:
            sections.append((cat, buf))
        buf = [ln]
    else:
        buf.append(ln)
if buf:
    sections.append((cat, buf))

rec_pat = re.compile(r"^##\s*(\d+)\.\s*(.+?)\s*｜\s*(.+?)\s*$")

def parse_block(cat, blk):
    head = rec_pat.match(blk[0].strip())
    if not head:
        return None
    no = int(head.group(1))
    en = head.group(2).strip()
    cn = head.group(3).strip()
    body = blk[1:]
    ref = ""
    tag = ""
    positioning = ""
    desc = ""
    dims = {}
    examples = []
    instruction = ""

    # metadata lines
    meta = []
    idx = 0
    while idx < len(body):
        s = body[idx].strip()
        if s.startswith("[") and "](" in s:
            ref = s
            idx += 1
            continue
        if re.match(r"^[^|#\[].{0,12}$", s) and not s.startswith("设计定位") and not s.startswith("参考示例") \
           and not s.startswith("设计指令") and not s.startswith("|") and s and not s.endswith("：") and not s.endswith(":"):
            # short tag line like 通用推荐
            if len(s) <= 12 and not s.startswith("设计"):
                tag = s
                idx += 1
                continue
        break

    joined = "\n".join(body)

    m = re.search(r"^设计定位：(.+)$", joined, re.M)
    if m:
        positioning = m.group(1).strip()

    # description = first paragraph after 设计定位 that is not a table/reference/example
    para_re = re.search(r"设计定位：.+\n+(.+?)\n", joined, re.S)
    if para_re:
        desc = re.sub(r"\s+", " ", para_re.group(1).strip())

    # table
    for row in re.findall(r"^\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|\s*$", joined, re.M):
        k, v = row[0].strip(), row[1].strip()
        if k in ("设计维度", "----", "---") or set(k) <= set("-: "):
            continue
        if k and v:
            dims[k] = v

    # examples
    ex_block = ""
    m = re.search(r"参考示例：\n(.*?)(?=\n\n设计指令|\n设计指令|\Z)", joined, re.S)
    if m:
        ex_block = m.group(1)
    for line in ex_block.split("\n"):
        line = line.strip()
        if not line or not re.match(r"^\d+[\.、]\s*", line):
            continue
        line = re.sub(r"^\d+[\.、]\s*", "", line)
        if "：" in line:
            t, d = line.split("：", 1)
            examples.append({"title": t.strip(), "desc": d.strip()})
        else:
            examples.append({"title": line.strip(), "desc": ""})

    m = re.search(r"^设计指令：\s*(.+)$", joined, re.M)
    if m:
        instruction = m.group(1).strip()

    return {
        "id": "R%02d" % no,
        "no": no,
        "name": en,
        "nameCn": cn,
        "category": cat,
        "tag": tag,
        "positioning": positioning,
        "desc": desc,
        "dims": dims,
        "examples": examples,
        "instruction": instruction,
        "ref": ref,
    }

for cat, blk in sections:
    r = parse_block(cat, blk)
    if r:
        recipes.append(r)

# ---------- hybrids ----------
m = re.search(r"# 七、跨风格组合方案(.*?)(?=\n# 八、)", text, re.S)
hybrids = []
if m:
    tbl = m.group(1)
    for row in re.findall(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$", tbl, re.M):
        if not row[0].startswith("组合名称") and not set(row[0]) <= set("-: "):
            raw = row[0].strip()
            mno = re.match(r"^(\d+)\.\s*(.+)$", raw)
            hybrids.append({
                "no": int(mno.group(1)) if mno else len(hybrids) + 1,
                "name": (mno.group(2) if mno else raw).strip(),
                "primary": row[1].strip(),
                "secondary": row[2].strip(),
                "expression": row[3].strip(),
            })
    ex = re.findall(r"^-\s*(.+?)[：:]\s*(.+)$", m.group(1), re.M)
    for h, (t, d) in zip(hybrids, ex):
        h["example"] = {"title": t.strip(), "desc": d.strip()}

# ---------- layouts ----------
m = re.search(r"# 八、布局与构图方案独立索引(.*?)(?=\n# 九、)", text, re.S)
layouts = []
if m:
    body = m.group(1)
    for mm in re.finditer(r"^L(\d+)\.\s*(.+?)\n\n(.+?)(?=\n\n|\Z)", body, re.M | re.S):
        layouts.append({
            "id": "L%02d" % int(mm.group(1)),
            "no": int(mm.group(1)),
            "name": mm.group(2).strip(),
            "desc": re.sub(r"\s+", " ", mm.group(3).strip()),
        })

# ---------- mapping matrix ----------
m = re.search(r"# 九、风格组合选择矩阵(.*?)(?=\n# 十、)", text, re.S)
mapping = []
if m:
    for row in re.findall(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$", m.group(1), re.M):
        if row[0].startswith("内容类型") or set(row[0]) <= set("-: "):
            continue
        mapping.append({
            "content": row[0].strip(),
            "style": row[1].strip(),
            "layouts": [x.strip() for x in re.split(r"[、,]", row[2]) if x.strip()],
            "mediums": row[3].strip(),
        })

# ---------- decision rules ----------
rules, flow = [], []
m = re.search(r"# 十、给 AI 使用的自动设计决策规范(.*?)(?=\n# 十一、)", text, re.S)
if m:
    body = m.group(1)
    mf = re.search(r"设计决策流程(.*?)设计决策的约束", body, re.S)
    if mf:
        for line in mf.group(1).split("\n"):
            line = line.strip()
            if re.match(r"^\d+[\.、]\s*", line):
                line = re.sub(r"^\d+[\.、]\s*", "", line)
                if "：" in line:
                    a, b = line.split("：", 1)
                    flow.append({"step": a.strip().rstrip("。"), "detail": b.strip()})
                else:
                    flow.append({"step": line.strip(), "detail": ""})
    mr = re.search(r"设计决策的约束\s*\n+(.*)", body, re.S)
    if mr:
        for line in mr.group(1).split("\n"):
            line = line.strip()
            if re.match(r"^\d+[\.、]\s*", line):
                rules.append(re.sub(r"^\d+[\.、]\s*", "", line))

out = {
    "categories": categories,
    "recipes": recipes,
    "hybrids": hybrids,
    "layouts": layouts,
    "mapping": mapping,
    "flow": flow,
    "rules": rules,
}
dst = os.path.join(ROOT, "src", "data", "parsed.json")
with io.open(dst, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("categories:", len(categories))
print("recipes:", len(recipes))
print("hybrids:", len(hybrids))
print("layouts:", len(layouts))
print("mapping:", len(mapping))
print("flow:", len(flow), "rules:", len(rules))
missing = [r["id"] for r in recipes if not r["dims"] or not r["examples"]]
print("incomplete:", missing)
print("sample:", json.dumps(recipes[0], ensure_ascii=False)[:400])
print("hyb0:", json.dumps(hybrids[0], ensure_ascii=False) if hybrids else None)
print("lay0:", json.dumps(layouts[0], ensure_ascii=False) if layouts else None)
