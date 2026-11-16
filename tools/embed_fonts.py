# -*- coding: utf-8 -*-
"""
embed_fonts.py —— 把封面实际用到的字子集化，并以 base64 woff2 内嵌进 HTML。

为什么要这一步：
  系统字体栈在别人的机器上会回退成默认宋/黑，封面立刻“变味”。
  本工具按 HTML 里真正出现的文字做子集，只嵌入用到的字，通常每套几十 KB，
  单文件离线、任何机器打开都是同一套字形。

用法：
  python tools/embed_fonts.py cover.html --display xiaowei --body smiley --meta smiley
  python tools/embed_fonts.py cover.html --display fonts/ZCOOLXiaoWei-Regular.ttf \
      --body fonts/SmileySans-Oblique.ttf --out cover.html

字体 ID 来自 dataset/fonts.json；也可以直接传 .ttf/.otf 路径。
注入的家族名固定为 CoverDisplay / CoverBody / CoverMeta，原字体栈保留在后面作兜底。
"""
import argparse
import base64
import io
import json
import os
import re
import sys
import tempfile
from html.parser import HTMLParser

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_JSON = os.path.join(ROOT, "dataset", "fonts.json")

BASE_CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    " .,:;!?()[]{}<>/\\-–—_=+*&%$#@'\""
    "，。！？、；：“”‘’（）《》〈〉…·"
)

MARK_START = "/* FONT-EMBED-START */"
MARK_END = "/* FONT-EMBED-END */"


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script", "title"):
            self.skip += 1
        for k, v in attrs:
            if k == "aria-label" and v:
                self.parts.append(v)

    def handle_endtag(self, tag):
        if tag in ("style", "script", "title"):
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def collect_text(html):
    p = TextExtractor()
    p.feed(html)
    content = "".join(p.parts)
    chars = set(BASE_CHARS) | set(content)
    chars = {c for c in chars if c == " " or not c.isspace()}
    return "".join(sorted(chars)), content


def load_registry():
    if not os.path.exists(FONTS_JSON):
        return {}
    data = json.load(io.open(FONTS_JSON, encoding="utf-8"))
    return {f["id"]: f for f in data.get("fonts", [])}


def resolve_font(ref, registry):
    if not ref:
        return None
    if os.path.splitext(ref)[1].lower() in (".ttf", ".otf", ".ttc"):
        return ref
    entry = registry.get(ref)
    if not entry:
        raise SystemExit("未知字体 ID：%s（可选 %s）" % (ref, ", ".join(sorted(registry))))
    path = entry["file"]
    if not os.path.isabs(path):
        path = os.path.join(ROOT, path)
    return path


def subset_woff2(path, text):
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.name_legacy = True
    opts.notdef_outline = True
    opts.recalc_timestamp = False
    opts.drop_tables += ["DSIG"]
    font = subset.load_font(path, opts)
    try:
        sub = subset.Subsetter(options=opts)
        sub.populate(text=text)
        sub.subset(font)
        fd, tmp = tempfile.mkstemp(suffix=".woff2")
        os.close(fd)
        try:
            subset.save_font(font, tmp, opts)
            return io.open(tmp, "rb").read()
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
    finally:
        font.close()


def coverage(path, content):
    font = TTFont(path, lazy=True)
    try:
        cmap = font.getBestCmap()
        return sorted({c for c in content if c not in " \n\t" and ord(c) not in cmap})
    finally:
        font.close()


def face_css(alias, data):
    b64 = base64.b64encode(data).decode("ascii")
    return (
        "@font-face{font-family:'%s';"
        "src:url(data:font/woff2;base64,%s) format('woff2');"
        "font-weight:400;font-style:normal;font-display:block}"
        % (alias, b64)
    )


def set_font_var(html, var, alias):
    pat = re.compile(r"(%s:\s*)([^;\"]+)" % re.escape(var))
    m = pat.search(html)
    if not m:
        return html, False
    value = m.group(2).strip()
    if value.startswith("'%s'" % alias):
        return html, True
    new = "%s'%s',%s" % (m.group(1), alias, value)
    return html[:m.start()] + new + html[m.end():], True


def inject_css(html, css):
    html = re.sub(re.escape(MARK_START) + r".*?" + re.escape(MARK_END), "", html, flags=re.S)
    block = MARK_START + "\n" + css + "\n" + MARK_END + "\n"
    if "</style>" in html:
        return html.replace("</style>", block + "</style>", 1)
    if "</head>" in html:
        return html.replace("</head>", "<style>\n" + block + "</style>\n</head>", 1)
    return "<style>\n" + block + "</style>\n" + html


def embed(html, display_path, body_path=None, meta_path=None, verbose=True):
    registry = load_registry()
    body_path = body_path or display_path
    meta_path = meta_path or body_path
    roles = [("display", display_path), ("body", body_path), ("meta", meta_path)]

    text, content = collect_text(html)
    path_alias = {}
    role_alias = {}
    faces = []
    report = []

    for role, path in roles:
        if not path:
            continue
        if path not in path_alias:
            alias = "Cover" + role.capitalize()
            data = subset_woff2(path, text)
            faces.append(face_css(alias, data))
            path_alias[path] = alias
            report.append({
                "role": role, "path": path, "alias": alias,
                "source": os.path.getsize(path), "subset": len(data),
                "missing": coverage(path, content),
            })
        role_alias[role] = path_alias[path]

    var_map = {"display": "--f-display", "body": "--f-body", "meta": "--f-meta"}
    extra = []
    for role, alias in role_alias.items():
        html, ok = set_font_var(html, var_map[role], alias)
        if not ok:
            extra.append(".cover{%s:'%s'}" % (var_map[role], alias))

    html = inject_css(html, "\n".join(faces + extra))

    if verbose:
        print("字体子集嵌入：")
        for r in report:
            src_kb = r["source"] / 1024
            sub_kb = r["subset"] / 1024
            miss = (" 缺字 " + "".join(r["missing"])) if r["missing"] else ""
            print("  %-7s %-42s %7.1f KB → %6.1f KB (%.1f%%)%s" % (
                r["role"], os.path.basename(r["path"]), src_kb, sub_kb,
                sub_kb / src_kb * 100, miss))
    return html, report


def main():
    ap = argparse.ArgumentParser(description="子集化并内嵌封面字体")
    ap.add_argument("html")
    ap.add_argument("--display", required=True, help="展示字体 ID 或文件路径")
    ap.add_argument("--body", help="正文字体 ID 或文件路径")
    ap.add_argument("--meta", help="元信息字体 ID 或文件路径")
    ap.add_argument("--out", help="输出文件（默认原地覆盖）")
    ap.add_argument("--check-only", action="store_true", help="只检查缺字，不写入")
    a = ap.parse_args()

    html = io.open(a.html, encoding="utf-8").read()
    reg = load_registry()
    display = resolve_font(a.display, reg)
    body = resolve_font(a.body, reg) if a.body else display
    meta = resolve_font(a.meta, reg) if a.meta else body

    if a.check_only:
        _, content = collect_text(html)
        bad = False
        for role, path in (("display", display), ("body", body), ("meta", meta)):
            miss = coverage(path, content)
            if miss:
                bad = True
                print("%s 缺字：%s" % (role, "".join(miss)))
        print("字体覆盖检查：%s" % ("有缺字" if bad else "通过"))
        return

    before = len(html.encode("utf-8"))
    out, report = embed(html, display, body, meta)
    after = len(out.encode("utf-8"))
    if len(out.encode("utf-8")) == before:
        print("未发生替换，请确认 HTML 中是否存在 --f-display / --f-body / --f-meta")
    dest = a.out or a.html
    io.open(dest, "w", encoding="utf-8").write(out)
    print("已写入：%s（%.1f KB → %.1f KB）" % (dest, before / 1024, after / 1024))
    if any(r["missing"] for r in report):
        print("警告：存在缺字，浏览器会回退到字体栈的下一项。")


if __name__ == "__main__":
    main()
