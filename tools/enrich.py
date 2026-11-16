# -*- coding: utf-8 -*-
"""Hand-authored design tokens: turn each recipe's prose into executable visual parameters."""
import io, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

T = {
"R01": dict(bg="#F4F1EA", ink="#111111", accent="#D62828", sub="#6B6B6B", accent2="#111111",
            fonts=dict(display="sans", body="sans", meta="mono"), texture="paper", density=0.45,
            keywords=["报告","研究","科技","商业","知识","专业"]),
"R02": dict(bg="#F3F2EF", ink="#171717", accent="#B8412E", sub="#7C7A74", accent2="#3A3A38",
            fonts=dict(display="serif", body="sans", meta="sans"), texture="grain", density=0.6,
            keywords=["杂志","文化","人物","深度","商业","访谈"]),
"R03": dict(bg="#FCFCFB", ink="#141414", accent="#B8B2A4", sub="#8A8A85", accent2="#2A2A28",
            fonts=dict(display="sans", body="sans", meta="mono"), texture="paper", density=0.22,
            keywords=["极简","哲学","科学","设计","思想","克制"]),
"R04": dict(bg="#FFFFFF", ink="#0A0A0A", accent="#E8112D", sub="#5A5A5A", accent2="#FFD400",
            fonts=dict(display="heavy", body="sans", meta="mono"), texture="rough", density=0.85,
            keywords=["社会","议题","观点","创新","先锋","强烈"]),
"R05": dict(bg="#F1F4F8", ink="#0F1B2D", accent="#1B4E9B", sub="#6B7A90", accent2="#C25E00",
            fonts=dict(display="sans", body="sans", meta="mono"), texture="none", density=0.72,
            keywords=["年报","白皮书","数据","行业","学术","信息"]),
"R06": dict(bg="#F6F3EC", ink="#2B2A26", accent="#6F8177", sub="#8A8578", accent2="#3E4A45",
            fonts=dict(display="serif", body="serif", meta="sans"), texture="paper", density=0.3,
            keywords=["文学","散文","随笔","哲学","人生","诗"]),
"R07": dict(bg="#EDE7DE", ink="#3A352F", accent="#8C7B6B", sub="#7A7266", accent2="#5A5148",
            fonts=dict(display="serif", body="serif", meta="sans"), texture="rough", density=0.25,
            keywords=["自然","时间","禅","朴素","人生","生活"]),
"R08": dict(bg="#D7DEE4", ink="#171A1F", accent="#6C5C86", sub="#5B6670", accent2="#2E3742",
            fonts=dict(display="serif", body="sans", meta="sans"), texture="grain", density=0.42,
            keywords=["超现实","意识","认知","心理","想象","哲学"]),
"R09": dict(bg="#E9E0D1", ink="#2B241C", accent="#A8792C", sub="#55604E", accent2="#7C3F2E",
            fonts=dict(display="serif", body="serif", meta="sans"), texture="grain", density=0.55,
            keywords=["历史","传记","爱情","人文","文学","温暖"]),
"R10": dict(bg="#F4F4F2", ink="#111111", accent="#111111", sub="#8A8A85", accent2="#5E5E5A",
            fonts=dict(display="serif", body="sans", meta="mono"), texture="none", density=0.35,
            keywords=["哲学","象征","思想","心理","科学","文化"]),
"R11": dict(bg="#FBFAF7", ink="#3A3A38", accent="#9FB3BF", sub="#9A9A96", accent2="#C9A6A6",
            fonts=dict(display="serif", body="serif", meta="sans"), texture="paper", density=0.2,
            keywords=["诗歌","情绪","生活","感悟","温柔","散文"]),
"R12": dict(bg="#0E2A47", ink="#F7F4EE", accent="#C6A46B", sub="#9FB0C4", accent2="#1D3E63",
            fonts=dict(display="serif", body="sans", meta="sans"), texture="paper", density=0.5,
            keywords=["年报","机构","战略","白皮书","权威","可持续"]),
"R13": dict(bg="#0B1E38", ink="#F2F5F8", accent="#E08A2E", sub="#6E8AA8", accent2="#2F5C8A",
            fonts=dict(display="sans", body="sans", meta="mono"), texture="none", density=0.7,
            keywords=["金融","经济","市场","投研","行业","咨询"]),
"R14": dict(bg="#0A0E18", ink="#EEF3F8", accent="#4FC3F7", sub="#8FA3B8", accent2="#1B2C44",
            fonts=dict(display="sans", body="sans", meta="mono"), texture="grain", density=0.62,
            keywords=["科技","AI","软件","工程","数字","白皮书"]),
"R15": dict(bg="#0C1220", ink="#E8EEF6", accent="#7CFF6B", sub="#5C7290", accent2="#1E3A5F",
            fonts=dict(display="sans", body="sans", meta="mono"), texture="none", density=0.78,
            keywords=["数据","报告","AI指数","研究","可视化","产业"]),
"R16": dict(bg="#E9E7E3", ink="#191919", accent="#A8A49E", sub="#6E6B66", accent2="#3D3B38",
            fonts=dict(display="sans", body="sans", meta="mono"), texture="none", density=0.4,
            keywords=["建筑","城市","空间","工业","设计","规划"]),
"R17": dict(bg="#F0EADD", ink="#141414", accent="#D32011", sub="#4A4A4A", accent2="#111111",
            fonts=dict(display="heavy", body="sans", meta="mono"), texture="print", density=0.9,
            keywords=["工程","革命","教育","设计","社会","力量"]),
"R18": dict(bg="#101012", ink="#F2F2F2", accent="#39FF14", sub="#8C8C92", accent2="#FF2D55",
            fonts=dict(display="heavy", body="sans", meta="mono"), texture="print", density=0.88,
            keywords=["先锋","文化","艺术","身份","数字","实验"]),
"R19": dict(bg="#F4EFE2", ink="#1A1A1A", accent="#2B4C9B", sub="#5E5648", accent2="#E8452C",
            fonts=dict(display="display", body="sans", meta="mono"), texture="print", density=0.75,
            keywords=["独立出版","艺术","文化","复古","设计","杂志"]),
"R20": dict(bg="#05060A", ink="#EDEDF2", accent="#A970FF", sub="#7C7C8C", accent2="#22E3FF",
            fonts=dict(display="sans", body="mono", meta="mono"), texture="print", density=0.85,
            keywords=["数字艺术","未来","AI","互联网","故障","实验"]),
"R21": dict(bg="#0F151B", ink="#F3EFE6", accent="#C9A227", sub="#6E7B85", accent2="#3C4A56",
            fonts=dict(display="serif", body="sans", meta="sans"), texture="grain", density=0.5,
            keywords=["小说","历史","传记","旅行","社会","叙事"]),
"R22": dict(bg="#F3F1EC", ink="#24211C", accent="#7C6A55", sub="#8C8880", accent2="#4A4438",
            fonts=dict(display="serif", body="sans", meta="sans"), texture="paper", density=0.38,
            keywords=["艺术","静物","生活","产品","美学","微距"]),
"R23": dict(bg="#E7DBBE", ink="#241C12", accent="#8C2F1F", sub="#6E5C42", accent2="#3C2F1E",
            fonts=dict(display="serif", body="serif", meta="mono"), texture="rough", density=0.68,
            keywords=["历史","档案","传记","文献","社会","工业史"]),
"R24": dict(bg="#F1EDE3", ink="#22301F", accent="#7A2E22", sub="#5C6B57", accent2="#3C4A33",
            fonts=dict(display="serif", body="serif", meta="mono"), texture="paper", density=0.62,
            keywords=["科普","医学","生物","科学","教育","解剖"]),
"R25": dict(bg="#F4F2E9", ink="#24301F", accent="#6B7A3F", sub="#7E8A73", accent2="#3F4A2C",
            fonts=dict(display="serif", body="serif", meta="sans"), texture="paper", density=0.45,
            keywords=["健康","生命","自然","营养","生活方式","疗愈"]),
"R26": dict(bg="#EFEDE7", ink="#141821", accent="#1F2A44", sub="#8A8F98", accent2="#B08D57",
            fonts=dict(display="sans", body="sans", meta="mono"), texture="none", density=0.5,
            keywords=["科技","艺术","商业","创新","未来","空间"]),
}

# 中文竖排 / 装饰性标记的可用性开关
SPECIAL = {
    "R06": dict(vertical=True),
    "R18": dict(vertical=False),
}

out = {}
for rid, v in T.items():
    d = dict(v)
    d.update(SPECIAL.get(rid, {}))
    out[rid] = d

dst = os.path.join(ROOT, "dataset", "tokens.json")
with io.open(dst, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("enriched:", len(out))
