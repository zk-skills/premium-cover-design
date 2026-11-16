# -*- coding: utf-8 -*-
"""
check_fonts.py —— 字体资产体检。

本地模式（默认）：
  1. 下载被截断、字体表损坏（fontTools 解析失败）；
  2. 只有拉丁字形，没有简体中文字形；
  3. 注册表里写了、但文件不存在。

在线模式（--online）：
  1. dataset/fonts-online.json 里每个字体能否从 Google Fonts 取到；
  2. 简体常用字的真实覆盖，标出缺字；
  3. 对比注册表里写的 coverage 等级是否与实测一致。

用法：
  python tools/check_fonts.py
  python tools/check_fonts.py --online
  python tools/check_fonts.py --online --sample "三品合一破局内卷"
  python tools/check_fonts.py fonts/SmileySans-Oblique.ttf
"""
import argparse
import concurrent.futures
import glob
import io
import json
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, "dataset", "fonts.json")
ONLINE_REGISTRY = os.path.join(ROOT, "dataset", "fonts-online.json")

SAMPLE = (
    "三品合一破局内卷的品类增长战法贾伟著洛可可学园组编"
    "机械工业出版社中国商业设计品牌创新用户价值场景差异化"
    "方法论实战案例冠军赛道"
    "0123456789ABCabc，。！？、；：（）《》—“”"
)
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def check(path):
    try:
        font = TTFont(path, lazy=False)
    except Exception as e:
        return {"path": path, "ok": False, "error": str(e)[:120]}
    try:
        cmap = font.getBestCmap() or {}
        family = font["name"].getDebugName(1) or "?"
        missing = [c for c in SAMPLE if c not in " \n" and ord(c) not in cmap]
        return {
            "path": path, "ok": True, "family": family,
            "glyphs": len(cmap), "missing": missing,
            "size": os.path.getsize(path),
        }
    finally:
        font.close()


def local_main(args):
    paths = args or sorted(glob.glob(os.path.join(ROOT, "fonts", "*.ttf")) +
                           glob.glob(os.path.join(ROOT, "fonts", "*.otf")))
    if not paths:
        print("本地字体未内置（已为压缩体积移除）。检查在线字体请用：")
        print("  python tools/check_fonts.py --online")
        return 0
    bad = 0
    print("本地字体资产体检：")
    for p in paths:
        r = check(p)
        name = os.path.basename(p)
        if not r["ok"]:
            bad += 1
            print("  [损坏] %-42s %s" % (name, r["error"]))
            continue
        miss = r["missing"]
        flag = "通过" if not miss else "缺字"
        if miss:
            bad += 1
        print("  [%s] %-42s %-28s %5d 字形  %6.1f MB%s" % (
            flag, name, r["family"], r["glyphs"], r["size"] / 1024 / 1024,
            "" if not miss else "  缺：" + "".join(miss[:16])))

    if os.path.exists(REGISTRY):
        reg = json.load(io.open(REGISTRY, encoding="utf-8"))
        for f in reg.get("fonts", []):
            fp = os.path.join(ROOT, f["file"])
            if not os.path.exists(fp):
                bad += 1
                print("  [缺失] 注册表 %s → %s" % (f["id"], f["file"]))
    print("结论：%s" % ("全部通过" if not bad else "%d 项问题" % bad))
    return 1 if bad else 0


# ---------------- 在线模式 ----------------

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()


def probe_css(font):
    """返回 (ok, css, 错误信息)。只请求字体真实支持的字重。"""
    ws = font.get("weights") or [400]
    url = ("https://fonts.googleapis.com/css2?family=%s:wght@%s&display=swap"
           % (font["family"].replace(" ", "+"), ";".join(str(w) for w in ws)))
    try:
        status, body = fetch(url)
        css = body.decode("utf-8", "replace")
        return (status == 200 and "@font-face" in css), css, ""
    except Exception as e:
        return False, "", str(e)[:80]


def parse_faces(css):
    faces = []
    for blk in re.findall(r"@font-face\s*\{(.*?)\}", css, re.S):
        ur = re.search(r"unicode-range:\s*([^;]+);", blk)
        src = re.search(r"url\((https://[^)]+)\)", blk)
        if ur and src:
            faces.append((ur.group(1).strip(), src.group(1)))
    return faces


def in_range(cp, rng):
    for part in rng.split(","):
        part = part.strip().replace("U+", "")
        try:
            if "-" in part:
                a, b = part.split("-")
                if int(a, 16) <= cp <= int(b, 16):
                    return True
            elif int(part, 16) == cp:
                return True
        except ValueError:
            pass
    return False


def coverage_of(css, sample):
    """按 unicode-range 找到字所在分片，下载后查 cmap。返回缺字列表。"""
    faces = parse_faces(css)
    need = {}
    for ch in sample:
        cp = ord(ch)
        for rng, url in faces:
            if in_range(cp, rng):
                need[ch] = url
                break
    cache = {}
    missing = []
    for ch, url in need.items():
        if url not in cache:
            try:
                cache[url] = fetch(url)[1]
            except Exception:
                cache[url] = None
        data = cache[url]
        if not data:
            missing.append(ch)
            continue
        try:
            fd, tmp = tempfile.mkstemp(suffix=".woff2")
            os.close(fd)
            open(tmp, "wb").write(data)
            f = TTFont(tmp, lazy=True)
            cmap = f.getBestCmap() or {}
            if ord(ch) not in cmap:
                missing.append(ch)
            f.close()
            os.unlink(tmp)
        except Exception:
            missing.append(ch)
    # 分片里没找到的字符也算缺失
    missing += [c for c in sample if c not in need]
    return sorted(set(missing))


def online_main(sample):
    reg = json.load(io.open(ONLINE_REGISTRY, encoding="utf-8"))
    fonts = reg["fonts"]
    sample = "".join(dict.fromkeys(c for c in sample if c.strip()))
    print("在线字体体检：%d 个字体，覆盖样本 %d 字（%s）" %
          (len(fonts), len(sample), reg["policy"]["defaultMode"]))

    def one(f):
        ok, css, err = probe_css(f)
        if not ok:
            return {"id": f["id"], "name": f["name"], "family": f["family"],
                    "ok": False, "error": err or "CSS 无 @font-face"}
        miss = coverage_of(css, sample) if sample else []
        return {"id": f["id"], "name": f["name"], "family": f["family"],
                "ok": True, "missing": miss, "declared": f["coverage"]}

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        rows = list(ex.map(one, fonts))

    bad = 0
    for r in sorted(rows, key=lambda x: (not x["ok"], x["declared"] if "declared" in x else "")):
        if not r["ok"]:
            bad += 1
            print("  [不可用] %-16s %-24s %s" % (r["id"], r["family"], r["error"]))
            continue
        miss = r["missing"]
        pct = 100.0 * (len(sample) - len(miss)) / len(sample) if sample else 100.0
        flag = "可用"
        if miss and r["declared"] == "sc":
            flag = "实测缺字"
            bad += 1
        elif miss:
            flag = "部分缺字"
        print("  [%s] %-16s %-24s %s %5.1f%%%s" % (
            flag, r["id"], r["family"], r["declared"], pct,
            "" if not miss else "  缺：" + "".join(miss[:20])))

    usable = len([r for r in rows if r["ok"]])
    print("-" * 76)
    print("结论：%d/%d 可用；登记为 sc 但实测缺字 %d 个" %
          (usable, len(rows), len([r for r in rows
                                   if r.get("missing") and r.get("declared") == "sc"])))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description="字体资产体检")
    ap.add_argument("paths", nargs="*", help="本地字体文件路径")
    ap.add_argument("--online", action="store_true", help="检查在线字体库")
    ap.add_argument("--sample", default=SAMPLE, help="缺字检测样本文字")
    a = ap.parse_args()
    if a.online:
        return online_main(a.sample)
    return local_main(a.paths)


if __name__ == "__main__":
    sys.exit(main())
