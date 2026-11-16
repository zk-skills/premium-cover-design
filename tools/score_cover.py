# -*- coding: utf-8 -*-
"""
score_cover.py —— 封面视觉表现自评。补 verify_cover.py 管不到的“好不好看”。

用法：
  python tools/score_cover.py cover.html

输出五项各 20 分，总分 100。这是建议性评分，不阻断交付；
60 分以下通常意味着版式过于默认，建议重做构图或字体。
"""
import argparse, io, re, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

TYPES = {f"T{i:02d}" for i in range(1, 13)}
COMPS = {f"C{i:02d}" for i in range(1, 9)}


def text_of(html, cls):
    m = re.search(r'<[a-z]+ class="%s"[^>]*>(.*?)</[a-z]+>' % cls, html, re.S)
    if not m: return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))).strip()


def main(path, track="premium"):
    html = io.open(path, encoding="utf-8").read()
    style = html[html.find("<style>"):html.find("</style>")] if "<style>" in html else ""
    cover_tag = re.search(r'<div class="cover([^"]*)"', html)
    classes = cover_tag.group(1).split() if cover_tag else []
    lay = next((c for c in classes if c.startswith("lay-")), "")
    tp = next((c for c in classes if c.startswith("tp-")), "")
    cp = next((c for c in classes if c.startswith("cp-")), "")

    def cssvar(name):
        m = re.search(r"--%s:\s*([\d.]+)cqw" % name, html)
        return float(m.group(1)) if m else None

    fs_title, fs_sub = cssvar("fs-title"), cssvar("fs-sub")
    tm = re.search(r"<h1>(.*?)</h1>", html, re.S)
    if tm:
        title = re.sub(r"<[^>]+>", "", tm.group(1)).strip()
    else:
        am = re.search(r'<div class="cv-title">.*?<svg[^>]*aria-label="([^"]*)"', html, re.S)
        title = am.group(1).strip() if am else ""
    sub = text_of(html, "cv-sub")

    rows, total = [], 0

    # 1 层级落差：书名 / 副标题
    if fs_title and fs_sub and fs_sub > 0:
        ratio = fs_title / fs_sub
        if ratio >= 2.2: pts, note = 20, "层级比 %.2f，主次清楚" % ratio
        elif ratio >= 1.8: pts, note = 14, "层级比 %.2f，副标题偏大" % ratio
        else: pts, note = 7, "层级比 %.2f，标题与副标题在打架" % ratio
    else:
        pts, note = 8, "缺少副标题字号，层级无法判断"
    rows.append(("层级落差", pts, note)); total += pts

    # 2 标题权重：书名占画布短边，按轨道取阈值
    if track == "auto":
        track = "mass" if (fs_title and fs_title >= 24) else "premium"
    if fs_title:
        if track == "mass":
            if 26 <= fs_title <= 40: pts, note = 20, "货架轨 · 书名占短边 %.1f%%，主角明确" % fs_title
            elif 20 <= fs_title < 26: pts, note = 16, "货架轨 · 书名占短边 %.1f%%，可再放大" % fs_title
            elif 40 < fs_title <= 46: pts, note = 14, "货架轨 · 书名占短边 %.1f%%，需裁切支撑" % fs_title
            elif 12 <= fs_title < 20: pts, note = 10, "货架轨 · 书名占短边 %.1f%%，货架首读偏弱" % fs_title
            else: pts, note = 6, "货架轨 · 书名占短边 %.1f%%，撑不住封面" % fs_title
        else:
            if 12 <= fs_title <= 26: pts, note = 20, "气质轨 · 书名占短边 %.1f%%，有主角感" % fs_title
            elif 9 <= fs_title < 12: pts, note = 13, "气质轨 · 书名占短边 %.1f%%，偏小" % fs_title
            elif fs_title > 26: pts, note = 14, "气质轨 · 书名占短边 %.1f%%，需要用裁切或出血支撑" % fs_title
            else: pts, note = 6, "气质轨 · 书名占短边 %.1f%%，撑不住封面" % fs_title
    else:
        pts, note = 6, "未读到书名字号"
    rows.append(("标题权重", pts, note)); total += pts

    # 3 字体气质：是否显式选择字体组合
    if tp:
        pts, note = 20, "使用 %s，字重与字距有明确主张" % tp
    elif re.search(r"letter-spacing", style) and re.search(r"font-weight", style):
        pts, note = 11, "未指定字体组合，沿用默认 700 字重"
    else:
        pts, note = 4, "字体几乎未配置"
    rows.append(("字体气质", pts, note)); total += pts

    # 4 构图张力
    if cp:
        pts, note = 20, "使用 %s，构图有明确重心" % cp
    elif lay in ("lay-L05", "lay-L13") and "<img" in html:
        pts, note = 16, "满版摄影，图像本身承担构图"
    elif lay and lay not in ("lay-L01", "lay-L02"):
        pts, note = 12, "使用 %s，仍是网格分配型构图" % lay
    else:
        pts, note = 5, "基础网格，缺少张力或偏心"
    rows.append(("构图张力", pts, note)); total += pts

    # 5 克制度：颜色、焦点、装饰
    colors = set(re.findall(r"#[0-9A-Fa-f]{6}", style)) | set(re.findall(r"#[0-9A-Fa-f]{6}", html[:2000]))
    foci = sum(1 for c in ("cv-title", "cv-figure", "cv-tagline", "cv-bookfoot", "cv-kicker") if c in html)
    latin = re.findall(r"[A-Za-z]{4,}", text_of(html, "cv-kicker") + " " + text_of(html, "cv-meta"))
    penalty = max(0, len(colors) - 5) * 3 + max(0, foci - 3) * 3 + min(6, len(set(latin)))
    pts = max(0, 20 - penalty)
    note = "颜色 %d 种 · 焦点 %d 个" % (len(colors), foci)
    rows.append(("克制度", pts, note)); total += pts

    print("封面视觉表现评分：%s" % path)
    print("  轨道：%s · 标题「%s」 · 副标题「%s」" % (
        "货架轨" if track == "mass" else "气质轨", title[:20], sub[:24]))
    print("-" * 60)
    for name, pts, note in rows:
        print("  %-6s %2d/20  %s" % (name, pts, note))
    print("-" * 60)
    print("  总分 %d/100" % total)
    if total < 60:
        print("  结论：版式过于默认，建议换字体组合或构图原型后重做。")
    elif total < 80:
        print("  结论：可用，但还有明显的默认感，优先调整构图或标题权重。")
    else:
        print("  结论：视觉主张清楚，进入细节校对。")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="封面视觉表现自评")
    ap.add_argument("html")
    ap.add_argument("--track", choices=["premium", "mass", "auto"], default="premium",
                    help="气质轨 / 货架轨 / 按标题大小自动判断")
    a = ap.parse_args()
    sys.exit(main(a.html, a.track))
