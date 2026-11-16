# -*- coding: utf-8 -*-
"""生成字体表现手法样张（单文件 HTML，SVG 内嵌，离线）。"""
import io, os

ROOT = "/workspace"
FILES = {
    "metal": "/workspace/ts-metal.svg",
    "photo": "/workspace/ts-photo.svg",
    "outline": "/workspace/ts-outline.svg",
    "offset": "/workspace/ts-offset.svg",
    "rotate": "/workspace/ts-rotate.svg",
}
svgs = {k: io.open(v, encoding="utf-8").read() for k, v in FILES.items() if os.path.exists(v)}


def cell(tag, name, body, dark=False):
    return f'''<div class="cell{' dark' if dark else ''}">
      <div class="meta"><span class="tag">{tag}</span><span>{name}</span></div>
      <div class="stage">{body}</div>
    </div>'''


html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>文字介质样张</title>
<style>
*{{box-sizing:border-box}}
html,body{{margin:0;background:#141414;font-family:'Source Han Sans SC','Noto Sans CJK SC',sans-serif}}
.page{{width:1350px;height:1800px;margin:0 auto;background:#0A0A0A;color:#F2EDE3;padding:96px 90px 80px;position:relative;overflow:hidden}}
.head{{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid rgba(242,237,227,.22);padding-bottom:22px}}
.head h1{{margin:0;font-size:44px;font-weight:300;letter-spacing:.12em}}
.head span{{font-size:16px;letter-spacing:.2em;color:#C7A66A}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:26px 30px;margin-top:34px}}
.cell{{height:348px;position:relative;border:1px solid rgba(242,237,227,.14);padding:26px 26px 18px;display:flex;flex-direction:column}}
.cell.dark{{background:#050505}}
.meta{{display:flex;gap:14px;align-items:baseline;font-size:15px;letter-spacing:.08em;color:#9C9588;flex:none}}
.tag{{color:#C7A66A;font-family:'JetBrains Mono',Consolas,monospace;font-size:13px;letter-spacing:.08em}}
.stage{{flex:1;display:flex;align-items:center;justify-content:center;overflow:hidden;position:relative}}
.stage svg{{width:100%;height:auto;display:block}}
.t-html{{font-size:150px;line-height:1;letter-spacing:.02em;white-space:nowrap}}
.w300{{font-weight:300}}.w900{{font-weight:900}}
.t-vert{{writing-mode:vertical-rl;font-size:82px;line-height:1.05;letter-spacing:.1em;height:270px}}
.t-crop{{font-size:250px;line-height:1;white-space:nowrap;font-weight:900;letter-spacing:-.06em;position:absolute;left:-52px;top:18px}}
.foot{{position:absolute;left:90px;right:90px;bottom:54px;display:flex;justify-content:space-between;font-size:14px;letter-spacing:.14em;color:#7E786C;border-top:1px solid rgba(242,237,227,.16);padding-top:16px}}
</style></head><body><div class="page">
  <div class="head"><h1>文字不是文本</h1><span>TEXT AS MATERIAL · 8 种介质</span></div>
  <div class="grid">
    {cell("M1 / HTML", "细体排印", '<div class="t-html w300">三品合一</div>')}
    {cell("M1 / HTML", "超粗排印", '<div class="t-html w900">三品合一</div>', True)}
    {cell("M2 / SVG", "金属渐变转曲", svgs.get("metal", ""))}
    {cell("M2 / SVG", "材质图片填充", svgs.get("photo", ""), True)}
    {cell("M2 / SVG", "描边镂空", svgs.get("outline", ""))}
    {cell("M2 / SVG", "叠印偏移", svgs.get("offset", ""), True)}
    {cell("M2 / SVG", "单字旋转", svgs.get("rotate", ""))}
    {cell("M1 / HTML", "裁切出血", '<div class="t-crop">三品合一</div>', True)}
  </div>
  <div class="foot"><span>premium-cover-design</span><span>同一句标题 · 八种呈现</span></div>
</div></body></html>'''

out = "/workspace/typography-specimen.html"
io.open(out, "w", encoding="utf-8").write(html)
print("已生成", out)
