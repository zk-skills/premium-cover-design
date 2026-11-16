# 在线字体库（79 个）

> 封面默认从在线字体库选字，不下载字体文件、不内嵌本地 TTF。
> 所有字体均通过 Google Fonts CSS2 接口按实际用到的字重加载，浏览器打开时联网取字。
> 结构化数据见 `dataset/fonts-online.json`，字体验证命令见文末。

## 为什么这样分级

中文字体的「覆盖」不能靠名字猜。库里的分级来自对同一段 86 字样本的逐字实测：
先把 CSS 的 unicode-range 映射到分片，下载分片后查 cmap，缺一个字就记一笔。
结果是：思源系列、站酷四款、书法四款、霞鹜文楷 100% 命中；
日文字体普遍缺「业、伟、军、创、场、战、户、组、编、计、论、设、贾、赛、长」这类简体专用字，
实测覆盖 70%–82%，所以不能标成「简体全覆盖」。

| 级别 | 数量 | 判定 | 使用规则 |
| --- | --- | --- | --- |
| sc 简体全覆盖 | 11 | 实测 86 个常用简体字 100% 命中，可直接用于任意简体标题。 | 任意简体标题 |
| han 东亚汉字 | 42 | 日文字体，含常用汉字但缺部分简体特有字。短标题可用，交付前必须检测。 | 短标题；先跑缺字检测 |
| tc 繁体 | 4 | 港台字形，简体字缺失较多，只用于繁体文本或港台版。 | 仅繁体文本 |
| latin 拉丁展示体 | 22 | 只覆盖西文；中文自动回退到 fallbackCn 指定的中文字体。 | 中西混排，中文走回退 |

## A 级 · 简体全覆盖（11）

| ID | 字体 | CSS family | 字重 | 气质 | 适用 |
| --- | --- | --- | --- | --- | --- |
| `noto-sans-sc` | 思源黑体 | Noto Sans SC | 100–900 | 现代 理性 中性 高可读 | 报告、商业、科技、机构 |
| `noto-serif-sc` | 思源宋体 | Noto Serif SC | 100–900 | 书卷 庄重 可归档 高可读 | 文学、学术、年鉴、白皮书 |
| `zcool-xiaowei` | 站酷小薇 | ZCOOL XiaoWei | 400 | 高对比 文艺 克制 东方现代 | 高对比美术宋，横细竖粗，机构与文化类标题 |
| `zcool-qingke` | 站酷庆科黄油 | ZCOOL QingKe HuangYou | 400 | 粗圆 亲切 有分量 商业 | 粗圆黑，笔画厚实，大众商业与活动标题 |
| `zcool-kuaile` | 站酷快乐 | ZCOOL KuaiLe | 400 | 轻松 童趣 手绘 亲和 | 轻松手写感，儿童、生活方式、轻科普 |
| `mashan` | 马善政楷书 | Ma Shan Zheng | 400 | 毛笔 楷书 东方 手写 | 毛笔楷书，东方、文化、宣言、题字 |
| `longcang` | 龙藏体 | Long Cang | 400 | 书法 硬朗 江湖 传统 | 硬朗毛笔行楷，笔画有刀刻感 |
| `zhimangxing` | 志莽行书 | Zhi Mang Xing | 400 | 行书 流动 文人 抒情 | 流动行书，适合诗意、文化、纪念 |
| `liujianmaocao` | 柳建毛草 | Liu Jian Mao Cao | 400 | 狂草 气势 传统 艺术 | 狂草毛笔，极强气势，适合宣言与限定版 |
| `lxgw-wenkai` | 霞鹜文楷 | LXGW WenKai TC | 300–700 | 楷体 温润 人文 耐读 | 开源楷体，温润耐读，适合文学与长副标题 |
| `lxgw-wenkai-mono` | 霞鹜文楷等宽 | LXGW WenKai Mono TC | 300–700 | 等宽 楷体 技术 人文 | 等宽楷体，代码感与书卷气并存 |

## B 级 · 东亚汉字（42）

| ID | 字体 | CSS family | 字重 | 气质 | 适用 |
| --- | --- | --- | --- | --- | --- |
| `shippori-mincho` | Shippori 明朝 | Shippori Mincho | 400–800 | 明朝 优雅 日本设计 高端 | 高品味明朝体，横竖对比柔和，适合文学与机构 |
| `shippori-antique` | Shippori Antique | Shippori Antique | 400 | 古董 安静 档案 中性 | 低对比古董黑体，安静、档案感 |
| `dela-gothic` | Dela Gothic | Dela Gothic One | 400 | 超粗 海报 高声量 冲击 | 超粗黑，单字重，海报与货架强首读 |
| `hina-mincho` | 雏明朝 | Hina Mincho | 400 | 纤细 明朝 安静 诗意 | 细笔明朝，纤细安静，文学与诗 |
| `kaisei-decol` | Kaisei Decol | Kaisei Decol | 400–700 | 装饰 明朝 柔和 生活 | 装饰明朝，圆润笔触，生活方式 |
| `kaisei-tokumin` | Kaisei Tokumin | Kaisei Tokumin | 400–800 | 端正 明朝 厚重 纪实 | 端正明朝，笔画厚重，适合传记与历史 |
| `kaisei-harunoumi` | Kaisei HarunoUmi | Kaisei HarunoUmi | 400–700 | 温和 明朝 呼吸 文艺 | 春之海明朝，温和有呼吸感 |
| `zen-old-mincho` | Zen 古明朝 | Zen Old Mincho | 400–900 | 经典 明朝 传统 出版 | 经典明朝，适合传统文化与出版 |
| `zen-kaku-gothic` | Zen 角黑 | Zen Kaku Gothic New | 300–900 | 角黑 现代 锐利 中性 | 现代角黑，锐利中性，科技与机构 |
| `zen-antique` | Zen 古董 | Zen Antique | 400 | 古董 书写 文化 品牌 | 古董黑体带书写味，适合文化品牌 |
| `zen-antique-soft` | Zen 古董柔 | Zen Antique Soft | 400 | 柔和 古董 亲和 生活 | 柔化古董黑体，亲和但不幼稚 |
| `zen-kurenaido` | Zen 红内道 | Zen Kurenaido | 400 | 手写 黑体 随性 生活 | 手写味黑体，随笔与生活提案 |
| `zen-maru-gothic` | Zen 丸黑 | Zen Maru Gothic | 300–900 | 圆体 友好 大众 青春 | 圆体黑，圆润友好，适合大众与青少年 |
| `sawarabi-mincho` | Sawarabi 明朝 | Sawarabi Mincho | 400 | 清秀 明朝 自然 散文 | 清秀明朝，适合散文与自然主题 |
| `sawarabi-gothic` | Sawarabi 黑 | Sawarabi Gothic | 400 | 清瘦 黑体 留白 极简 | 清瘦黑体，留白感强，适合极简 |
| `yuji-boku` | Yuji 朴 | Yuji Boku | 400 | 毛笔 松弛 文化 随笔 | 毛笔楷书，松弛自然，适合文化随笔 |
| `yuji-mai` | Yuji 舞 | Yuji Mai | 400 | 毛笔 轻盈 流动 诗意 | 毛笔行书，轻盈流动 |
| `yuji-syuku` | Yuji 俶 | Yuji Syuku | 400 | 毛笔 工整 端正 传统 | 工整毛笔楷，端正克制 |
| `klee-one` | Klee One | Klee One | 400–600 | 教科书 手写 温和 教育 | 教科书体，铅笔书写感，适合教育与人情味 |
| `dotgothic16` | DotGothic16 | DotGothic16 | 400 | 像素 点阵 科技 怀旧 | 点阵像素体，数字、游戏、科技怀旧 |
| `rocknroll-one` | RocknRoll One | RocknRoll One | 400 | 摇滚 青年 活动 有力 | 摇滚味圆黑，青年文化与活动 |
| `hachi-maru-pop` | Hachi Maru Pop | Hachi Maru Pop | 400 | 手账 可爱 生活 轻快 | 手账圆体，可爱、生活方式 |
| `kosugi` | Kosugi | Kosugi | 400 | 清瘦 中性 安静 极简 | 清瘦无衬，安静中性，适合正文标题 |
| `kosugi-maru` | Kosugi Maru | Kosugi Maru | 400 | 圆体 清瘦 柔和 技术 | 清瘦圆体，柔和技术感 |
| `mplus-1p` | M PLUS 1p | M PLUS 1p | 100–900 | 几何 现代 中性 排版 | 几何无衬，现代主义排版 |
| `mplus-rounded-1c` | M PLUS Rounded 1c | M PLUS Rounded 1c | 100–900 | 几何 圆体 温和 科技 | 几何圆体，温和科技 |
| `mplus-1` | M PLUS 1 | M PLUS 1 | 100–900 | 几何 可变 现代 中性 | 可变几何无衬，粗细跨度大 |
| `mplus-2` | M PLUS 2 | M PLUS 2 | 100–900 | 几何 可变 宽字面 现代 | 可变几何无衬，字面略宽 |
| `biz-udpgothic` | BIZ UDP 黑 | BIZ UDPGothic | 400–700 | 通用设计 清晰 中性 机构 | 通用设计黑体，清晰度优先 |
| `biz-udpmincho` | BIZ UDP 明朝 | BIZ UDPMincho | 400–700 | 通用设计 明朝 可读 机构 | 通用设计明朝，长文可读性优先 |
| `biz-udgothic` | BIZ UD 黑 | BIZ UDGothic | 400–700 | 通用设计 清晰 中性 教育 | 通用设计黑体，笔画区分明确 |
| `biz-udmincho` | BIZ UD 明朝 | BIZ UDMincho | 400–700 | 通用设计 明朝 端正 教育 | 通用设计明朝，端正易读 |
| `new-tegomin` | New Tegomin | New Tegomin | 400 | 手写 明朝 纸感 文艺 | 手写明朝，带有纸笔温度 |
| `yomogi` | Yomogi | Yomogi | 400 | 手写 细笔 轻盈 生活 | 细笔手写体，轻盈少女感 |
| `murecho` | Murecho | Murecho | 100–900 | 可变 收紧 现代 标题 | 可变无衬，字形收紧，适合现代标题 |
| `kiwi-maru` | Kiwi Maru | Kiwi Maru | 300–500 | 圆润 手写 亲和 食物 | 圆润手写体，亲和、食物与生活 |
| `stick` | Stick | Stick | 400 | 手写 硬朗 青年 运动 | 硬朗手写黑，青年与运动 |
| `rampart-one` | Rampart One | Rampart One | 400 | 立体 描边 活动 潮流 | 立体描边装饰体，活动与潮流 |
| `reggae-one` | Reggae One | Reggae One | 400 | 复古 招牌 厚重 个性 | 复古招牌体，厚重有个性 |
| `potta-one` | Potta One | Potta One | 400 | 招牌 粗笔 包装 有力 | 粗笔招牌体，适合标题与包装 |
| `train-one` | Train One | Train One | 400 | 描边 装饰 活动 短标题 | 描边装饰体，适合短标题与活动 |
| `yusei-magic` | Yusei Magic | Yusei Magic | 400 | 马克笔 手写 活力 生活 | 马克笔手写体，轻松有活力 |

## C 级 · 繁体（4）

| ID | 字体 | CSS family | 字重 | 气质 | 适用 |
| --- | --- | --- | --- | --- | --- |
| `noto-sans-tc` | 思源黑体（繁） | Noto Sans TC | 100–900 | 繁体 现代 中性 高可读 | 繁体无衬线，适合港台版封面 |
| `noto-serif-tc` | 思源宋体（繁） | Noto Serif TC | 100–900 | 繁体 书卷 庄重 可归档 | 繁体衬线，适合港台文学与学术 |
| `noto-sans-hk` | 思源黑体（港） | Noto Sans HK | 100–900 | 繁体 香港字形 现代 中性 | 香港字形无衬线 |
| `noto-serif-hk` | 思源宋体（港） | Noto Serif HK | 100–900 | 繁体 香港字形 书卷 庄重 | 香港字形衬线 |

## D 级 · 拉丁展示体（22）

| ID | 字体 | CSS family | 字重 | 气质 | 适用 |
| --- | --- | --- | --- | --- | --- |
| `playfair-display` | Playfair Display | Playfair Display | 400–900 | 高对比 迪多 时尚 编辑 | 高对比迪多系，时尚、人物、文化 |
| `bodoni-moda` | Bodoni Moda | Bodoni Moda | 400–900 | 迪多 锋利 优雅 高定 | 经典 Bodoni，锋利优雅，高定感 |
| `dm-serif-display` | DM Serif Display | DM Serif Display | 400 | 展示 衬线 厚实 友好 | 现代展示衬线，厚实友好 |
| `cormorant-garamond` | Cormorant Garamond | Cormorant Garamond | 300–700 | 古典 加拉蒙 纤细 文学 | 古典加拉蒙，纤细文学感 |
| `libre-baskerville` | Libre Baskerville | Libre Baskerville | 400–700 | 经典 衬线 可读 学术 | 经典巴斯克维尔，长文可读 |
| `fraunces` | Fraunces | Fraunces | 100–900 | 复古 软衬线 品牌 个性 | 复古软衬线，个性强，适合品牌 |
| `instrument-serif` | Instrument Serif | Instrument Serif | 400 | 窄体 展示 编辑 时尚 | 窄体展示衬线，编辑设计常用 |
| `bebas-neue` | Bebas Neue | Bebas Neue | 400 | 压缩 大写 海报 高声量 | 全大写压缩无衬，海报与货架 |
| `anton` | Anton | Anton | 400 | 超粗 压缩 冲击 海报 | 超粗压缩无衬，冲击力强 |
| `archivo-black` | Archivo Black | Archivo Black | 400 | 厚重 无衬 粗野 现代 | 厚重无衬，现代粗野主义 |
| `oswald` | Oswald | Oswald | 200–700 | 窄体 无衬 混排 标题 | 窄体无衬，适合中英混排标题 |
| `archivo-narrow` | Archivo Narrow | Archivo Narrow | 400–700 | 窄体 无衬 信息密度 编辑 | 窄体无衬，信息密度高 |
| `rubik-mono-one` | Rubik Mono One | Rubik Mono One | 400 | 等宽 粗体 数字 科技 | 等宽粗体，数字与科技 |
| `monoton` | Monoton | Monoton | 400 | 霓虹 线条 装饰 活动 | 霓虹线条体，装饰性强 |
| `space-grotesk` | Space Grotesk | Space Grotesk | 300–700 | 几何 怪诞 科技 编辑 | 几何怪诞体，科技编辑 |
| `syne` | Syne | Syne | 400–800 | 实验 几何 艺术 时尚 | 实验几何体，艺术与时尚 |
| `unbounded` | Unbounded | Unbounded | 200–900 | 圆角 未来 潮流 科技 | 圆角未来体，Web3 与潮流 |
| `chakra-petch` | Chakra Petch | Chakra Petch | 300–700 | 方角 科技 数据 硬件 | 方角科技体，数据与硬件 |
| `inter-tight` | Inter Tight | Inter Tight | 100–900 | 紧凑 无衬 元信息 界面 | 紧凑无衬，元信息与界面感 |
| `caveat` | Caveat | Caveat | 400–700 | 手写 马克笔 笔记 随笔 | 手写马克笔，笔记与随笔 |
| `ibm-plex-mono` | IBM Plex Mono | IBM Plex Mono | 100–700 | 等宽 工程 数据 编号 | 工程感等宽，数据与编号 |
| `jetbrains-mono` | JetBrains Mono | JetBrains Mono | 100–800 | 等宽 代码 技术 数据 | 开发者等宽，代码感强 |

## 32 组字体组合

每组定义展示体、正文体、元信息体三个角色，以及字重、字距、行高。
展示体只用于书名；副标题换正文字体；元信息用中性体收口。一张封面最多三族。

| # | 名称 | 展示体 | 正文 | 元信息 | 字距 / 行高 | 气质 | 覆盖 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T01 | 硬朗编辑 | 思源黑体 900 | 思源黑体 400 | Inter Tight 500 | -0.03em / 0.92 | 理性、强势、可信 | sc |
| T02 | 文学宋 | 思源宋体 600 | 思源黑体 300 | 思源黑体 500 | 0.05em / 1.14 | 安静、有年代感 | sc |
| T03 | 高定细黑 | 思源黑体 200 | 思源黑体 300 | Inter Tight 300 | 0.08em / 1.08 | 昂贵、克制、有距离感 | sc |
| T04 | 粗野宣言 | 思源黑体 900 | 思源黑体 700 | IBM Plex Mono 700 | -0.055em / 0.86 | 冲撞、直接、贴墙宣言 | sc |
| T05 | 杂志迪多 | Playfair Display 700 | 思源黑体 300 | Inter Tight 400 | 0.005em / 1.0 | 锋利、时髦、主编判断力 | latin |
| T06 | 机构衬线 | 思源宋体 600 | 思源宋体 400 | 思源黑体 500 | 0.08em / 1.22 | 庄重、正式、可归档 | sc |
| T07 | 数据等宽 | 思源黑体 700 | 思源黑体 400 | IBM Plex Mono 400 | 0.02em / 1.0 | 冷静、可检索、终端输出 | sc |
| T08 | 宋黑对位 | 思源宋体 600 | 思源黑体 300 | 思源黑体 500 | 0.02em / 1.1 | 有观点、有停顿、长篇评论 | sc |
| T09 | 暗调反白 | 思源黑体 200 | 思源黑体 300 | 思源黑体 400 | 0.08em / 1.1 | 低调、电影感、让图像说话 | sc |
| T10 | 毛笔楷 | 马善政楷书 400 | 思源宋体 400 | 思源黑体 400 | 0.06em / 1.2 | 温和、手写、有生活气 | sc |
| T11 | 压缩标题 | Oswald 700 | 思源黑体 400 | IBM Plex Mono 400 | 0.01em / 0.95 | 速度感、音量感、横向撑满 | latin |
| T12 | 现代宋 | 思源宋体 700 | 思源黑体 400 | 思源黑体 500 | 0em / 1.05 | 稳重、成熟、书卷兼商业 | sc |
| T13 | 霞鹜文楷 | 霞鹜文楷 400 | 霞鹜文楷 400 | 思源黑体 400 | 0.03em / 1.16 | 温润、耐读、有人情味 | sc |
| T14 | 小薇美术宋 | 站酷小薇 400 | 思源黑体 400 | 思源黑体 400 | 0.06em / 1.12 | 高对比、文艺、东方现代 | sc |
| T15 | 庆科黄油 | 站酷庆科黄油 400 | 思源黑体 400 | 思源黑体 400 | 0.03em / 1.05 | 粗圆、亲切、有分量 | sc |
| T16 | 快乐体 | 站酷快乐 400 | 思源黑体 400 | 思源黑体 400 | 0.02em / 1.12 | 轻松、童趣、手绘 | sc |
| T17 | 龙藏书法 | 龙藏体 400 | 思源宋体 400 | 思源黑体 400 | 0.04em / 1.18 | 刀刻感、硬朗、江湖气 | sc |
| T18 | 志莽行书 | 志莽行书 400 | 思源宋体 400 | 思源黑体 400 | 0.03em / 1.2 | 流动、文人、抒情 | sc |
| T19 | 柳建毛草 | 柳建毛草 400 | 思源宋体 400 | 思源黑体 400 | 0.02em / 1.22 | 狂草、气势、艺术性 | sc |
| T20 | 黑金主义 | 思源黑体 900 | 思源宋体 300 | Playfair Display 400 | -0.02em / 0.94 | 强对比、溢价、机构感 | sc |
| T21 | 日式明朝 | Shippori 明朝 600 | Shippori 明朝 400 | 思源黑体 400 | 0.05em / 1.14 | 优雅、克制、日本编辑 | han |
| T22 | 日式古董 | Shippori Antique 400 | Shippori Antique 400 | 思源黑体 400 | 0.04em / 1.12 | 安静、档案、低对比 | han |
| T23 | 现代角黑 | Zen 角黑 700 | Zen 角黑 400 | 思源黑体 400 | -0.01em / 1.02 | 锐利、中性、现代 | han |
| T24 | 圆体亲和 | Zen 丸黑 500 | 思源黑体 400 | 思源黑体 400 | 0.03em / 1.1 | 圆润、友好、大众 | han |
| T25 | 教科书楷 | Klee One 400 | 思源宋体 400 | 思源黑体 400 | 0.04em / 1.18 | 铅笔书写、温和、教育感 | han |
| T26 | 像素科技 | DotGothic16 400 | 思源黑体 400 | DotGothic16 400 | 0.02em / 1.06 | 像素、数字、怀旧科技 | han |
| T27 | 粗圆海报 | Dela Gothic 400 | 思源黑体 400 | IBM Plex Mono 400 | -0.02em / 0.92 | 超粗、海报、强首读 | han |
| T28 | 复古招牌 | Reggae One 400 | 思源黑体 400 | 思源黑体 400 | 0.01em / 1.02 | 复古招牌、厚重、有个性 | han |
| T29 | 装饰实验 | Rampart One 400 | 思源黑体 400 | IBM Plex Mono 400 | 0.02em / 1.0 | 立体描边、潮流、活动 | han |
| T30 | 古典西文 | Cormorant Garamond 600 | 思源宋体 400 | Inter Tight 400 | 0.04em / 1.08 | 古典、纤细、文学编辑 | latin |
| T31 | 未来无衬 | Space Grotesk 700 | 思源黑体 400 | Space Grotesk 400 | -0.01em / 1.0 | 几何、未来、科技编辑 | latin |
| T32 | 手写西文 | Caveat 700 | 思源黑体 400 | Inter Tight 400 | 0.02em / 1.05 | 随手笔记、轻松、个人化 | latin |

## 加载方式

生成器会做四件事，缺一不可：

1. `<link rel="preconnect">` 预热 `fonts.googleapis.com` 与 `fonts.gstatic.com`；
2. 只请求当前组合真正用到的 family 与字重，例如
   `family=Shippori+Mincho:wght@400;600&family=Noto+Sans+SC:wght@400`；
3. `display=swap`，字体未到时先显示回退字形，不出现空白；
4. 写入 `document.fonts.ready` 标记，导出 PNG/PDF 时等 `[data-fonts="ready"]` 再截图。

导出脚本如果不等待 `fonts.ready`，截图会截到回退的宋体或黑体，看起来「字体没生效」。

## 缺字处理

B、C 级字体不是不能用，是不能盲用。三条规则：

1. **标题先检测**。`python tools/check_fonts.py --online --sample "你的书名"`，
   输出缺字列表；缺字就换字体，或把缺字改成不依赖该字体的短标题。
2. **缺字必须回退到 A 级**。字体栈固定为 `'展示体', 'Noto Sans SC', ...`，
   缺字时只影响单个字，不会整行失效。
3. **B、C 级不做正文字体**。副标题、作者、出版信息一律 A 级，避免小字缺字难发现。

## 选择顺序

| 内容 | 优先组合 | 备选 |
| --- | --- | --- |
| 商业、经管、机构报告 | T01 T06 T20 | T07 T12 T23 |
| 文学、散文、诗集 | T02 T13 T21 | T25 T30 T10 |
| 艺术、设计、展览 | T03 T05 T22 | T14 T26 T19 |
| 科技、数据、AI | T07 T31 T23 | T26 T11 T03 |
| 青年、活动、潮流 | T04 T27 T29 | T16 T24 T28 |
| 传统文化、地方志 | T10 T17 T18 | T19 T14 T21 |
| 童书、生活方式 | T16 T24 T15 | T25 T28 T32 |

## 验证命令

```bash
# 在线字体全部可用性 + 缺字实测（约 2–3 分钟）
python tools/check_fonts.py --online

# 只查某个书名在某套字体下是否缺字
python tools/check_fonts.py --online --sample "三品合一破局内卷"

# 封面门禁（会检查字体来源、CDN 白名单、基础字体禁用、缺字风险）
python tools/verify_cover.py cover.html --recipe R12 --title "三品合一"
```
