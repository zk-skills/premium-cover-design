# HTML 实现示例

为压缩 Skill 体积，44 张配方示例与 18 张组合示例的 HTML 与截图已移除。
`prototypes/` 保留 3 张构图原型示范，用来核对 C 原型与 T 组合的差异。

## 重新生成

```bash
# 26 张配方示例
python tools/generate_examples.py

# 18 张组合示例
python tools/generate_hybrid_examples.py

# 批量校验
python tools/verify_examples.py
```

生成的是单文件 HTML，样式内联、在线字体实时加载，可直接打开或打印为 PDF。
