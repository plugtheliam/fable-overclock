#!/usr/bin/env python3
"""UserPromptSubmit hook — type `foc on` / `foc off` / `foc status` to toggle the gate.

Intercepts those commands so they never reach the model: it writes the gate state
file and shows you a one-line status (via the block `reason`). Any other prompt
passes through untouched. Fail-open: on any error it stays silent and lets the
prompt proceed.

  foc off            turn the gate off for THIS project (cwd/.myinc/gate)
  foc on             turn it back on for this project
  foc off all        turn it off machine-wide (~/.myinc/gate)
  foc on all         turn it back on machine-wide
  foc status         show whether the gate is currently on

stdin: a Claude Code UserPromptSubmit event (uses the `prompt` field).
"""
import json
import re
import sys

try:
    from lib import gate_enabled, set_gate_state, gate_state_path, _read_state
except ImportError:
    from .lib import gate_enabled, set_gate_state, gate_state_path, _read_state

CMD_RE = re.compile(
    r"^\s*(?:foc|fable-overclock)\s+(on|off|status)(?:\s+(all|machine|project))?\s*$",
    re.I,
)


def _block(reason):
    print(json.dumps({"decision": "block", "reason": reason}))


def main():
    try:
        event = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return 0  # not JSON — let it through
    prompt = (event.get("prompt") or "").strip()
    m = CMD_RE.match(prompt)
    if not m:
        return 0  # not a foc command — pass through untouched

    action = m.group(1).lower()
    scope = "machine" if (m.group(2) or "").lower() in ("all", "machine") else "project"

    if action == "status":
        proj = _read_state("project")
        mach = _read_state("machine")
        state = "ON" if gate_enabled() else "OFF"
        _block(
            "fable-overclock gate is %s. project=%s machine=%s "
            "(env MYINC_GATE overrides). Toggle: `foc off` / `foc on` / add `all` for machine-wide."
            % (state, proj or "unset", mach or "unset")
        )
        return 0

    on = action == "on"
    try:
        path = set_gate_state(on, scope=scope)
    except Exception as e:
        _block("fable-overclock: could not write gate state (%s). Use MYINC_GATE=off instead." % e)
        return 0
    where = "machine-wide" if scope == "machine" else "this project"
    _block("fable-overclock gate turned %s for %s (%s)." % ("ON" if on else "OFF", where, path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
