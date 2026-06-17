---
name: myinc-harness
description: A per-model reliability contract for Claude Code. Loaded before you produce anything, it makes the model you're running source its claims, abstain instead of inventing, stay in scope, and verify before finishing — tuned to that model's failure mode (Opus/Sonnet/DeepSeek). Non-blocking. Invoke at the start of any task that produces factual output, or let it auto-load.
---

# myinc-harness — make the model you run more reliable

Non-blocking. No gate walls — it front-loads the discipline that separates reliable
output from confident-but-wrong output, tuned to the model you're on.

## 0. Load your profile

```
python3 harness/gate/profile.py        # shows the active profile's dials
python3 harness/gate/contract.py       # prints the reliability contract to follow
```

## 1. The reliability contract (every task)

- **Source every figure.** Each $ amount / % / named metric carries an inline
  `(source, date)` / `as of …`, or is omitted. No bare claims.
- **Abstain, never guess.** If a fact/number isn't in the source, write `UNKNOWN`. A
  fabricated citation doesn't make it real.
- **Stay in scope.** Produce exactly what's asked; delete out-of-scope output.
- **Verify before finishing.** Check the output against every stated requirement.
- Output **grounds**, never your chain-of-thought (reasoning_extraction-safe).

## 2. Per-model emphasis

- **Opus** — failure is sprawl: do exactly what's asked, then stop; name 2 simpler options
  you rejected before adding anything extra.
- **Sonnet** — conclusion-first; escalate to Opus on deep multi-domain / pure reasoning.
- **DeepSeek** — single-concern steps; never invent a symbol/API/number — abstain.
- **Codex (GPT-5.5)** — outcome-first; it won't self-flag uncertainty, so source every claim.

## 3. Optional: cross-model verify

For factual output from a cheap model, have a low-hallucination model (Opus) check it
against the source and flag anything invented:

```
python3 harness/gate/verify.py REPORT.md RUBRIC.md SOURCE.md   # routes via claude-cli or OpenRouter
```

## 4. The gate (safety net)

`harness/gate/` ships a PreToolUse hook + `refuse.py` that deterministically flag output
breaking the rules above (e.g. a figure with no source). Tripwires, not verdicts — they
flag; your reasoning still writes the fix. Domain rule-packs (e.g. a CFO that blocks a
spend with no verdict) layer on the general reliability pack.
