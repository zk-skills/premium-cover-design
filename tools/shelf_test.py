# -*- coding: utf-8 -*-
"""
shelf_test.py —— 货架轨封面的缩略图首读测试。

把封面缩到 240px 与 120px 宽，并排输出一张对照板，同时打印：
  平均明度（0–255）、平均饱和度（0–1）、暖色像素比例、明度标准差。

用法：
  python tools/shelf_test.py cover-a.png cover-b.png --out shelf.png
"""
import argparse, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageStat

CJK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"


def font(size):
    for p in (CJK, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def metrics(im):
    im = im.convert("RGB")
    hsv = im.convert("HSV")
    h, s, v = hsv.split()
    st = ImageStat.Stat(im)
    lum = sum(st.mean) / 3.0
    sat = ImageStat.Stat(s).mean[0] / 255.0
    hp = h.load()
    sp = s.load()
    warm = 0
    total = im.width * im.height
    for y in range(0, im.height, 3):
        for x in range(0, im.width, 3):
            hh = hp[x, y] * 360 // 255
            if sp[x, y] > 35 and (hh <= 55 or hh >= 335):
                warm += 1
    sampled = len(range(0, im.height, 3)) * len(range(0, im.width, 3))
    sd = sum(ImageStat.Stat(im).stddev) / 3.0
    return {"luminance": round(lum, 1), "saturation": round(sat, 2),
            "warm_ratio": round(warm / max(sampled, 1), 2), "contrast": round(sd, 1)}


def make_thumb(im, w):
    h = round(im.height * w / im.width)
    return im.convert("RGB").resize((w, h), Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+")
    ap.add_argument("--out", default="shelf.png")
    ap.add_argument("--widths", default="240,120")
    a = ap.parse_args()
    widths = [int(x) for x in a.widths.split(",") if x.strip()]
    rows = []
    for p in a.images:
        im = Image.open(p)
        rows.append((os.path.basename(p), im, metrics(im)))

    label_h = 34
    row_h = max(round(im.height * widths[0] / im.width) for _, im, _ in rows) + label_h
    left = 20
    col_w = sum(widths) + 24 * (len(widths) - 1)
    right = 300
    board = Image.new("RGB", (left * 2 + col_w + right, row_h * len(rows) + 20), (238, 235, 228))
    d = ImageDraw.Draw(board)
    f = font(15)
    fs = font(13)

    y = 10
    for name, im, m in rows:
        x = left
        for w in widths:
            th = make_thumb(im, w)
            board.paste(th, (x, y))
            d.text((x, y + th.height + 6), "%dpx" % w, font=fs, fill=(70, 70, 70))
            x += w + 24
        tx = left + col_w + 20
        d.text((tx, y + 2), name[:34], font=f, fill=(25, 25, 25))
        d.text((tx, y + 26), "明度 %s · 饱和 %s" % (m["luminance"], m["saturation"]), font=fs, fill=(60, 60, 60))
        d.text((tx, y + 46), "暖色 %s · 对比 %s" % (m["warm_ratio"], m["contrast"]), font=fs, fill=(60, 60, 60))
        y += row_h

    board.save(a.out)
    print("对照板：%s" % a.out)
    for name, _, m in rows:
        print("  %-32s 明度 %-6s 饱和 %-5s 暖色 %-5s 对比 %s" % (
            name[:32], m["luminance"], m["saturation"], m["warm_ratio"], m["contrast"]))
    print("人工检查：240px 下书名与品类是否能一眼读出；120px 下是否还剩下一个可辨认的形状。")


if __name__ == "__main__":
    main()
