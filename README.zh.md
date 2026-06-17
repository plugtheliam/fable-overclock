<div align="center">

[English](README.md) · **中文** · [日本語](README.ja.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [한국어](README.ko.md)

# fable-overclock

## 让 Opus、Sonnet 和 DeepSeek 跑出 Fable 级的水准。
### 用你还能跑的模型，榨出 Fable 级的输出。

Sonnet 和 DeepSeek 张口就编数字，懒得回头核对；Opus
则爱过度发挥，越做越偏离你的本意。fable-overclock 治的不是模型，而是这股*行为*：便宜的模型每个数字
都得交代来源，不确定就老实说"我不知道"，绝不瞎猜;Opus 只做你要的那件事，做完就收手。同一个
模型 —— 输出却是你真能直接交付的。用数据说话，而非空口承诺：在 DeepSeek 上，带有出处的数字占比从 **4% 升到 100%**。

名字是字面意思 —— 就像给 CPU 超频，它把你手里这块芯片*每一次*都逼到真正的极限，靠的是流程，不是运气。它不会拔高模型的原始智商。一条
命令搞定。纯 stdlib。你现在跑的那个模型，拿来即用。

![MIT](https://img.shields.io/badge/license-MIT-green)
![zero deps](https://img.shields.io/badge/deps-stdlib%20only-brightgreen)
![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin%20%2B%20hook-8A63D2)
![tuned for](https://img.shields.io/badge/tuned-Opus%20%C2%B7%20Sonnet%20%C2%B7%20DeepSeek-orange)
![tests](https://img.shields.io/badge/tests-green-success)

</div>

![fable-overclock flagging a claim with no source](assets/demo-2x.gif)

## 每个模型的收益

每个模型都有一个让你付出代价的坏毛病 —— 一次悄无声息的改写、一个错误的数字、为一个根本不存在
的 API 搭进去的一整个下午。fable-overclock 把这些毛病摸得门儿清，一一掐灭 —— 而且能证明：测试中，关卡抓出了 **100% 的编造数字，零误报**。

| 模型 | 让你付出代价的坏毛病 | 你换来的结果 |
|---|---|---|
| **Opus** | 过度发挥，偏离需求 | 只做你要的，做完就停 —— 还会列出它跳过的更简单方案 |
| **Sonnet** | 跳过核对，丢掉来源 | 每个数字都有出处，每项要求都先验证再收尾 |
| **DeepSeek** | 编造数字、整套 API 都敢编 | 与其自信地撒谎，不如返回 `UNKNOWN`；其余的交由第二个模型复核 |

靠的是两层机制。一份**契约**在模型写下第一个 token 之前就加载完毕，纪律从一开始就在。一道
确定性的**关卡**则是最后防线 —— 评分由它自己完成（没有 LLM 裁判），任何无出处或凭空捏造的数字，落地之前都会被它逮住。回报很
实在：输出不必再逐行去核实。完整讲解见 [`docs/HOW-IT-WORKS.md`](docs/HOW-IT-WORKS.md)。

## 为什么是现在

<!-- FABLE-MOMENT:start — time-bound. Remove when Fable access is restored to non-US founders. -->
2026 年 6 月，美国出口管制切断了 Anthropic 的 Fable 5 与 Mythos 5 对所有外国国民的供应。
如果你是非美国开发者，一夜之间，最前沿的模型就从你的技术栈里消失了。你拿不回来 —— 那就让手里
还剩的这个模型，做出前沿级的活儿 —— 靠测量，而不是指望。
<!-- FABLE-MOMENT:end -->

## 亲眼看看

同一个模型，同一条提示词：*"把上个月的投资人简报写出来，带上关键数字。"*

**DeepSeek，单打独斗**
```
Revenue grew 38% last quarter, churn fell to 2.1%, and we added 14,000 users.
```
信誓旦旦。零出处。这些数字你压根没给过它 —— 全是它自己编的。把这个发出去，错就成了你的错。

**DeepSeek，跑在 fable-overclock 上**
```
I don't have last month's figures (UNKNOWN). Give me revenue, churn, and user
data and I'll write it — each number cited to its source.
```

它一停止瞎猜，你的输出就跟着变了：从一份还得去核实的草稿，变成一份可以原样发出的成品。这就是
"模型写的"和"我敢替它背书"之间的区别。

## 安装

### 方式一 —— Claude Code 插件（推荐）

```
/plugin marketplace add https://github.com/plugtheliam/fable-overclock
/plugin install fable-overclock@plugtheliam
```

请用完整的 `https://` 链接。简写 `plugtheliam/fable-overclock` 会让 Claude Code 走 SSH
克隆，在没有 GitHub SSH 密钥的机器上会失败。更新用 `/plugin marketplace update plugtheliam`，
卸载用 `/plugin uninstall fable-overclock@plugtheliam`。

### 方式二 —— 手动（任意环境，纯 stdlib）

```bash
git clone https://github.com/plugtheliam/fable-overclock && cd fable-overclock
harness/install.sh                 # --global for every project · --uninstall to remove
export MYINC_PROFILE=sonnet        # or opus / deepseek / codex
```

现在就抓一个编造的数字 —— 免安装，免 API key：

```bash
printf 'Revenue grew 38%% last quarter and we added 14,000 users.\n' \
  | python3 harness/gate/refuse.py        # flagged: two figures, no source
```

### 开关自如

关卡只检查你的文字（`.md`、`.txt`……），代码一概放行。想改这个行为，在任意会话里输入：

```
foc off        # pause the gate for this project
foc on         # resume
foc status     # is it on?
foc off all    # machine-wide (add `all` to any command)
```

或者设置 `MYINC_GATE=off`。想让它管住你写的*一切*、连代码也不放过？`MYINC_GATE_ALL=1`。

## 证据

由工具自带的关卡打分 —— 没有 LLM 裁判，没有藏着掖着的评分表。一条命令即可复现：
`python3 harness/tests/bench.py`。

| 检测（离线，n=20） | 数值 |  | DeepSeek，OFF → ON | OFF | ON |
|---|---|---|---|---|---|
| 编造声明被抓住 | **100%** |  | 带有出处的数字 | 4% | **100%** |
| 真实声明被误判 | **0%** |  | 不知道就坦白弃权 | 10/12 | **12/12** |

这衡量的是模型怎么*行事*，而不是它推理得多好 —— 基于一个适中的样本（20 个报告提示 + 12 个无法得知的事实提示），单次运行。重点不在于数字有多大，而在于它可复现。拿你自己的模型跑一遍。方法与注意事项见
[`docs/BENCHMARK.md`](docs/BENCHMARK.md)。

## 横向对比

|  | fable-overclock | NeMo Guardrails | Guardrails AI | DeepEval |
|---|---|---|---|---|
| 在 Claude Code 内运行（插件 + 钩子） | ✅ | ❌ | ❌ | ❌ |
| 零依赖，开箱即用无需 API key | ✅ | ❌ | ❌ | ❌ |
| 按模型逐一调校 | ✅ | ❌ | ❌ | ❌ |
| 让模型弃权，而非编造 | ✅ | partial | partial | ❌ (eval only) |
| 第二个模型交叉核对声明 | ✅ | ✅ (hallucination rail) | ❌ | ❌ |
| 边写边管，而非另跑一趟 | ✅ | ❌ | ❌ | ❌ |

交叉核对不算新鲜 —— NeMo 的幻觉防护栏早就用第二个模型来验证声明。这里不一样的地方是：它就活在
Claude Code 里，一条命令装好，还按模型逐一调校。

## 它做不到什么

它不会拔高你模型能力的上限。它降的是出错的下限：编造的数字、无出处的声明、偏离任务。这些它能
减少，但不能根除。它不改动模型权重，也无法保证一个*已注明出处*的数字就是对的 —— 它只核查出处
是否存在，剩下的交给验证器去办。别盲信这些数字；拿你自己的模型跑一遍
`harness/tests/bench.py`。

## 公开构建

作者是一位非美国创始人，因出口管制痛失 Fable，转而为我们其余人还跑得动的那些模型打造可靠性
工具。来 X 围观：[@liampluglab](https://x.com/liampluglab)。托管版见
[myinc.app](https://myinc.app)。属于 **myinc-os** 工具包的一部分。

## 许可证

MIT。详见 [`LICENSE`](LICENSE)。
