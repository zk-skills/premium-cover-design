# -*- coding: utf-8 -*-
"""
text_to_svg.py —— 把标题转成矢量图形，供封面使用。文字不再是“文本”，而是图形。

支持：
  实色填充 / 线性渐变 / 图片材质填充 / 描边 / 多层偏移 / 逐字旋转 / 竖排

用法：
  python tools/text_to_svg.py --text "三品合一" \
    --font fonts/LXGWWenKai-Regular.ttf --size 240 \
    --gradient "#E9D6AE,#8C6B35" --output title.svg

  # 用图片填充文字
  python tools/text_to_svg.py --text "三品合一" --font fonts/LXGWWenKai-Regular.ttf \
    --image texture_three.jpg --output title.svg

输出 SVG 可直接内嵌到封面 HTML，印刷为矢量，不依赖客户端字体。
"""
import argparse, base64, io, os, sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from fontTools.ttLib import TTFont, TTCollection
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform


def load_font(path, index=0):
    if path.lower().endswith(".ttc"):
        coll = TTCollection(path)
        return coll.fonts[index]
    return TTFont(path)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build(args):
    font = load_font(args.font, args.font_index)
    glyphset = font.getGlyphSet()
    cmap = font.getBestCmap()
    upem = font["head"].unitsPerEm
    scale = args.size / upem

    lines = args.text.split("|")
    tracking = args.tracking * args.size
    line_gap = args.line_height * args.size

    paths = []
    max_w = 0
    for li, line in enumerate(lines):
        x = 0.0
        y = li * line_gap
        for ci, ch in enumerate(line):
            gname = cmap.get(ord(ch))
            if not gname:
                x += args.size
                continue
            pen = SVGPathPen(glyphset)
            # 字体坐标 y 向上，SVG y 向下；逐字可单独旋转
            base = Transform(scale, 0, 0, -scale, x, y + args.size * 0.86)
            if args.rotate and ci == args.rotate_index:
                cx, cy = x + args.size / 2, y + args.size / 2
                base = base.translate(cx, cy).rotate(args.rotate).translate(-cx, -cy)
            glyphset[gname].draw(TransformPen(pen, base))
            d = pen.getCommands()
            if d:
                paths.append((d, x, y))
            x += args.size + tracking
        max_w = max(max_w, x - tracking)

    width = max_w
    height = len(lines) * line_gap + args.size * 0.2
    pad = args.padding
    vb_w, vb_h = width + pad * 2, height + pad * 2

    defs, fill_attr = [], args.fill
    if args.gradient:
        c1, c2 = (args.gradient.split(",") + ["#000", "#fff"])[:2]
        defs.append(
            '<linearGradient id="tg" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
            "</linearGradient>" % (esc(c1.strip()), esc(c2.strip()))
        )
        fill_attr = "url(#tg)"
    if args.image:
        ext = os.path.splitext(args.image)[1].lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        b64 = base64.b64encode(io.open(args.image, "rb").read()).decode()
        defs.append(
            '<filter id="tlift"><feComponentTransfer>'
            '<feFuncR type="linear" slope="1.55"/><feFuncG type="linear" slope="1.55"/>'
            '<feFuncB type="linear" slope="1.55"/></feComponentTransfer></filter>'
            '<pattern id="tp" patternUnits="userSpaceOnUse" x="0" y="0" '
            'width="%d" height="%d">'
            '<image href="data:%s;base64,%s" x="0" y="0" width="%d" height="%d" '
            'filter="url(#tlift)" preserveAspectRatio="xMidYMid slice"/></pattern>'
            % (int(vb_w), int(vb_h), mime, b64, int(vb_w), int(vb_h))
        )
        fill_attr = "url(#tp)"

    stroke = ""
    if args.stroke:
        stroke = ' stroke="%s" stroke-width="%s" paint-order="stroke"' % (
            esc(args.stroke), args.stroke_width)

    body = []
    for d, x, y in paths:
        body.append(
            '<path d="%s" fill="%s" fill-rule="evenodd"%s/>' % (d, fill_attr, stroke)
        )
        if args.offset_shadow:
            body.append(
                '<path d="%s" fill="%s" opacity=".35" transform="translate(%s,%s)"/>'
                % (d, esc(args.offset_shadow), args.shadow_dx, args.shadow_dy)
            )

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
        'width="%d" height="%d" role="img" aria-label="%s">'
        "<defs>%s</defs>%s</svg>"
        % (vb_w, vb_h, vb_w, vb_h, esc(args.text.replace("|", "")), "".join(defs),
           "".join(body))
    )
    return svg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True, help="标题，| 表示换行")
    ap.add_argument("--font", required=True, help="字体文件路径，ttf/otf/ttc")
    ap.add_argument("--font-index", type=int, default=0, help="ttc 内的字体序号")
    ap.add_argument("--size", type=float, default=240)
    ap.add_argument("--tracking", type=float, default=0, help="字距，单位 em")
    ap.add_argument("--line-height", type=float, default=1.05, help="行高，单位 em")
    ap.add_argument("--padding", type=float, default=20)
    ap.add_argument("--fill", default="#0A0A0A")
    ap.add_argument("--gradient", help='两色渐变，如 "#E9D6AE,#8C6B35"')
    ap.add_argument("--image", help="用图片材质填充文字")
    ap.add_argument("--stroke", help="描边颜色")
    ap.add_argument("--stroke-width", default="3")
    ap.add_argument("--offset-shadow", help="偏移层颜色，用于叠印")
    ap.add_argument("--shadow-dx", default="8")
    ap.add_argument("--shadow-dy", default="8")
    ap.add_argument("--rotate", type=float, default=0, help="单个字的旋转角度")
    ap.add_argument("--rotate-index", type=int, default=0, help="旋转第几个字")
    ap.add_argument("--output", required=True)
    a = ap.parse_args()

    svg = build(a)
    io.open(a.output, "w", encoding="utf-8").write(svg)
    print("已生成", a.output, len(svg), "bytes")


if __name__ == "__main__":
    main()
