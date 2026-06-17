#!/usr/bin/env python3
"""Front-loaded reliability contract — inject it BEFORE the model generates.

The gate (spec_gate.py / refuse.py) is REACTIVE: it flags unreliable output after the
fact. This is PROACTIVE: it hands the model a compact, per-profile checklist up front so
the output is reliable on the first pass. Domain-agnostic.

  from contract import build_contract
  text = build_contract()                 # general reliability contract for the active profile
  text = build_contract(profile=load_profile("deepseek"))

CLI:  python3 harness/gate/contract.py [--profile deepseek]
"""
import sys

try:
    from lib import load_profile, resolve_profile_name
except ImportError:
    from .lib import load_profile, resolve_profile_name

RELIABILITY = """RELIABILITY CONTRACT (read before you produce anything):
- SOURCE every figure, ANYWHERE it appears (table, prose, a flag). Each $ amount / % /
  named metric carries an inline `(source, date)` / `as of …`, OR is omitted.
- ABSTAIN, never guess: if a fact/number isn't in the provided source, write `UNKNOWN`.
  A fabricated source tag does not make a number real.
- STAY IN SCOPE: produce exactly what's asked; delete out-of-scope output.
- VERIFY before you finalize: check the output against every stated requirement.
- Output GROUNDS, never your chain-of-thought (reasoning_extraction-safe)."""

NOTES = {
    "opus": "Your failure is sprawl. Do exactly what's asked and stop; before adding anything extra, name 2 simpler options you rejected.",
    "sonnet": "Conclusion-first. Hit the asked shape; delete out-of-scope output. Escalate to Opus on deep multi-domain / pure-reasoning calls.",
    "deepseek": "Single-concern steps; re-read the requirements before each. If a fact isn't in the source, output UNKNOWN — don't invent symbols/APIs/numbers.",
    "codex": "Work outcome-first (goal, success, evidence, output shape). You won't self-flag uncertainty, so source every claim and abstain when unsure.",
}


def build_contract(profile=None):
    profile = profile or load_profile()
    name = profile.get("name", "?")
    parts = [
        "=== RELIABILITY CONTRACT (profile: %s) ===" % name,
        NOTES.get(name, "Produce reliable output: source everything, abstain when unsure, stay in scope, verify before finishing."),
        "",
        RELIABILITY,
        "",
        "PREFLIGHT (run on your draft before you emit it): every figure sourced or UNKNOWN? "
        "nothing out of scope? nothing invented? If not, fix it now.",
        "=== END CONTRACT ===",
    ]
    return "\n".join(parts)


def main(argv):
    prof = load_profile(argv[argv.index("--profile") + 1]) if "--profile" in argv else load_profile()
    print(build_contract(prof))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
