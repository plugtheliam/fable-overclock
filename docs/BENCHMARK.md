# Benchmark — what's measured, and how to reproduce it

Every number here is produced by `harness/tests/bench.py` and scored by the **same
deterministic gate the tool ships** — no LLM judges, no hidden rubric. Run it yourself:

```bash
python3 harness/tests/bench.py --detection                          # Part A, offline
OPENROUTER_API_KEY=… python3 harness/tests/bench.py --model deepseek/deepseek-v4-flash   # + Part B
```

This measures **reliability behavior** (does the model source its claims and abstain when
it can't), not raw capability. We make no claim that the harness raises a model's reasoning.

## Part A — gate detection (deterministic, offline, n=20)

A labeled corpus: 10 unsourced quantified claims that *should* be flagged, 10 of the same
claims *with* a source that should be left alone.

| metric | value |
|---|---|
| unsourced claims caught (recall) | 10/10 = **100%** |
| sourced claims wrongly flagged (FPR) | 0/10 = **0%** |
| precision | **100%** |

Deterministic — same result on every machine, no network.

## Part B — behavior OFF vs ON (live, gate-scored)

Model: `deepseek/deepseek-v4-flash` via OpenRouter. Run date: 2026-06-17, temperature 0.
OFF = bare prompt. ON = the same prompt with the per-model reliability contract loaded
(`harness/gate/contract.py`). Each output scored by the gate.

| metric | OFF | ON |
|---|---|---|
| claim-lines carrying a source (mean, 20 prompts that *provide* the source) | 4% | **100%** |
| abstains when the fact is unknowable (12 unknowable-fact prompts) | 10/12 | **12/12** |

Reading it: given data + its provenance, the bare model reports the numbers but drops the
citation (4%); with the contract it carries `(source, date)` inline on every figure. Asked
for a fact it cannot know, the bare model still invents sometimes (10/12); with the contract
it abstains every time.

## Honest caveats

- Modest n (32 live prompts), single model, single run. Live-model numbers vary a few points
  run-to-run (providers aren't perfectly deterministic). The detection numbers (Part A) do not.
- The ON citation rate reads 100% because every prompt *supplies* the source and the contract
  enforces carrying it inline — it measures whether the model keeps the provenance, not whether
  it can find one. The gate (Part A) is the deterministic backstop for everything else.
- Add `--model` for any OpenAI-compatible model (or point `MYINC_BASE_URL` at a local one)
  and rerun. The scorer doesn't change, so your numbers are comparable to these.
