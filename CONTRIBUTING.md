# Contributing

fable-overclock is stdlib-only Python by design — no dependencies, no build step. Keep it
that way; a PR that adds a runtime dependency will be asked to remove it.

## Ground rules

- **Honest claims only.** This repo's whole pitch is reliability. Any new claim in the
  README or docs must be backed by something a reader can run (`harness/tests/`).
- **stdlib only.** No `pip install`. If you need a model call, go through
  `harness/gate/provider.py` (OpenAI-compatible, works with OpenRouter or a local model).
- **Tests must stay green.** Run before you push:
  ```bash
  python3 harness/tests/test_gate.py
  python3 harness/tests/test_verify_cli.py
  python3 harness/tests/bench.py --detection
  ```

## Good first contributions

- **A new rule-pack** under `harness/gate/rules/` (see `examples/cfo-pack/` for the shape).
- **A new model profile** under `harness/profiles/` tuned to a model's failure mode.
- **Detector precision/recall** — add labeled cases to `bench.py`'s corpus and improve
  `CLAIM_LINE_RE` without raising the false-positive rate (currently 0%).

## PRs

Small, focused, with a one-line "what + why." If it changes behavior, add or update a test.
MIT-licensed; by contributing you agree your work is too.
