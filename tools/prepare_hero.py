# -*- coding: utf-8 -*-
"""
prepare_hero.py —— 主视觉上版前的处理与体检。

生成图直接塞进封面通常有三个问题：比例不对、色调和版面两张皮、分辨率不够。
本工具按封面比例裁切、可选降饱和与叠色、重编码，并把有效 dpi 算清楚。

用法：
  python tools/prepare_hero.py hero-raw.png --size a4 --out hero.jpg \
      --focus "50% 35%" --desat 20 --tone "#0B1A2E" --tone-op 0.3

  # 只体检不改图
  python tools/prepare_hero.py hero.jpg --size a4 --check
"""
import argparse, io, json, os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(io.open(os.path.join(ROOT, "dataset", "design-recipes.json"), encoding="utf-8"))


def parse_focus(spec):
    s = str(spec or "50% 50%").strip()
    pct = "%" in s
    parts = s.replace("%", "").split()
    def num(p, default):
        try: v = float(p)
        except ValueError: return default
        if pct: v /= 100.0
        return min(1.0, max(0.0, v))
    return num(parts[0], 0.5), (num(parts[1], 0.5) if len(parts) > 1 else 0.5)


def hex2rgb(h):
    h = (h or "#000").lstrip("#")
    if len(h) == 3: h = h[0]*2 + h[1]*2 + h[2]*2
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def flatten(im, bg="#ffffff"):
    """透明图先合成到底色，避免 convert('RGB') 把透明区压成黑色。"""
    from PIL import Image
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        base = Image.new("RGB", im.size, hex2rgb(bg))
        base.paste(im, mask=im.getchannel("A"))
        return base
    return im.convert("RGB")


def process(path, sz, focus="50% 50%", desat=0, tone=None, tone_op=0.0, quality=88, bg="#ffffff"):
    from PIL import Image, ImageEnhance
    im = flatten(Image.open(path), bg)
    src = im.size
    tw, th = sz["w"], sz["h"]
    target = tw / float(th)
    fx, fy = parse_focus(focus)

    if src[0] / float(src[1]) > target:
        nw = int(round(src[1] * target))
        ox = max(0, min(src[0] - nw, int(round((src[0] - nw) * fx))))
        im = im.crop((ox, 0, ox + nw, src[1]))
    else:
        nh = int(round(src[0] / target))
        oy = max(0, min(src[1] - nh, int(round((src[1] - nh) * fy))))
        im = im.crop((0, oy, src[0], oy + nh))

    crop = im.size
    scale = max(tw / float(crop[0]), th / float(crop[1]))
    if scale > 1.0:
        im = im.resize((max(tw, int(round(crop[0]*scale))), max(th, int(round(crop[1]*scale)))),
                       Image.Resampling.LANCZOS)
    out = im.size

    if desat:
        im = ImageEnhance.Color(im).enhance(max(0.0, 1.0 - desat/100.0))
    if tone and tone_op:
        layer = Image.new("RGB", im.size, hex2rgb(tone))
        im = Image.blend(im, layer, min(1.0, max(0.0, tone_op)))

    mm = sz["mm"].split()
    mm_w = float(mm[0].replace("mm", "")); mm_h = float(mm[1].replace("mm", ""))
    dpi = int(round(min(out[0]/(mm_w/25.4), out[1]/(mm_h/25.4))))
    return im, {"src": src, "crop": crop, "out": out,
                "scale": round(out[0]/float(crop[0]), 2), "dpi": dpi,
                "need_px": int(round(mm_w/25.4*300))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--size", default="a4", help="画布预设，见 dataset/design-recipes.json meta.sizes")
    ap.add_argument("--out")
    ap.add_argument("--focus", default="50% 50%")
    ap.add_argument("--desat", type=float, default=0)
    ap.add_argument("--tone")
    ap.add_argument("--tone-op", type=float, default=0.0)
    ap.add_argument("--quality", type=int, default=88)
    ap.add_argument("--check", action="store_true", help="只体检，不写文件")
    ap.add_argument("--bg", default="#ffffff", help="透明 PNG 的合成底色，应与封面主色一致")
    a = ap.parse_args()

    sz = DATA["meta"]["sizes"].get(a.size)
    if not sz:
        raise SystemExit("未知画布 %s（可选 %s）" % (a.size, "、".join(DATA["meta"]["sizes"])))
    im, m = process(a.image, sz, a.focus, a.desat, a.tone, a.tone_op, a.quality, a.bg)

    print("主视觉体检：%s" % a.image)
    print("  源 %dx%d → 裁切 %dx%d → 输出 %dx%d（放大 %.2fx）" % (
        *m["src"], *m["crop"], *m["out"], m["scale"]))
    print("  有效 dpi %d（整幅出血）· 印刷 300dpi 需 %dpx 宽" % (m["dpi"], m["need_px"]))
    if m["dpi"] < 200:
        print("  结论：不足 200dpi，付印不接受；屏幕交付可接受，建议重新生成更大尺寸。")
    elif m["dpi"] < 300:
        print("  结论：200–300dpi，付印前需打样确认；屏幕交付足够。")
    else:
        print("  结论：达到 300dpi，可付印。")

    if not a.check:
        out = a.out or os.path.splitext(a.image)[0] + "-hero.jpg"
        im.save(out, "JPEG", quality=a.quality, optimize=True, progressive=True)
        print("  已写出：%s（%dKB）" % (out, os.path.getsize(out)//1024))


if __name__ == "__main__":
    main()
