# -*- coding: utf-8 -*-
"""
build_font_specimen_online.py —— 生成在线字体样张 HTML。

把 dataset/fonts-online.json 里的字体按覆盖等级分组铺成一张样张页，
浏览器打开时从 Google Fonts 实时加载，用来肉眼核对字形、字重与气质。

用法：
  python tools/build_font_specimen_online.py --out font-specimen.html
  python tools/build_font_specimen_online.py --out specimen.html --level sc,han
"""
import argparse
import io
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "dataset", "fonts-online.json")

TITLES = {
    "sc": ("A 级 · 简体全覆盖", "86 个常用简体字实测 100% 命中，可用于任意简体标题。"),
    "han": ("B 级 · 东亚汉字", "日文字体，缺部分简体专用字；短标题可用，交付前必须检测。"),
    "tc": ("C 级 · 繁体", "港台字形，简体字缺失较多，只用于繁体文本。"),
    "latin": ("D 级 · 拉丁展示体", "只覆盖西文，中文自动回退到指定中文字体。"),
}


def links(fonts):
    out, batch = [], []
    for f in fonts:
        ws = f["weights"]
        batch.append("family=%s:wght@%s" % (
            f["family"].replace(" ", "+"), ";".join(str(w) for w in ws)))
        if len(batch) == 12:
            out.append("&".join(batch))
            batch = []
    if batch:
        out.append("&".join(batch))
    return "\n".join(
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?%s&display=swap">' % b
        for b in out)


def stack(font):
    own = "'%s'" % font["family"]
    if font["script"] == "latin":
        cn = "'Noto Serif SC'" if font.get("fallbackCn") == "noto-serif-sc" else "'Noto Sans SC'"
        return "%s,%s,sans-serif" % (own, cn)
    return "%s,'Noto Sans SC',sans-serif" % own


def card(f):
    sample = "三品合一" if f["coverage"] != "latin" else "Aa Bb 0123"
    note = "中文回退思源宋" if f.get("fallbackCn") == "noto-serif-sc" else (
        "中文回退思源黑" if f["script"] == "latin" else "")
    w0, w1 = f["weights"][0], f["weights"][-1]
    wtxt = str(w0) if w0 == w1 else "%d–%d" % (w0, w1)
    return (
        '<article class="card">'
        '<header><b>%s</b><em>%s</em></header>'
        '<div class="meta"><code>%s</code><span>%s</span><span>%s</span>'
        '<span>%s</span></div>'
        '<div class="sample %s" style="font-family:%s">%s</div>'
        '<div class="sub" style="font-family:%s">破局内卷的品类增长战法</div>'
        '<footer>%s</footer>'
        '</article>') % (
        f["name"], f["family"], f["id"], f["coverage"],
        f["traits"].split()[0], wtxt,
        "latin" if f["script"] == "latin" else "",
        stack(f), sample, stack(f), note)


def build(levels):
    reg = json.load(io.open(REG, encoding="utf-8"))
    fonts = [f for f in reg["fonts"] if not levels or f["coverage"] in levels]
    sections = []
    for code in ("sc", "han", "tc", "latin"):
        part = [f for f in fonts if f["coverage"] == code]
        if not part:
            continue
        title, desc = TITLES[code]
        sections.append('<section><h2>%s <small>%d 个</small></h2><p>%s</p><div class="grid">%s</div></section>'
                        % (title, len(part), desc, "".join(card(f) for f in part)))
    return (
        '<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>在线字体样张 · %d 个</title>'
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '%s'
        '<style>'
        '*{box-sizing:border-box}'
        'body{margin:0;padding:48px;background:#F4F1EA;color:#1B1B1B;'
        "font-family:'Noto Sans SC',sans-serif}"
        'h1{font-size:34px;margin:0 0 6px}'
        '.lead{color:#6B665C;margin:0 0 40px;font-size:14px}'
        'h2{font-size:20px;margin:44px 0 6px;padding-top:18px;border-top:2px solid #1B1B1B}'
        'h2 small{font-size:12px;color:#8A8375;font-weight:400;margin-left:8px}'
        'section>p{margin:0 0 18px;color:#6B665C;font-size:13px}'
        '.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}'
        '.card{background:#fff;border:1px solid #DED8CC;padding:16px 18px 12px;'
        'display:flex;flex-direction:column;min-height:230px}'
        '.card header{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}'
        '.card header b{font-size:15px}'
        '.card header em{font-style:normal;font-size:11px;color:#8A8375}'
        '.meta{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0 14px;'
        'font-family:"IBM Plex Mono",monospace;font-size:10px;color:#8A8375}'
        '.meta code{color:#B4552D}'
        '.sample{font-size:54px;line-height:1.12;white-space:nowrap;margin-top:auto}'
        '.sample.latin{font-size:44px}'
        '.sub{font-size:15px;color:#5C574D;margin-top:6px;opacity:.85}'
        '.card footer{margin-top:12px;padding-top:8px;border-top:1px solid #EFEAE0;'
        'font-size:10px;color:#9A9385}'
        '</style></head><body>'
        '<h1>在线字体样张</h1>'
        '<p class="lead">%d 个 Google Fonts 在线字体 · 打开时实时加载 · 缺字会回退到思源黑/宋</p>'
        '%s</body></html>') % (
        len(fonts), links(fonts), len(fonts), "".join(sections))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="font-specimen.html")
    ap.add_argument("--level", default="", help="只输出指定级别，逗号分隔：sc,han,tc,latin")
    a = ap.parse_args()
    levels = {x.strip() for x in a.level.split(",") if x.strip()}
    html = build(levels)
    io.open(a.out, "w", encoding="utf-8").write(html)
    print("已生成：%s（%d KB）" % (a.out, len(html.encode("utf-8")) // 1024))


if __name__ == "__main__":
    main()
