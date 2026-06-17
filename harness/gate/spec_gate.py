#!/usr/bin/env python3
"""PreToolUse hook entry — the deterministic CFO gate.

Wired by adapters/claude-code/settings.snippet.json on Write|Edit|MultiEdit.
Reads a Claude Code PreToolUse event on stdin, decides allow/deny, and emits the
hookSpecificOutput JSON contract. Fail-open on anything it doesn't understand so
it can never brick the agent on unrelated tools.

Manual test:
  echo '{"tool_name":"Write","tool_input":{"file_path":"company/loops/ops-loop/evidence/x.md","content":"Upgrade hosting to annual billing, $400/mo."}}' \
    | MYINC_PROFILE=sonnet python3 harness/gate/spec_gate.py
"""
import json
import sys

try:
    from lib import (  # when run as a file inside gate/
        read_hook_event, extract_target, is_deliverable_path, evaluate, load_profile,
        gate_enabled,
    )
except ImportError:  # when imported as a package
    from .lib import (
        read_hook_event, extract_target, is_deliverable_path, evaluate, load_profile,
        gate_enabled,
    )


def _emit(decision, reason):
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,            # "allow" | "deny"
            "permissionDecisionReason": reason or "",
        }
    }
    print(json.dumps(out))


def main():
    event = read_hook_event(sys.stdin.read())
    tool, path, text = extract_target(event)

    if tool not in ("Write", "Edit", "MultiEdit"):
        _emit("allow", "")
        return 0
    if not gate_enabled():            # `foc off` / MYINC_GATE=off
        _emit("allow", "")
        return 0
    if not is_deliverable_path(path):
        _emit("allow", "")
        return 0
    if not text.strip():
        _emit("allow", "")
        return 0

    profile = load_profile()
    result = evaluate(text, profile=profile)

    if result.decision == "deny":
        reason = result.reason()
        _emit("deny", reason)
        # Also surface to stderr for older CC versions that read exit-2 + stderr.
        sys.stderr.write(reason + "\n")
        return 2

    # allow, but pass warnings through to the user via stderr (non-blocking).
    if result.warns:
        sys.stderr.write(result.reason() + "\n")
    _emit("allow", "; ".join(result.warns))
    return 0


if __name__ == "__main__":
    sys.exit(main())
