# -*- coding: utf-8 -*-
"""
generate_cover.py —— 依据配方与布局生成单文件 HTML 封面。

这是本 Skill 的主生产工具。AI 选定配方与布局后调用本脚本，直接得到可交付的
单文件 HTML（样式内联、在线字体 CDN、内置 @page，可直接打印为 PDF）。

用法：
  python tools/generate_cover.py --recipe R01 --layout L01 \
      --title "2026 全球数字经济发展报告" \
      --subtitle "结构、变量与拐点的系统分析" \
      --kicker "产业观察" --meta1 "产业研究院" --meta2 "2026" \
      --size a4 --out cover.html

参数：
  --recipe     配方编号 R01–R26（必填）
  --layout     布局编号 L01–L16（默认 L01）
  --size       画布预设 a4/a4l/book/pub34/square/story/wide（默认 a4）
  --title/--subtitle/--kicker/--meta1/--meta2   封面文案
  --tagline    宣传语（书籍封面顶部，与 kicker 二选一）
  --author     作者署名      --org  组编／机构
  --press      出版社中文名  --press-en  出版社英文名
  --logo       出版社标志图片路径（自动转 base64）
  --credits    署名区原型 A01–A05（见 knowledge/credits-system.md，默认 A01）
  --kicker-pos 题眉位置 auto/side/topright/inline（书籍默认 inline，其余跟随布局）
  --credits-scrim A03 图文咬合时的压暗色，如 rgba(8,8,10,.6)
  --typepair   字体组合 T01–T12（见 knowledge/type-pairings.md）
  --composition 构图原型 C01–C08（见 knowledge/composition-prototypes.md）
  --hero       主视觉图片路径（正式封面的唯一来源）
  --image      同 --hero，保留兼容
  --text-only  纯文字封面，不使用主视觉
  --hero-focus "50% 40%"  裁切焦点，横向/纵向百分比
  --hero-tone  #0A1628    主视觉叠色，用于统一到配方色系
  --hero-tone-op 0.28     叠色强度 0–1
  --hero-desat 15         降低饱和度百分比
  --hero-quality 88       内嵌 JPEG 质量
  --scale      标题缩放百分比（默认 100）
  --bg/--ink/--accent/--sub   覆盖单个语义色
  --out        输出文件（默认 stdout）
"""
import argparse, io, json, os, re, sys
try: sys.stdout.reconfigure(encoding='utf-8')
except Exception: pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(io.open(os.path.join(ROOT, "dataset", "design-recipes.json"), encoding="utf-8"))
FONTDATA = json.load(io.open(os.path.join(ROOT, "dataset", "fonts.json"), encoding="utf-8"))
ONLINE = json.load(io.open(os.path.join(ROOT, "dataset", "fonts-online.json"), encoding="utf-8"))
FONTS = {f["id"]: f for f in FONTDATA["fonts"]}
OFONTS = {f["id"]: f for f in ONLINE["fonts"]}
OTP = ONLINE["typepairs"]
CN_FALLBACK = ONLINE["chineseFallbacks"]

# 未指定字体组合时，按配方给一个默认，避免回落到系统宋/黑
DEFAULT_TP = {
    "R01": "T03", "R02": "T12", "R03": "T05", "R04": "T04", "R05": "T03",
    "R06": "T02", "R07": "T13", "R08": "T14", "R09": "T02", "R10": "T19",
    "R11": "T13", "R12": "T20", "R13": "T06", "R14": "T07", "R15": "T07",
    "R16": "T23", "R17": "T04", "R18": "T04", "R19": "T17", "R20": "T07",
    "R21": "T09", "R22": "T09", "R23": "T06", "R24": "T06", "R25": "T14",
    "R26": "T03",
}

# 配方里的通用字族 → 在线字体 ID
FAMILY_TO_ONLINE = {
    "sans": "noto-sans-sc", "serif": "noto-serif-sc", "heavy": "noto-sans-sc",
    "mono": "ibm-plex-mono", "display": "shippori-mincho",
}

def font_path(ref, key=None, tp="T12"):
    """本地字体 ID 或文件路径 → 绝对路径（仅离线内嵌模式使用）。"""
    if ref:
        if os.path.splitext(ref)[1].lower() in (".ttf", ".otf", ".ttc"):
            return ref
        if ref in FONTS:
            return os.path.join(ROOT, FONTS[ref]["file"])
        raise SystemExit("未知本地字体 ID：%s" % ref)
    pair = FONTDATA["typepairs"].get(tp) or FONTDATA["typepairs"]["T12"]
    return os.path.join(ROOT, FONTS[pair[key]]["file"])


def online_font(ref, generic="sans"):
    """在线字体 ID / CSS family 名 → 字体条目。"""
    if ref in OFONTS:
        return OFONTS[ref]
    for f in ONLINE["fonts"]:
        if f["family"].lower() == str(ref).lower():
            return f
    raise SystemExit("未知在线字体：%s（可选 %s）" % (
        ref, "、".join(sorted(OFONTS)[:12]) + " …"))


def quote_stack(items):
    generic = {"sans-serif", "serif", "monospace", "system-ui", "cursive"}
    return ",".join(x if x in generic else "'%s'" % x for x in items)


def cn_stack(generic="sans"):
    return quote_stack(CN_FALLBACK.get(generic, CN_FALLBACK["sans"]))


def font_stack(font, generic=None):
    """在线字体 → CSS font-family 栈。西文字体自动补中文回退。"""
    if generic is None:
        generic = "serif" if font.get("fallbackCn") == "noto-serif-sc" else "sans"
    own = "'%s'" % font["family"]
    if font["script"] == "latin":
        fb = OFONTS.get(font.get("fallbackCn") or "")
        rest = ("'%s'," % fb["family"] if fb else "") + cn_stack(generic)
        return "%s,%s" % (own, rest)
    return "%s,%s" % (own, cn_stack(generic))


def pair_role(typepair, key, override=None):
    """返回某角色的 (字体, 字重)。"""
    p = OTP.get((typepair or "T12").upper()) or OTP["T12"]
    fid = override or p.get(key)
    weight = p.get(key + "Weight", 400)
    if override:
        f = online_font(override)
        weight = weight if weight in f["weights"] else f["weights"][0]
    return OFONTS[fid], weight


def google_url(pairs):
    """[(字体, 字重)] → Google Fonts CSS2 URL。"""
    spec = {}
    for font, weight in pairs:
        if font["source"] != "google":
            continue
        spec.setdefault(font["family"], set()).add(weight)
    if not spec:
        return ""
    parts = []
    for fam in sorted(spec):
        ws = sorted(spec[fam])
        parts.append("family=%s:wght@%s" % (fam.replace(" ", "+"), ";".join(str(w) for w in ws)))
    return "https://fonts.googleapis.com/css2?" + "&".join(parts) + "&display=swap"


def rec(rid):
    for r in DATA["recipes"]:
        if r["id"] == rid: return r
    raise SystemExit("未知配方编号：%s（可选 %s）" % (rid, ", ".join(r["id"] for r in DATA["recipes"])))

def lay(lid):
    for l in DATA["layouts"]:
        if l["id"] == lid: return l
    raise SystemExit("未知布局编号：%s（可选 %s）" % (lid, ", ".join(l["id"] for l in DATA["layouts"])))

def hex2rgb(h):
    h = (h or "#000").lstrip("#")
    if len(h) == 3: h = h[0]*2 + h[1]*2 + h[2]*2
    return [int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)]

def lum(h):
    c = []
    for v in hex2rgb(h):
        v /= 255.0
        c.append(v/12.92 if v <= 0.03928 else ((v+0.055)/1.055)**2.4)
    return 0.2126*c[0] + 0.7152*c[1] + 0.0722*c[2]

def esc(s):
    return (str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;"))

def title_markup(t):
    parts = [p for p in str(t).split("|") if p.strip()]
    return "<br>".join(esc(p.strip()) for p in parts)

CREDIT_ROLES = ("编著", "主编", "监制", "口述", "整理", "著", "编", "绘", "译", "等")
_CREDIT_RE = re.compile(r"^(.+?)[\s　]+(" + "|".join(CREDIT_ROLES) + r")$")

def person_html(s):
    """把「贾伟 著」拆成姓名与角色两级，角色词字号降一档。"""
    s = str(s or "").strip()
    m = _CREDIT_RE.match(s)
    if m:
        return ('<span class="person"><span class="name">%s</span>'
                '<span class="role">%s</span></span>' % (esc(m.group(1).strip()), esc(m.group(2))))
    return '<span class="person"><span class="name">%s</span></span>' % esc(s)

def img_src(path):
    ext = os.path.splitext(path)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    return "data:%s;base64,%s" % (mime, __import__("base64").b64encode(io.open(path,"rb").read()).decode())

def parse_focus(spec):
    """'50% 40%' / '0.5 0.4' → (fx, fy)，范围 0–1。"""
    s = str(spec or "50% 50%").strip()
    pct = "%" in s
    parts = s.replace("%", "").split()
    def num(p, default):
        try: v = float(p)
        except ValueError: return default
        if pct: v /= 100.0
        return min(1.0, max(0.0, v))
    fx = num(parts[0], 0.5)
    fy = num(parts[1], 0.5) if len(parts) > 1 else 0.5
    return fx, fy


def flatten(im, bg="#ffffff"):
    """透明图先合成到底色，否则 convert('RGB') 会把透明区压成黑色。"""
    from PIL import Image
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        base = Image.new("RGB", im.size, tuple(hex2rgb(bg)))
        base.paste(im, mask=im.getchannel("A"))
        return base
    return im.convert("RGB")


def make_hero(path, sz, a, bg="#ffffff"):
    """按封面比例裁切、可选降饱和、重编码为内嵌 JPEG。返回 (data_uri, meta)。"""
    from PIL import Image, ImageEnhance
    im = flatten(Image.open(path), bg)
    src_w, src_h = im.size
    tw, th = sz["w"], sz["h"]
    target = tw / float(th)

    if src_w / float(src_h) > target:
        nw = int(round(src_h * target)); fx, _ = parse_focus(getattr(a, "hero_focus", None))
        ox = max(0, min(src_w - nw, int(round((src_w - nw) * fx))))
        im = im.crop((ox, 0, ox + nw, src_h))
    else:
        nh = int(round(src_w / target)); _, fy = parse_focus(getattr(a, "hero_focus", None))
        oy = max(0, min(src_h - nh, int(round((src_h - nh) * fy))))
        im = im.crop((0, oy, src_w, oy + nh))

    crop_w, crop_h = im.size
    scale = max(tw / float(crop_w), th / float(crop_h))
    if scale > 1.0:
        im = im.resize((max(tw, int(round(crop_w * scale))), max(th, int(round(crop_h * scale)))),
                       Image.Resampling.LANCZOS)
    out_w, out_h = im.size

    desat = float(getattr(a, "hero_desat", 0) or 0)
    if desat:
        im = ImageEnhance.Color(im).enhance(max(0.0, 1.0 - desat / 100.0))

    import io as _io
    buf = _io.BytesIO()
    im.save(buf, "JPEG", quality=int(getattr(a, "hero_quality", 88) or 88),
            optimize=True, progressive=True)
    uri = "data:image/jpeg;base64," + __import__("base64").b64encode(buf.getvalue()).decode()

    mm = sz["mm"].split()
    mm_w = float(mm[0].replace("mm", "")); mm_h = float(mm[1].replace("mm", ""))
    dpi_w = out_w / (mm_w / 25.4); dpi_h = out_h / (mm_h / 25.4)
    meta = {
        "src": (src_w, src_h), "crop": (crop_w, crop_h), "out": (out_w, out_h),
        "scale": round(out_w / float(crop_w), 2),
        "dpi": int(round(min(dpi_w, dpi_h))), "bytes": len(buf.getvalue()),
    }
    return uri, meta


def texture_svg(kind):
    cfg = DATA["meta"]["textures"].get(kind)
    if not cfg: return ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" preserveAspectRatio="none">'
            '<filter id="tx"><feTurbulence type="fractalNoise" baseFrequency="{f}" numOctaves="4" seed="3"/>'
            '<feColorMatrix type="saturate" values="0"/></filter>'
            '<rect width="100%" height="100%" filter="url(#tx)" opacity="{o}"/></svg>').format(f=cfg["f"], o=cfg["o"])

def hybrid(no):
    for h in DATA["hybrids"]:
        if int(h["no"]) == int(no): return h
    raise SystemExit("未知组合编号 H%s（可选 %s）" % (
        no, ", ".join("H%02d" % int(h["no"]) for h in DATA["hybrids"])))

def build(a):
    sz = DATA["meta"]["sizes"][a.size]
    stacks = DATA["meta"]["fontStacks"]

    # 组合方案：主风格定调性与令牌，辅助风格只贡献具体手法
    hb = None
    if getattr(a, "hybrid", None):
        hb = hybrid(a.hybrid)
        r = rec(hb["primaryId"])
        sec = rec(hb["secondaryId"])
        tech = hb.get("technique") or {}
        lid = a.layout if getattr(a, "layout_explicit", False) else (tech.get("layoutHint") or a.layout)
        texture_src = sec if tech.get("texture") == "secondary" else r
        font_src = sec if tech.get("displayFont") == "secondary" else r
    else:
        r = rec(a.recipe)
        lid = a.layout
        texture_src = font_src = r
    L = lay(lid)

    t = dict(r["tokens"])
    for key, val in (("bg",a.bg),("ink",a.ink),("accent",a.accent),("sub",a.sub)):
        if val: t[key] = val
    tagline = getattr(a, "tagline", None)
    author = getattr(a, "author", None)
    org = getattr(a, "org", None)
    press = getattr(a, "press", None)
    press_en = getattr(a, "press_en", None)
    logo = getattr(a, "logo", None)
    typepair = getattr(a, "typepair", None)
    composition = getattr(a, "composition", None)
    full_bleed = lid in ("L05", "L13")
    has_hero = bool(getattr(a, "hero", None) or getattr(a, "image", None)) and not a.text_only
    hero_is_dark = (has_hero and bool(getattr(a, "hero_tone", None))
                    and lum(a.hero_tone) < 0.30
                    and (getattr(a, "hero_tone_op", 0) or 0) >= 0.15)
    dark = lum(t["bg"]) < 0.25 or (full_bleed and hero_is_dark)
    scrim = "rgba(10,10,14,.62)" if dark else "rgba(255,255,255,.84)"
    scrim_strong = "rgba(6,9,15,.96)" if dark else "rgba(255,255,255,.97)"

    comp_fs = {"C03": 8.6, "C04": 23.0, "C06": 10.5, "C07": 7.4, "C08": 15.5}
    base_title = comp_fs.get((composition or "").upper(), L.get("baseTitle") or 10.5)
    fs_title = round(base_title * (a.scale/100.0), 2)
    fs_sub = round(max(1.6, fs_title*0.24), 2)

    title = a.title or (r["examples"][0]["title"] if r["examples"] else r["nameCn"])
    kicker = a.kicker or ("" if (getattr(a,"tagline",None) or getattr(a,"author",None) or getattr(a,"press",None) or getattr(a,"org",None)) else r.get("tag",""))
    meta_bits = [m for m in (a.meta1, a.meta2) if m]

    hero_meta = None
    hero_path = getattr(a, "hero", None) or getattr(a, "image", None)
    if a.text_only:
        figure = ""
    elif hero_path:
        if hero_path.startswith(("http://", "https://", "data:")):
            fig_src = hero_path
        else:
            fig_src, hero_meta = make_hero(hero_path, sz, a, t["bg"])
        figure = ('<img src="%s" alt="">'
                  '<i class="cv-hero-tone"></i>'
                  '<i class="cv-hero-vignette"></i>') % esc(fig_src)
    else:
        raise SystemExit(
            "缺少主视觉：请用 --hero 传入生成图或摄影。\n"
            "  只有纯文字封面才用 --text-only。\n"
            "  出提示词：python tools/hero_prompt.py --recipe %s --aspect 2:3\n"
            "  处理图片：python tools/prepare_hero.py <原图> --size %s --out hero.jpg"
            % (a.recipe, a.size))

    # 字体：默认在线。typepair 决定三个角色的字体与字重。
    online = getattr(a, "font_mode", "online") != "local"
    if online:
        d_font, d_w = pair_role(typepair, "display", getattr(a, "font_display", None))
        b_font, b_w = pair_role(typepair, "body", getattr(a, "font_body", None))
        m_font, m_w = pair_role(typepair, "meta", getattr(a, "font_meta", None))
        tp = OTP.get((typepair or "T12").upper()) or OTP["T12"]
        font_vars = [
            "--f-display:" + font_stack(d_font),
            "--f-body:" + font_stack(b_font),
            "--f-meta:" + font_stack(m_font),
            "--fw-display:" + str(d_w), "--fw-body:" + str(b_w), "--fw-meta:" + str(m_w),
            "--tp-tracking:" + tp["tracking"], "--tp-lh:" + str(tp["lineHeight"]),
        ]
        used_fonts = [(d_font, d_w), (b_font, b_w), (m_font, m_w)]
        font_note = "在线字体 %s × %s × %s" % (d_font["name"], b_font["name"], m_font["name"])
        missing_risk = [f["name"] for f, _ in used_fonts if f["coverage"] == "han"]
    else:
        font_vars = [
            "--f-display:" + stacks.get(font_src["fonts"].get("display","sans"), stacks["sans"]),
            "--f-body:" + stacks.get(r["fonts"].get("body","sans"), stacks["sans"]),
            "--f-meta:" + stacks.get(r["fonts"].get("meta","mono"), stacks["mono"]),
        ]
        used_fonts = []
        font_note = "本地字体（离线内嵌）"
        missing_risk = []

    vars_ = ";".join([
        "--c-bg:" + t["bg"], "--c-ink:" + t["ink"], "--c-accent:" + t["accent"],
        "--c-sub:" + t["sub"], "--c-accent2:" + t["accent2"],
        *font_vars,
        "--fs-title:" + str(fs_title) + "cqw", "--fs-sub:" + str(fs_sub) + "cqw",
        "--c-scrim:" + scrim,
        "--c-scrim-strong:" + scrim_strong,
        "--c-hero-tone:" + (getattr(a, "hero_tone", None) or t["bg"]),
        "--c-hero-tone-op:" + str(getattr(a, "hero_tone_op", 0) if getattr(a, "hero_tone_op", 0) is not None else 0),
        "--c-hero-vig:" + str(getattr(a, "hero_vignette", 0.32) if getattr(a, "hero_vignette", 0.32) is not None else 0.32),
        "--crf-scrim:" + (getattr(a, "credits_scrim", None) or ("rgba(8,8,10,.58)" if dark else "rgba(245,242,235,.78)")),
        "background:" + t["bg"], "color:" + t["ink"],
    ])

    font_links = ""
    if online:
        href = google_url(used_fonts)
        font_links = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                      '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
                      '<link rel="stylesheet" href="%s">\n' % esc(href))
    a._font_note = font_note
    a._missing_risk = missing_risk
    a._used_fonts = used_fonts
    a._hero_meta = hero_meta

    # 书籍封面扩展槽位
    tagline_html = ('<div class="cv-tagline">%s</div>' % esc(tagline)) if tagline else ""
    byline_html = ""
    if author or org:
        bits = []
        if author: bits.append(person_html(author))
        if org: bits.append('<span class="org">%s</span>' % esc(org))
        byline_html = '<div class="cv-byline">%s</div>' % '<i class="sep"></i>'.join(bits)
    press_html = ""
    if logo and os.path.exists(logo):
        press_html = '<div class="cv-press"><img src="%s" alt="%s"></div>' % (
            img_src(logo), esc(press or ""))
    elif press:
        press_html = ('<div class="cv-press"><span class="cn">%s</span>'
                      '<span class="en">%s</span></div>') % (esc(press), esc(press_en or ""))
    bookfoot = ('<div class="cv-bookfoot">%s%s</div>' % (byline_html, press_html)) if (byline_html or press_html) else ""
    extra_cls = []
    if typepair: extra_cls.append("tp-" + typepair.upper())
    if composition: extra_cls.append("cp-" + composition.upper())
    credits = (getattr(a, "credits", None) or "A01").upper()
    if re.match(r"^A0[1-5]$", credits): extra_cls.append("cr-" + credits)
    kicker_pos = (getattr(a, "kicker_pos", None) or "auto").lower()
    if kicker_pos == "auto":
        # 书籍封面默认把题眉并入署名信息带，避免孤悬左上角
        kicker_pos = "inline" if a.size in ("book", "pub34", "story") else "auto"
    if kicker_pos in ("side", "topright", "inline"): extra_cls.append("ck-" + kicker_pos)
    extra_cls = (" " + " ".join(extra_cls)) if extra_cls else ""

    hero_kind = "none" if a.text_only else "image"
    cover = ('<div class="cover lay-%s%s%s" data-hero="%s" style="%s">'
             '<div class="cv-texture%s">%s</div>'
             '%s'
             '<div class="cv-frame">'
             '<div class="cv-kicker">%s</div>'
             '<div class="cv-title"><h1>%s</h1>%s</div>'
             '<div class="cv-figure">%s</div>'
             '<div class="cv-meta">%s</div>'
             '</div>%s</div>') % (
        lid, " darkink" if dark else "", extra_cls, hero_kind, vars_,
        " dark" if dark else "", texture_svg(texture_src.get("texture","none")),
        tagline_html,
        esc(kicker), title_markup(title),
        ('<p class="cv-sub">%s</p>' % esc(a.subtitle)) if a.subtitle else "",
        figure,
        '<i class="rule"></i>'.join('<span>%s</span>' % esc(m) for m in meta_bits),
        bookfoot,
    )

    css = io.open(os.path.join(ROOT, "templates", "cover.css"), encoding="utf-8").read()
    page = ('html,body{margin:0;padding:0;background:#fff}\n'
            'body{display:flex;align-items:center;justify-content:center;min-height:100vh}\n'
            '.cover{width:%dpx;height:%dpx}\n'
            '@page{size:%s;margin:0}\n'
            '@media print{body{display:block}.cover{break-inside:avoid;page-break-inside:avoid}}') % (
        sz["w"], sz["h"], sz["mm"])

    font_ready = ('<script>document.documentElement.dataset.fonts="loading";'
                  'document.fonts&&document.fonts.ready.then(function(){'
                  'document.documentElement.dataset.fonts="ready"});</script>\n')
    return ('<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '<title>%s</title>\n%s<style>\n%s\n%s\n</style>\n%s</head>\n<body>\n%s\n</body>\n</html>\n') % (
        esc(title), font_links, css, page, font_ready, cover)

def main():
    ap = argparse.ArgumentParser(description="生成单文件 HTML 封面")
    ap.add_argument("--recipe")
    ap.add_argument("--hybrid", help="跨风格组合编号 H01–H18（与 --recipe 二选一）")
    ap.add_argument("--layout", default="L01")
    ap.add_argument("--size", default="a4")
    ap.add_argument("--title"); ap.add_argument("--subtitle"); ap.add_argument("--kicker")
    ap.add_argument("--meta1"); ap.add_argument("--meta2")
    ap.add_argument("--tagline", help="宣传语")
    ap.add_argument("--author", help="作者"); ap.add_argument("--org", help="组编／机构")
    ap.add_argument("--press", help="出版社中文名"); ap.add_argument("--press-en", help="出版社英文名")
    ap.add_argument("--logo", help="出版社标志图片路径")
    ap.add_argument("--credits", choices=["A0%d" % i for i in range(1, 6)], default="A01",
                    help="署名区原型 A01–A05，见 knowledge/credits-system.md")
    ap.add_argument("--kicker-pos", choices=["auto", "side", "topright", "inline"], default="auto",
                    help="题眉位置：auto 书籍默认 inline、其余跟随布局；side 竖排贴边；topright 右上；inline 并入署名信息带")
    ap.add_argument("--credits-scrim", help="A06 图文咬合的整宽压暗色，如 rgba(8,8,10,.6)")
    ap.add_argument("--font-display", help="在线字体 ID 或 CSS family 名（默认按 typepair）")
    ap.add_argument("--font-body", help="在线字体 ID 或 CSS family 名")
    ap.add_argument("--font-meta", help="在线字体 ID 或 CSS family 名")
    ap.add_argument("--font-mode", choices=["online", "local"], default="online",
                    help="online 用在线字体（默认）；local 子集内嵌 fonts/ 下的本地字体")
    ap.add_argument("--embed-local", action="store_true",
                    help="等价于 --font-mode local，离线内嵌本地字体")
    ap.add_argument("--no-embed-fonts", action="store_true",
                    help="兼容旧参数；在线模式下本来就无需内嵌")
    ap.add_argument("--typepair", help="字体组合 T01–T12")
    ap.add_argument("--composition", help="构图原型 C01–C08")
    ap.add_argument("--hero", help="主视觉图片路径（正式交付推荐）")
    ap.add_argument("--image", help="同 --hero，兼容旧参数")
    ap.add_argument("--hero-focus", default="50% 50%", help="裁切焦点，如 '50%% 40%%'")
    ap.add_argument("--hero-tone", help="主视觉叠色，统一到配方色系")
    ap.add_argument("--hero-tone-op", type=float, default=0.0, help="叠色强度 0–1")
    ap.add_argument("--hero-desat", type=float, default=0.0, help="降低饱和度百分比")
    ap.add_argument("--hero-quality", type=int, default=88, help="内嵌 JPEG 质量")
    ap.add_argument("--hero-vignette", type=float, default=0.32, help="暗角强度 0–1")
    ap.add_argument("--text-only", "--no-motif", dest="text_only", action="store_true",
                    help="纯文字封面，不使用主视觉")
    ap.add_argument("--scale", type=int, default=100)
    ap.add_argument("--bg"); ap.add_argument("--ink"); ap.add_argument("--accent"); ap.add_argument("--sub")
    ap.add_argument("--out")
    ap.add_argument("--fit", action="store_true", help="生成后自动缩放标题以消除溢出（需 Playwright）")
    a = ap.parse_args()
    if not a.recipe and not a.hybrid:
        raise SystemExit("必须指定 --recipe R01–R26 或 --hybrid H01–H18")
    if a.hybrid:
        hb = hybrid(a.hybrid)
        a.recipe = hb["primaryId"]
        a.layout_explicit = a.layout != "L01"
    if a.embed_local:
        a.font_mode = "local"
    if not a.typepair:
        a.typepair = DEFAULT_TP.get(a.recipe, "T12")
    html = build(a)
    if a.out:
        with io.open(a.out, "w", encoding="utf-8") as f: f.write(html)
        r = rec(a.recipe); L = lay(a.layout)
        if a.hybrid:
            hb = hybrid(a.hybrid)
            tech = hb.get("technique") or {}
            if not a.layout_explicit and tech.get("layoutHint"):
                L = lay(tech["layoutHint"])
        print("已生成：%s" % a.out)
        if a.hybrid:
            hb = hybrid(a.hybrid)
            print("  组合 H%02d %s（主 %s + 辅 %s）" % (int(hb["no"]), hb["name"], hb["primary"], hb["secondary"]))
            print("  手法 %s" % hb["expression"])
        print("  配方 %s %s｜%s" % (r["id"], r["name"], r["nameCn"]))
        print("  布局 %s %s" % (L["id"], L["name"]))
        print("  署名区 %s｜题眉 %s" % (a.credits, a.kicker_pos))
        print("  画布 %s（%dx%d）" % (DATA["meta"]["sizes"][a.size]["label"], DATA["meta"]["sizes"][a.size]["w"], DATA["meta"]["sizes"][a.size]["h"]))
        print("  令牌 bg %s · ink %s · accent %s · sub %s" % (
            r["tokens"]["bg"], r["tokens"]["ink"], r["tokens"]["accent"], r["tokens"]["sub"]))
        print("  字体 %s" % getattr(a, "_font_note", ""))
        hm = getattr(a, "_hero_meta", None)
        if hm:
            print("  主视觉 %dx%d → 裁切 %dx%d → 输出 %dx%d（放大 %.2f×，约 %ddpi，内嵌 %dKB）" % (
                hm["src"][0], hm["src"][1], hm["crop"][0], hm["crop"][1],
                hm["out"][0], hm["out"][1], hm["scale"], hm["dpi"], hm["bytes"]//1024))
            if hm["dpi"] < 300:
                mm_w = float(DATA["meta"]["sizes"][a.size]["mm"].split()[0].replace("mm", ""))
                print("  提示：整幅出血仅 %ddpi。印刷需 %dpx 宽；屏幕交付可忽略。"
                      % (hm["dpi"], int(round(mm_w/25.4*300))))
        if getattr(a, "_missing_risk", None):
            print("  注意 %s 属日文汉字字体，个别简体字可能缺失；交付前跑 check_fonts.py --online" %
                  "、".join(a._missing_risk))
        if a.fit:
            import subprocess
            out = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "fit_cover.py"), a.out, "--apply"],
                                 capture_output=True, encoding="utf-8", errors="replace")
            msg = (out.stdout or "").strip()
            print("  自适应：%s" % (msg.replace("\n", " ") if msg else "未执行（需 Playwright）"))
        if a.font_mode == "local":
            from embed_fonts import embed as embed_fonts
            html2 = io.open(a.out, encoding="utf-8").read()
            out_html, _ = embed_fonts(
                html2,
                font_path(a.font_display, "display", a.typepair),
                font_path(a.font_body, "body", a.typepair),
                font_path(a.font_meta, "meta", a.typepair),
            )
            io.open(a.out, "w", encoding="utf-8").write(out_html)
    else:
        if a.font_mode == "local":
            from embed_fonts import embed as embed_fonts
            html, _ = embed_fonts(
                html,
                font_path(a.font_display, "display", a.typepair),
                font_path(a.font_body, "body", a.typepair),
                font_path(a.font_meta, "meta", a.typepair),
            )
        sys.stdout.write(html)

if __name__ == "__main__":
    main()
