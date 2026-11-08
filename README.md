# 歌手合成引擎 · AI 提示词合集

七个提示词。整份复制,粘贴给一个有 shell 权限的 AI agent,它就能在那台机器上把桥装好、
并开始驱动编辑器 —— **不用你点鼠标,也不需要它模拟键盘**。

其中 01–06 是我构建并验证过的六个仓库,07 是别人的。

## 七个提示词

| # | 编辑器 | 提示词 | 对应仓库 | 它靠什么进去 |
|---|---|---|---|---|
| 01 | Synthesizer V Studio 1.x / 2.x | [md](prompts/01-synthesizer-v.md) · [txt](prompts/01-synthesizer-v.txt) | [lh-synthv-mcp](https://github.com/ppzbr/lh-synthv-mcp) | 编辑器自己的 Lua 宿主(这七个里唯一有官方脚本 API 的) |
| 02 | CeVIO AI(唱的那一半) | [md](prompts/02-cevio-ai.md) · [txt](prompts/02-cevio-ai.txt) | [lh-cevio-mcp](https://github.com/ppzbr/lh-cevio-mcp) | 注入进程内的 CLR 加载器 |
| 03 | VoiSona | [md](prompts/03-voisona.md) · [txt](prompts/03-voisona.txt) | [lh-voisona-mcp](https://github.com/ppzbr/lh-voisona-mcp) | 注入原生 DLL(zig 构建) |
| 04 | VOCALOID 6 | [md](prompts/04-vocaloid6.md) · [txt](prompts/04-vocaloid6.txt) | [lh-vocaloid6-mcp](https://github.com/ppzbr/lh-vocaloid6-mcp) | 与 VoiSona 同一个 DLL |
| 05 | Piapro Studio NT | [md](prompts/05-piapro-studio-nt.md) · [txt](prompts/05-piapro-studio-nt.txt) | [lh-piapro](https://github.com/ppzbr/lh-piapro) | 工程文件 + 一个 drop-in(**没有 MCP**) |
| 06 | X Studio(网易云音乐内) | [md](prompts/06-x-studio.md) · [txt](prompts/06-x-studio.txt) | [lh-xstudio](https://github.com/ppzbr/lh-xstudio) | 工程文件 + 一个 drop-in(**没有实时控制**) |
| 07 | OpenUtau | [txt](prompts/07-openutau-mcp-bridge.txt) | 第三方:[openutau-mcp-bridge](https://github.com/KakaruHayate/openutau-mcp-bridge) | 插件 DLL(走 OpenUtau 的外挂 BatchEdit 机制) |

`all-prompts.txt` 是七份连在一起的版本,每份前面有 `FILE:` 分隔线,方便一口气读完。

## 怎么用

打开对应那个文件,**全选,复制,整段粘给 agent**。不用改任何东西:

- 每个提示词里都写着真的 `git clone https://github.com/...` 地址,不是占位符;
- 每个提示词都自带背景、规则、步骤和排错表,**不需要你先解释这个仓库是什么**;
- 提示词里提到的每个仓内路径,都在对应仓库的自检里被核对过(全新 clone 之后跑测试,
  路径对不上就报错),所以它不会让你去运行一个不存在的文件。

一句话:`把这份文件粘进去,然后把 agent 报的东西念给它听` 就够了。

## 各自到底能做到什么(这部分最重要)

这七个不是同一成熟度的东西,提示词本身也这么写 —— **做不到的地方它直接说做不到**,
而不是描述一个能力然后让你发现根本没有。

| 引擎 | 音符级实时控制 | 实际状态 |
|---|---|---|
| Synthesizer V 1.x/2.x | ✅ 可以 | 音符、歌词、音高、音素、时间、走带全可以;`UNDO`/`REDO`/`SAVE` 做不到 —— 枚举过宿主的成员表,它确实没有这些入口,agent 会直接答 `err` |
| CeVIO AI | ✅ 可以 | 21 个工具。**渲染默认拒绝**:实测四次要约里有一次渲染把编辑器直接弄死了(无法保存),所以除非你明确要求并加 `force`,它不渲染 |
| VoiSona | ⚠️ 传输全通,音符未定 | 注入、内存读写、扫描、工具全都能用;但"音符词汇表"(内存偏移)还没定下来。偏移会随编辑器更新而变,而错的偏移不会报错 —— 它会读出看着合理的垃圾再写回去。所以要么让人手动改一个音符来对,要么走 UI 自动化那一层 |
| VOCALOID 6 | ⚠️ 同上,且更悬 | 它其实是 WPF + .NET,不是原生 C++ 编辑器,而 GC 会移动托管对象 —— 今天能用的指针链明天可能就失效。提示词里明写着:**在有人确认链稳不稳定之前,不要开始做音符地图** |
| Piapro Studio NT | ❌ 没有 | 没有厂商脚本 API,没有插件 API,我也没给它写 MCP 桥。能做的是:把它当**工程文件**读写(`.ppsf`,外加十几个格式互转、一套批量作业),以及用 drop-in 把 11 个热键动作放进编辑器里。热键改的是**文件**,不是编辑器内存里的那个工程 |
| X Studio | ❌ 没有 | 同样没有实时控制。但它的工程格式已经被解开了:`.svip3` 是 Protocol Buffers,schema 从它自己的 exe 里扒了出来,codec 拿全部 8 个自带模板工程逐音符对过(21 轨、4535 个音符,往返一致)。所以文件层的音符读写是真的,**实时控制是假的** |
| OpenUtau | ✅ 可以(第三方) | 47 个工具。见下面「07 是别人的」 |

一句总结:**Synthesizer V 和 CeVIO 是成熟的;VoiSona / VOCALOID 6 的通道修好了但音符映射还没定;
Piapro 和 X Studio 只能在文件层做事。** 提示词里每一条都照这个写。

## 为什么 .md 和 .txt 都有

- `.md` —— 在 GitHub 上直接渲染,方便你在这里读;
- `.txt` —— 用来粘贴。UTF-8 带 BOM、CRLF 换行,这样任何版本的记事本打开都不会是乱码或者一行长条
  (提示词里有长破折号、`风雪千千`、`D:\文档` 这些非 ASCII 内容)。

内容是一样的。`.md` 是各自仓库 `prompt.md` 的原样文本,`.txt` 是和它同文本的粘贴版。

## 这些提示词的自我要求

写这些的时候按三条来:

1. **只写实测的东西。** 能跑通才写"能",跑不通就写"做不到"和为什么。比如 X Studio 的实时控制这条,
   是查过它内嵌的 gRPC 客户端、确认合成是在网易服务器上做的之后才写"没有"的,不是猜的。
2. **不假装安全。** 会弄死编辑器的那种调用(CeVIO 渲染)默认拒绝,而不是"请谨慎使用"。
3. **不碰你的桌面。** 所有路径都是"进程内注入 / 编辑器自己的加载机制 / 工程文件",
   不是模拟点击和键盘。唯一需要人的地方,提示词会明说需要人:SynthV 要在菜单里点一次启动脚本,
   OpenUtau 要在钢琴卷帘里打开一个声部,否则端点根本不存在。

## 07 是别人的

`07-openutau-mcp-bridge.txt` 不是我写的,是
[KakaruHayate/openutau-mcp-bridge](https://github.com/KakaruHayate/openutau-mcp-bridge) 的安装提示词,
原样收录,方便和上面六个放在一起看。

**它的授权和上面六个不一样:那个项目是 MPL-2.0,不是 MIT。** 所以这一个文件也是 MPL-2.0,
不是本仓库 MIT 的一部分 —— 详见 [NOTICE.md](NOTICE.md)。我没验证过它,也没跑过它;
它自己的正文里写着它的来源和状态。

## 授权

本仓库自己的内容(01–06 的提示词、这份说明、README 等)是 MIT,见 [LICENSE](LICENSE)。
`prompts/07-openutau-mcp-bridge.txt` 是 MPL-2.0,见 [NOTICE.md](NOTICE.md)。

那六个引擎仓库各自有独立的授权(MIT)和独立的说明,这个仓库只是它们的提示词合集。
