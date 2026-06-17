# How it works

myinc-os is a thin, deterministic reliability layer around the model your Claude Code (or
Codex) session is already running. `python3` stdlib only — no services, no SDKs.

## The pieces (`harness/`)

- **`profiles/{opus,sonnet,deepseek,codex}.json`** — per-model dials. The same harness
  behaves differently per model because each fails differently: Opus over-engineers
  (lenient gate, anti-sprawl), Sonnet skips verification (strict), DeepSeek hallucinates
  (strictest + abstain + cross-verify). The active one resolves from `MYINC_PROFILE`.

- **`gate/contract.py`** — the *proactive* layer. Prints a compact reliability contract
  (source every figure, abstain instead of inventing, stay in scope, verify before
  finishing) tuned to the active profile. The `myinc-harness` skill front-loads it before
  the model produces.

- **`gate/lib.py` + `gate/spec_gate.py` + `gate/refuse.py`** — the *reactive* layer. A
  deterministic check: a factual claim (a $ amount, %, count, unit, or named metric) with no
  source on its line is flagged. Wired as a Claude Code `PreToolUse` hook (`spec_gate.py`) and
  runnable standalone (`refuse.py`). Tripwires, not verdicts — it flags; your reasoning
  writes the fix. Fail-open: it never bricks an unrelated tool call.

- **`gate/toggle.py`** — a `UserPromptSubmit` hook that intercepts `foc on` / `foc off` /
  `foc status` (add `all` for machine scope) so you can pause the gate without leaving the
  session. State lives in a file (`.myinc/gate` per project, `~/.myinc/gate` machine-wide);
  `MYINC_GATE=off` overrides everything.

## What the gate checks (scope)

By default the gate fires on **prose/document writes** — `.md`, `.markdown`, `.mdx`, `.txt`,
`.rst` — anywhere, since that's where unsourced claims actually ship. **Code is excluded**
(a `14000` in `users = 14000` is not a factual claim). Override:
`MYINC_GATE_ALL=1` checks every write; `MYINC_GATE_PATHS="<regex>"` sets a custom path filter.

- **`gate/verify.py` + `gate/provider.py`** — *cross-model verification*. Hands a cheap
  model's output + the source to a low-hallucination model (Opus) and asks it to flag any
  figure absent from the source. Backend `auto`: local `claude -p` if present, else an
  OpenAI-compatible endpoint (OpenRouter, or local Ollama via `MYINC_BASE_URL`).

- **`gate/rules/`** — `reliability.json` is the general, domain-agnostic pack (sourcing,
  no fabrication). Domain packs layer on top — see `gate/rules/cfo.json` and
  `examples/cfo-pack/`.

## Per-model strictness (why the gate is lenient on Opus, strict on DeepSeek)

The gate reads `profile.gate.strictness`. An ambiguous unsourced figure is a **warning**
on a high-calibration model (Opus = lenient) and a **block** on a model that hallucinates
(DeepSeek = strictest). Hard rules (a fabricated number caught by the verifier; a domain
pack's tripwire) block regardless.

## Install surfaces

- **Claude Code** — `harness/install.sh` adds the `myinc-harness` skill and the PreToolUse
  hook to `.claude/` (project) or `~/.claude` (`--global`). `--uninstall` reverses it.
- **Codex** — no PreToolUse hook, so the gate runs at *worktree-accept*:
  `harness/adapters/codex/accept-gate.sh` rejects a changeset whose deliverables break the
  rules.

## Run the proof

```bash
python3 harness/tests/test_gate.py         # the gate behaves per profile (deterministic)
python3 harness/tests/test_verify_cli.py   # the verifier backend resolution
python3 harness/gate/profile.py            # the active profile's dials
```
