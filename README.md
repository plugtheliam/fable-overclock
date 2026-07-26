<div align="center">

**English** · [中文](README.zh.md) · [日本語](README.ja.md) · [Español](README.es.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [한국어](README.ko.md)

# fable-overclock

## Reliable output from the coding model you already use.
### Make every model earn your trust.

Sonnet and DeepSeek make up numbers and skip the check. Opus over-builds and drifts past what
you asked. fable-overclock fixes the *behavior*, not the model: the cheap models cite every
figure and say UNKNOWN instead of guessing; Opus does exactly what you asked, then stops. Same
model — output you can actually ship. Measured, not promised: on DeepSeek, the share of figures
that carry a source went **4% → 100%**.

The name is literal — like overclocking a CPU, it pushes the chip you already have to its real
limit, every time, by procedure instead of luck. It doesn't raise a model's raw IQ. One command.
stdlib-only. Works with the model you already run.

![MIT](https://img.shields.io/badge/license-MIT-green)
![zero deps](https://img.shields.io/badge/deps-stdlib%20only-brightgreen)
![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin%20%2B%20hook-8A63D2)
![tuned for](https://img.shields.io/badge/tuned-Opus%20%C2%B7%20Sonnet%20%C2%B7%20DeepSeek-orange)
![tests](https://img.shields.io/badge/tests-green-success)

</div>

![fable-overclock flagging a claim with no source](assets/demo-2x.gif)

## What each model gains

Every model has one expensive habit — a silent rewrite, a wrong number, an afternoon lost to
an API that never existed. fable-overclock knows each one and shuts it down — and proves it: in
testing, the gate flagged **100% of fabricated numbers with zero false positives**.

| Model | The habit that costs you | What you get instead |
|---|---|---|
| **Opus** | over-builds, drifts past the ask | exactly what you asked, then it stops — and names the simpler options it skipped |
| **Sonnet** | skips the check, drops its sources | every figure sourced, every requirement verified before it calls it done |
| **DeepSeek** | invents numbers and whole APIs | `UNKNOWN` instead of a confident lie; a second model double-checks the rest |

Two layers do it. A **contract** loads before the model writes its first token, so the
discipline is there from the start. A deterministic **gate** is the backstop — it scores the
output itself (no LLM judge) and catches any unsourced or made-up number before it lands. The
payoff: output you don't have to fact-check line by line. Full walkthrough in
[`docs/HOW-IT-WORKS.md`](docs/HOW-IT-WORKS.md).

## Why this exists

The most expensive model failure is often not a benchmark miss. It is a plausible number with no
source, an API that never existed, or an implementation that quietly exceeds the request. Better
models reduce these failures; they do not remove the need for a reproducible operating contract
and a deterministic backstop.

fable-overclock was first built during the brief June 2026 Fable access interruption. Access has
since been restored. The tool remains useful because reliability should travel with your workflow
rather than depend on one model or one release cycle.

## See it for yourself

Same model, same prompt: *"Write last month's investor update with the key numbers."*

**DeepSeek, on its own**
```
Revenue grew 38% last quarter, churn fell to 2.1%, and we added 14,000 users.
```
Confident. Sourced by nothing. You never gave it those numbers — it made them up. Ship that and
the mistake is now yours.

**DeepSeek, on fable-overclock**
```
I don't have last month's figures (UNKNOWN). Give me revenue, churn, and user
data and I'll write it — each number cited to its source.
```

The moment it stops guessing, your output changes with it: from a draft you have to fact-check
into something you can send as-is. That's the difference between "a model wrote this" and "I
can stand behind this."

## Install

### Option 1 — Claude Code plugin (recommended)

```
/plugin marketplace add https://github.com/plugtheliam/fable-overclock
/plugin install fable-overclock@plugtheliam
```

Use the full `https://` URL. The short `plugtheliam/fable-overclock` form makes Claude Code
clone over SSH, which fails on machines without a GitHub SSH key. Update with
`/plugin marketplace update plugtheliam`, remove with `/plugin uninstall fable-overclock@plugtheliam`.

### Option 2 — Manual (any setup, stdlib-only)

```bash
git clone https://github.com/plugtheliam/fable-overclock && cd fable-overclock
harness/install.sh                 # --global for every project · --uninstall to remove
export MYINC_PROFILE=sonnet        # or opus / deepseek / codex
```

Catch a made-up number right now — no install, no API key:

```bash
printf 'Revenue grew 38%% last quarter and we added 14,000 users.\n' \
  | python3 harness/gate/refuse.py        # flagged: two figures, no source
```

### Turn it on or off

The gate checks your prose (`.md`, `.txt`, …) and leaves code alone. To change that, type in
any session:

```
foc off        # pause the gate for this project
foc on         # resume
foc status     # is it on?
foc off all    # machine-wide (add `all` to any command)
```

Or set `MYINC_GATE=off`. Want it on *everything* you write, code included? `MYINC_GATE_ALL=1`.

## The proof

Scored by the gate the tool ships — no LLM judge, no hidden rubric. Reproduce it with one
command: `python3 harness/tests/bench.py`.

| Detection (offline, n=20) | value |  | DeepSeek, OFF → ON | OFF | ON |
|---|---|---|---|---|---|
| made-up claims caught | **100%** |  | figures that carry a source | 4% | **100%** |
| real claims wrongly flagged | **0%** |  | abstains when it can't know | 10/12 | **12/12** |

These measure how the model *behaves*, not how well it reasons — on a modest set (20 report
prompts + 12 unknowable-fact prompts), single run. The point isn't that the numbers are huge;
it's that they're reproducible. Run it on your own model. Method and caveats:
[`docs/BENCHMARK.md`](docs/BENCHMARK.md).

## How it compares

|  | fable-overclock | NeMo Guardrails | Guardrails AI | DeepEval |
|---|---|---|---|---|
| Runs inside Claude Code (plugin + hook) | ✅ | ❌ | ❌ | ❌ |
| Zero dependencies, no API key to start | ✅ | ❌ | ❌ | ❌ |
| Tuned per model | ✅ | ❌ | ❌ | ❌ |
| Tells the model to abstain, not invent | ✅ | partial | partial | ❌ (eval only) |
| Second model cross-checks claims | ✅ | ✅ (hallucination rail) | ❌ | ❌ |
| Works while you edit, not as a separate run | ✅ | ❌ | ❌ | ❌ |

The cross-check isn't new — NeMo's hallucination rail already verifies claims with a second
model. What's different here: it lives inside Claude Code, installs with one command, and is
tuned per model.

## What it doesn't do

It won't raise the ceiling on what your model can do. It lowers the floor on what it gets
wrong: invented numbers, unsourced claims, drift past the task. It reduces those. It doesn't
erase them. It doesn't change model weights, and it can't promise a *cited* number is correct —
it checks that a source is there and lets the verifier handle the rest. Don't take the numbers
on trust; run `harness/tests/bench.py` on your own model.

## Built in public

By a hands-on Founding CTO and Founding Engineer building reliability tools for production AI
workflows. Follow along on X: [@liampluglab](https://x.com/liampluglab).
A managed version lives at [myinc.app](https://myinc.app). Part of the **myinc-os** toolkit.

## License

MIT. See [`LICENSE`](LICENSE).
