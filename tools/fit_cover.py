# -*- coding: utf-8 -*-
"""
fit_cover.py —— 自动缩放封面标题以消除溢出，并回写到 HTML 文件。
需 Playwright（npm i -D playwright && npx playwright install chromium）。
不可用时退出码 2，提示改用 generate_cover.py --scale 手动下调。
"""
import argparse, io, json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

def fit(path):
    out = subprocess.run(["node", os.path.join(ROOT, "tools", "fit_cover.js"), path],
                         capture_output=True, encoding="utf-8", errors="replace")
    try: return json.loads(out.stdout)
    except Exception: return {"ok": False, "reason": "no-result"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--apply", action="store_true", help="把缩放结果写回文件")
    a = ap.parse_args()
    r = fit(a.html)
    if not r.get("ok"):
        print("无法自动适配（%s）。请用 generate_cover.py --scale 手动下调标题字号，或改用更宽松的布局。" % r.get("reason"))
        sys.exit(2)
    scale = r.get("scale", 1)
    if scale >= 0.999:
        print("标题无需缩放（1.00），版面正常。")
        return
    if a.apply:
        html = io.open(a.html, encoding="utf-8").read()
        m = re.search(r"--fs-title:([\d.]+)cqw", html)
        if m:
            new = round(float(m.group(1)) * scale, 2)
            newsub = round(max(1.6, new * 0.30), 2)
            html = html.replace("--fs-title:%scqw" % m.group(1), "--fs-title:%scqw" % new)
            html = re.sub(r"--fs-sub:[\d.]+cqw", "--fs-sub:%scqw" % newsub, html, count=1)
            io.open(a.html, "w", encoding="utf-8").write(html)
    print("标题缩放：%.3f（%s → %s）" % (scale, r.get("needed"), round(float(r.get("needed")) * scale, 2)))

if __name__ == "__main__":
    main()
