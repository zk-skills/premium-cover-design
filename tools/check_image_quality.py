# -*- coding: utf-8 -*-
"""
check_image_quality.py —— 按成品尺寸计算图片的有效 dpi 与放大倍数。

dpi = 源像素宽 / (成品显示宽 mm / 25.4)
放大倍数 = 画布显示像素 / 源像素（>1 表示被放大）

用法：
  python tools/check_image_quality.py hero.png --mm 141
  python tools/check_image_quality.py logo.png --mm 49.9 --logo
  python tools/check_image_quality.py a.png b.png --mm 141,49.9 --display-px 1060,374
"""
import argparse, os, sys
from PIL import Image
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def parse_list(s, n):
    if not s:
        return [None] * n
    parts = [x.strip() for x in s.split(",")]
    if len(parts) == 1:
        return parts * n
    if len(parts) != n:
        raise SystemExit("列表长度与图片数量不一致：%s" % s)
    return parts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+")
    ap.add_argument("--mm", help="成品显示宽度（毫米），逗号分隔")
    ap.add_argument("--display-px", help="画布上的显示宽度（CSS px），逗号分隔")
    ap.add_argument("--canvas-px", type=float, help="画布总宽（CSS px），用于折算 mm")
    ap.add_argument("--logo", action="store_true", help="按标识标准（≥600dpi，优先矢量）")
    ap.add_argument("--strict", action="store_true", help="有失败项时返回非零")
    a = ap.parse_args()

    n = len(a.images)
    mms = parse_list(a.mm, n)
    dps = parse_list(a.display_px, n)
    rows, failed = [], False

    for i, p in enumerate(a.images):
        im = Image.open(p)
        w, h = im.size
        mm = float(mms[i]) if mms[i] else None
        if mm is None and a.canvas_px and dps[i]:
            mm = 180.0 * float(dps[i]) / a.canvas_px
        dpi = w / (mm / 25.4) if mm else None
        up = (float(dps[i]) / w) if dps[i] else None

        if a.logo:
            if dpi is None:
                verdict, note = "warn", "缺少成品尺寸，无法算 dpi"
            elif dpi >= 600:
                verdict, note = "pass", "标识清晰度达标；位图仍建议换矢量"
            else:
                verdict, note = "warn", "标识建议 ≥600dpi 或直接换矢量"
            if im.mode in ("RGBA", "LA") or "transparency" in im.info:
                note += "；含透明通道"
        else:
            if dpi is None:
                verdict, note = "warn", "缺少成品尺寸，无法算 dpi"
            elif dpi >= 300:
                verdict, note = "pass", "印刷清晰度达标"
            elif dpi >= 200:
                verdict, note = "warn", "接近下限，建议重出或缩小显示尺寸"
            else:
                verdict, note = "fail", "有效 dpi 过低，印刷会糊"

        if up is not None:
            if up > 2:
                verdict, note = "fail", note + "；放大 %.2f× 超过 2×" % up
            elif up > 1.5:
                if verdict == "pass":
                    verdict = "warn"
                note += "；放大 %.2f×，边缘会软" % up
            elif up > 1.0:
                note += "；放大 %.2f×" % up

        if verdict == "fail":
            failed = True
        rows.append((os.path.basename(p), "%dx%d" % (w, h),
                     "%.0f" % dpi if dpi else "—",
                     "%.2f×" % up if up else "—", verdict, note))

    print("%-28s %-12s %7s %7s  %-5s %s" % ("文件", "源像素", "有效dpi", "放大", "结论", "说明"))
    print("-" * 100)
    for r in rows:
        print("%-28s %-12s %7s %7s  %-5s %s" % r)
    print("-" * 100)
    print("阈值：主视觉印刷 ≥300dpi；标识 ≥600dpi 或矢量；放大 >2× 不接受。")
    if failed:
        print("结论：存在失败项，付印前必须处理。")
    if a.strict and failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
