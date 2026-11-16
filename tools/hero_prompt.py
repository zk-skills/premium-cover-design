# -*- coding: utf-8 -*-
"""
hero_prompt.py —— 把配方翻译成可执行的图像提示词。

封面主视觉不允许用「几何色块 + 细线」描述，必须落到一个可命名的主体、
一种材质、一束光、一个镜头。本工具就是为了逼出这四个要素。

用法：
  python tools/hero_prompt.py --recipe R14 --aspect 3:4
  python tools/hero_prompt.py --recipe R06 --variation 2 --json
  python tools/hero_prompt.py --recipe R14 --extra "a suspended glass cube above a mirror"

输出：完整正向提示词 + 负向提示词 + 中文核对单。--variation 1/2/3 给出景别不同的三套，
用于三套候选封面。
"""
import argparse, io, json, os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(io.open(os.path.join(ROOT, "dataset", "image-prompts.json"), encoding="utf-8"))

VARIATIONS = {
    "1": ("environmental wide shot", "the subject sits small in a large field, generous negative space"),
    "2": ("tight editorial crop", "the subject fills the frame, its material texture readable at a glance"),
    "3": ("dramatic low angle", "the subject towers over the viewer, deep shadow wrapping the edges"),
}

ASPECT_HINT = {
    "3:4": "vertical 3:4 portrait composition",
    "2:3": "vertical 2:3 book cover composition",
    "1:1": "square composition",
    "4:3": "horizontal 4:3 composition",
    "16:9": "wide 16:9 cinematic composition",
}


def build(rid, aspect="3:4", variation="1", extra=""):
    r = P["recipes"].get(rid)
    if not r:
        raise SystemExit("未知配方 %s（可选 %s）" % (rid, "、".join(sorted(P["recipes"]))))
    d = P["defaults"]
    shot, framing = VARIATIONS.get(str(variation), VARIATIONS["1"])
    parts = [
        "%s of %s" % (r["medium"], r["subject"]),
        "%s, %s" % (shot, framing),
        r["composition"],
        r["light"],
        r["lens"],
        "materials: " + r["materials"],
        "color palette: " + r["palette"],
        "mood: " + r["mood"],
        d["quality"],
        d["no"],
        ASPECT_HINT.get(aspect, aspect),
    ]
    if extra:
        parts.append(extra)
    prompt = ". ".join(p.strip().rstrip(".") for p in parts if p) + "."
    negative = ", ".join([P["globalNegative"], d["negativeExtra"]])
    return {
        "recipe": rid,
        "nameCn": r["nameCn"],
        "variation": str(variation),
        "aspect": aspect,
        "prompt": prompt,
        "negative": negative,
        "checklist": {
            "单一主体": r["subject"],
            "材质": r["materials"],
            "光": r["light"],
            "镜头": r["lens"],
            "负空间": r["composition"],
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--recipe", required=True)
    ap.add_argument("--aspect", default="3:4", help="3:4 / 2:3 / 1:1 / 4:3 / 16:9")
    ap.add_argument("--variation", default="1", choices=["1", "2", "3"])
    ap.add_argument("--extra", default="", help="追加主题词，如 'a single suspended glass cube'")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    out = build(a.recipe, a.aspect, a.variation, a.extra)
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return
    print("配方 %s %s｜变体 %s｜比例 %s" % (out["recipe"], out["nameCn"], out["variation"], out["aspect"]))
    print("-" * 68)
    print("正向提示词：\n" + out["prompt"])
    print("\n负向提示词：\n" + out["negative"])
    print("\n核对单：")
    for k, v in out["checklist"].items():
        print("  %s：%s" % (k, v))
    print("\n提示：主视觉生成后必须过 tools/prepare_hero.py 做裁切与调色，再传 --hero 入封面。")


if __name__ == "__main__":
    main()
