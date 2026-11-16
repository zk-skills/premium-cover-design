# -*- coding: utf-8 -*-
"""fix_tokens.py —— 保持色相与饱和度不变，只调整明度，使强调色/辅助色对底色的对比度达标。"""
import colorsys, io, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
P = os.path.join(ROOT, "dataset", "tokens.json")

def hex2rgb(h):
    h = h.lstrip("#")
    if len(h) == 3: h = h[0]*2+h[1]*2+h[2]*2
    return [int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)]
def rgb2hex(c):
    return "#%02X%02X%02X" % tuple(max(0,min(255,int(round(v)))) for v in c)
def lum(h):
    c=[]
    for v in hex2rgb(h):
        v/=255.0
        c.append(v/12.92 if v<=0.03928 else ((v+0.055)/1.055)**2.4)
    return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
def contrast(a,b):
    l1,l2=lum(a),lum(b); hi,lo=max(l1,l2),min(l1,l2)
    return (hi+0.05)/(lo+0.05)
def hls(h):
    r,g,b = [v/255.0 for v in hex2rgb(h)]
    return colorsys.rgb_to_hls(r,g,b)
def from_hls(h_,l_,s_):
    r,g,b = colorsys.hls_to_rgb(h_,l_,s_)
    return rgb2hex([r*255,g*255,b*255])

def fit(fg, bg, target):
    if contrast(fg,bg) >= target: return fg, False
    h_,l_,s_ = hls(fg)
    darker = lum(bg) > 0.35
    lo, hi = (0.0, l_) if darker else (l_, 1.0)
    best = fg
    for _ in range(40):
        mid = (lo+hi)/2.0
        cand = from_hls(h_, mid, s_)
        if darker:
            if contrast(cand,bg) >= target: best, lo = cand, mid
            else: hi = mid
        else:
            if contrast(cand,bg) >= target: best, lo = cand, mid
            else: hi = mid
    return best, True

data = json.load(io.open(P, encoding="utf-8"))
changed = []
for rid, t in data.items():
    for key, target in (("accent", 3.15), ("sub", 3.15)):
        old = t.get(key)
        if not old: continue
        new, ch = fit(old, t["bg"], target)
        if ch:
            t[key] = new
            changed.append("%s.%s %s -> %s (对比度 %.2f -> %.2f)" % (
                rid, key, old, new, contrast(old,t["bg"]), contrast(new,t["bg"])))
io.open(P, "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=2))
print("调整 %d 处：" % len(changed))
for c in changed: print("  " + c)
