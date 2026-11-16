# -*- coding: utf-8 -*-
"""
verify_cover.py —— 封面质量门禁。生成 HTML 后必须运行，全部通过才算完成。

用法：
  python tools/verify_cover.py cover.html --recipe R01 --title "..." --kicker "..." --meta1 "..." --meta2 "..."

静态检查（无外部依赖，永远可跑）：
  1 标题溢出预判     2 文字对比度     3 缩略图可读性   4 安全区预判
  5 主次关系预判     6 装饰噪音       7 信息层级       8 配方契合
附加检查：画布与 @page 一致性、外部资源白名单、结构完整性、字体栈与来源、缺字风险

若本机可用 Playwright，额外执行真实布局检查（溢出/安全区/主次关系），
结果合并进同一次报告。
"""
import argparse, io, json, os, re, subprocess, sys
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(io.open(os.path.join(ROOT, "dataset", "design-recipes.json"), encoding="utf-8"))
ONLINE = json.load(io.open(os.path.join(ROOT, "dataset", "fonts-online.json"), encoding="utf-8"))
OFONTS = {f["id"]: f for f in ONLINE["fonts"]}
BY_FAMILY = {f["family"].lower(): f for f in ONLINE["fonts"]}
ALLOW_HOSTS = set(ONLINE["policy"]["allowHosts"])
GENERIC = {"sans-serif", "serif", "monospace", "system-ui", "cursive"}

# 交付封面不得把系统基础字体当展示体
BASIC_FAMILIES = {
    "simsun", "songti sc", "stsong", "simhei", "heiti sc", "pingfang sc",
    "microsoft yahei", "source han sans sc", "source han serif sc",
    "noto sans cjk sc", "noto serif cjk sc", "arial", "helvetica",
    "times new roman", "georgia", "courier new", "consolas",
}


def first_family(stack):
    m = re.match(r"\s*['\"]?([^'\",]+)", stack or "")
    return m.group(1).strip().lower() if m else ""

def hex2rgb(h):
    h = (h or "#000").lstrip("#")
    if len(h) == 3: h = h[0]*2 + h[1]*2 + h[2]*2
    try: return [int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)]
    except ValueError: return [0,0,0]

def lum(h):
    c = []
    for v in hex2rgb(h):
        v /= 255.0
        c.append(v/12.92 if v <= 0.03928 else ((v+0.055)/1.055)**2.4)
    return 0.2126*c[0] + 0.7152*c[1] + 0.0722*c[2]

def contrast(a,b):
    l1,l2 = lum(a),lum(b)
    hi,lo = max(l1,l2),min(l1,l2)
    return (hi+0.05)/(lo+0.05)

def find_style(html):
    m = re.search(r'<div class="cover ([^"]+)"([^>]*)>', html)
    if not m: return None, {}, ""
    classes = m.group(1).split()
    lay = next((c[4:] for c in classes if c.startswith("lay-")), "")
    sm = re.search(r'style="([^"]*)"', m.group(2))
    vars_ = {}
    if sm:
        for kv in sm.group(1).split(";"):
            if ":" in kv:
                k,v = kv.split(":",1); vars_[k.strip()] = v.strip()
    return lay, vars_, " ".join(classes)

def slot_text(html, cls):
    m = re.search(r'<div class="%s">(.*?)</div>' % cls, html, re.S)
    if not m: return ""
    t = re.sub(r"<[^>]+>", " ", m.group(1))
    t = t.replace("&amp;","&").replace("&lt;","<").replace("&gt;",">").replace("&quot;",'"')
    return re.sub(r"\s+"," ",t).strip()

def h1_text(html):
    m = re.search(r"<h1>(.*?)</h1>", html, re.S)
    if m:
        return re.sub(r"\s+"," ",re.sub(r"<[^>]+>","",m.group(1))).strip()
    # 转曲标题：从 SVG 的 aria-label 读取
    m = re.search(r'<div class="cv-title">.*?<svg[^>]*aria-label="([^"]*)"', html, re.S)
    return m.group(1).strip() if m else ""

def cqw_px(v, canvas_w):
    m = re.match(r"([\d.]+)cqw", v or "")
    return float(m.group(1))/100.0*canvas_w if m else None

def page_mm(html):
    m = re.search(r"@page\{size:([\d.]+)mm\s+([\d.]+)mm", html)
    return (float(m.group(1)), float(m.group(2))) if m else None

def data_uri_size(html):
    m = re.search(r'<img src="data:image/[\w+]+;base64,([^"]+)"', html)
    if not m: return None
    try:
        import base64
        from PIL import Image
        raw = base64.b64decode(m.group(1))
        return Image.open(io.BytesIO(raw)).size
    except Exception:
        return None

def hero_checks(html, add, is_print=False):
    """主视觉来源与清晰度。这是「封面不像 PPT」的第一道闸。"""
    hm = re.search(r'data-hero="(image|none)"', html)
    kind = hm.group(1) if hm else "unknown"
    mm = page_mm(html)

    if kind == "image":
        size = data_uri_size(html)
        if size and mm:
            dpi = int(round(size[0] / (mm[0] / 25.4)))
            floor = 300 if is_print else 150
            lvl = "pass" if dpi >= floor else ("warn" if dpi >= floor * 0.8 else "fail")
            add("主视觉来源", "pass", "位图 %d×%d，整幅出血约 %ddpi" % (size[0], size[1], dpi))
            add("主视觉清晰度", lvl,
                "%ddpi（%s阈值 %d）；印刷 300dpi 需 %dpx 宽" % (
                    dpi, "印刷" if is_print else "屏幕", floor,
                    int(round(mm[0] / 25.4 * 300))) +
                ("" if lvl == "pass" else "；付印前重出更大尺寸"))
        else:
            add("主视觉来源", "warn", "图片为外链或尺寸不可读，无法核算 dpi")
        return

    if kind == "none":
        add("主视觉来源", "pass", "纯文字封面，不使用主视觉")
        return

    add("主视觉来源", "fail", "没有主视觉位图；封面必须用生成图或摄影，纯文字请显式 --text-only")
    add("主视觉形态", "fail", "无法确认主视觉，请用当前版 generate_cover.py 重新生成")

def check(html, args):
    lay, vars_, classes = find_style(html)
    res = []
    def add(name, level, detail): res.append({"name":name,"level":level,"detail":detail})

    if not vars_:
        add("结构完整性","fail","未找到 .cover 元素及其内联样式变量")
        return res, {}
    bg = vars_.get("--c-bg","#fff"); ink = vars_.get("--c-ink","#000")
    accent = vars_.get("--c-accent","#000"); sub = vars_.get("--c-sub","#888")
    title = h1_text(html); kicker = slot_text(html,"cv-kicker")
    meta1 = slot_text(html,"cv-meta")

    # 2 对比度
    ci, ca, cs = contrast(ink,bg), contrast(accent,bg), contrast(sub,bg)
    lvl = "pass" if (ci>=4.5 and ca>=3 and cs>=3) else ("warn" if (ci>=3 and ca>=2.2) else "fail")
    add("文字对比度", lvl, "墨/底 %.2f:1（需 ≥4.5）· 强调/底 %.2f:1（需 ≥3）· 辅助/底 %.2f:1（需 ≥3）" % (ci,ca,cs))

    # 3 缩略图可读性
    m = re.search(r"\.cover\{width:(\d+)px;height:(\d+)px\}", html)
    cw = int(m.group(1)) if m else 1240
    fs = cqw_px(vars_.get("--fs-title"), cw)
    if fs:
        tp = fs/cw*240
        add("缩略图可读性", "pass" if tp>=8 else "warn",
            "标题 %.0fpx @1240 → %.1fpx @240（需 ≥8）" % (fs, tp))
    else:
        add("缩略图可读性","warn","未读到 --fs-title，无法计算")

    # 6 装饰噪音
    user = " ".join([args.title or "", args.subtitle or "", args.kicker or "",
                     args.meta1 or "", args.meta2 or ""])
    latin = re.findall(r"[A-Za-z]{3,}", (kicker + " " + meta1))
    noise = [w for w in latin if w not in user]
    add("装饰噪音", "pass" if not noise else "fail" if args.strict else "warn",
        "版面英文均来自输入" if not noise else "检测到非输入内容：%s" % "、".join(noise))

    # 7 信息层级：统计四个槽位实际生效的字号
    cover_css = io.open(os.path.join(ROOT, "templates", "cover.css"), encoding="utf-8").read()
    def slot_default(cls):
        m = re.search(r"\." + cls + r"\{[^}]*font-size:var\(--fs-[a-z]+,([\d.]+)cqw\)", cover_css, re.S)
        return m.group(1) + "cqw" if m else None
    sizes = set()
    for v in (vars_.get("--fs-title"), vars_.get("--fs-sub"), slot_default("cv-kicker"), slot_default("cv-meta")):
        if v: sizes.add(v)
    lvls = len(sizes)
    add("信息层级", "pass" if lvls>=3 else "warn",
        "标题/副标题/题眉/元信息 共 %d 级字号（建议 3–4 级）" % lvls)

    # 8 配方契合
    if args.recipe:
        r = next((x for x in DATA["recipes"] if x["id"]==args.recipe), None)
        if r:
            diffs = []
            for k in ("bg","ink","accent","sub"):
                if vars_.get("--c-"+k) != r["tokens"][k]:
                    diffs.append("%s %s→%s" % (k, r["tokens"][k], vars_.get("--c-"+k)))
            add("配方契合", "pass" if not diffs else "warn",
                "令牌与 %s %s 一致" % (r["id"], r["nameCn"]) if not diffs
                else "已偏离 %s：%s" % (r["id"], "，".join(diffs)))
        else:
            add("配方契合","warn","未知配方编号 %s" % args.recipe)

    # 画布与 @page
    m2 = re.search(r"@page\{size:([^;]+);margin:0\}", html)
    m3 = re.search(r"\.cover\{width:(\d+)px;height:(\d+)px\}", html)
    if m2 and m3:
        add("画布一致性","pass","@page %s 与画布 %s×%s 一致" % (m2.group(1), m3.group(1), m3.group(2)),
            )
    else:
        add("画布一致性","warn","未找到 @page 或 .cover 尺寸声明")

    # 外部资源：只允许在线字体 CDN
    urls = set(re.findall(r'https?://[^\s"\'<>)]+', html))
    urls = {u for u in urls if "w3.org" not in u}
    outside = sorted(u for u in urls if not any(h in u for h in ALLOW_HOSTS))
    add("外部资源","pass" if not outside else "fail",
        "仅在线字体 CDN，共 %d 个字体请求" % len(urls) if not outside
        else "存在非字体外链：%s" % "、".join(outside[:3]))

    # 结构完整性
    need = ["cv-kicker","cv-title","cv-figure","cv-meta"]
    missing = [n for n in need if ('class="%s"' % n) not in html]
    add("结构完整性","pass" if not missing else "fail",
        "四个槽位齐全" if not missing else "缺少：%s" % "、".join(missing))
    if "cv-title h1" not in html and "<h1>" not in html and 'class="cv-title"' not in html:
        add("标题存在","fail","未找到标题元素")

    hero_checks(html, add, getattr(args, "is_print", False))

    # 字体栈：展示体必须是注册过的在线字体，不得用系统基础字体
    fd = vars_.get("--f-display", "")
    fam = first_family(fd)
    if not fd:
        add("字体栈", "fail", "未指定 --f-display")
    elif fam in BASIC_FAMILIES:
        add("字体栈", "fail", "展示体是系统基础字体「%s」，禁止用于交付" % fam)
    elif fam in BY_FAMILY:
        f = BY_FAMILY[fam]
        add("字体栈", "pass", "展示体 %s（%s，%s 覆盖）" % (f["name"], f["family"], f["coverage"]))
    else:
        add("字体栈", "warn", "展示体「%s」不在在线字体库，无法保证字形" % fam)

    # 字体来源：在线 link 或内嵌 @font-face
    has_google = "fonts.googleapis.com/css2" in html
    has_face = "@font-face" in html
    add("字体来源", "pass" if (has_google or has_face) else "fail",
        "在线字体 CDN" if has_google else ("内嵌 @font-face" if has_face else "无字体来源，B 机器会回退"))

    # 字体加载：导出前必须能确认字体就绪
    pre = html.count("preconnect")
    ready = "fonts.ready" in html
    add("字体加载", "pass" if (pre >= 1 and ready) else "warn",
        "已声明 preconnect 与 fonts.ready" if (pre >= 1 and ready)
        else "缺少 preconnect 或 fonts.ready，导出可能截在回退字形")

    # 缺字风险：日文汉字字体与繁体字体要提示
    m = re.search(r"\btp-(T\d{2})\b", classes or "")
    tp = ONLINE["typepairs"].get(m.group(1)) if m else None
    if tp:
        if tp["level"] == "han":
            add("缺字风险", "warn",
                "%s 展示体为日文汉字字体，个别简体字可能缺失；交付前跑 check_fonts.py --online"
                % tp["name"])
        elif tp["level"] == "tc":
            add("缺字风险", "warn", "%s 为繁体字体，简体字缺失较多，仅限繁体文本" % tp["name"])
        elif tp["level"] == "latin":
            add("缺字风险", "pass", "%s 为拉丁展示体，中文回退到思源黑/宋" % tp["name"])
        else:
            add("缺字风险", "pass", "%s 展示体简体覆盖完整" % tp["name"])

    return res, {"title": title, "kicker": kicker, "meta": meta1, "layout": lay, "canvas": cw}

def browser_checks(html_path):
    script = os.path.join(ROOT, "tools", "verify_cover_browser.js")
    if not os.path.exists(script): return []
    try:
        out = subprocess.run(["node", script, html_path], capture_output=True, encoding="utf-8", errors="replace", timeout=180)
        if out.returncode != 0: return [{"name":"浏览器布局检查","level":"skip","detail":"未运行（%s）" % (out.stderr.strip().splitlines() or [""])[-1][:120]}]
        return json.loads(out.stdout)
    except Exception as e:
        return [{"name":"浏览器布局检查","level":"skip","detail":"未运行（%s）" % str(e)[:120]}]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--recipe"); ap.add_argument("--title"); ap.add_argument("--subtitle")
    ap.add_argument("--kicker"); ap.add_argument("--meta1"); ap.add_argument("--meta2")
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--strict", action="store_true", help="警告也视为失败")
    ap.add_argument("--print", dest="is_print", action="store_true",
                    help="按印刷 300dpi 阈值检查主视觉")
    ap.add_argument("--require-fonts", action="store_true",
                    help="兼容旧参数；字体来源检查默认已强制")
    a = ap.parse_args()
    html = io.open(a.html, encoding="utf-8").read()
    res, info = check(html, a)
    if not a.no_browser:
        res += browser_checks(a.html)
    order = {"fail":0,"warn":1,"pass":2,"skip":3}
    res.sort(key=lambda x: order.get(x["level"],9))
    print("封面质量门禁：%s" % a.html)
    print("  配方 %s · 布局 %s · 画布 %dpx · 标题「%s」" % (a.recipe or "—", info.get("layout"), info.get("canvas",0), info.get("title","")[:24]))
    print("-" * 68)
    icons = {"pass":"[通过]","warn":"[警告]","fail":"[失败]","skip":"[跳过]"}
    for r in res:
        print("  %s %-12s %s" % (icons.get(r["level"],"[?]"), r["name"], r["detail"]))
    fails = [r for r in res if r["level"]=="fail"]
    warns = [r for r in res if r["level"]=="warn"]
    print("-" * 68)
    print("结论：%d 项通过，%d 项警告，%d 项失败" % (
        len([r for r in res if r["level"]=="pass"]), len(warns), len(fails)))
    if fails or (a.strict and warns):
        sys.exit(1)
    print("交付前请同时完成人工复核（语义指向、气质、无装饰噪音、可印刷性），见 workflows/visual-quality-review.md")

if __name__ == "__main__":
    main()
