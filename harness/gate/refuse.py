#!/usr/bin/env python3
"""Standalone CFO tripwire checker — usable outside the hook.

Reads text from a file arg or stdin, prints which tripwires fired and whether a
verdict / source / escalate is still required. Exit 0 = clean, 1 = needs action.

  python3 harness/gate/refuse.py company/loops/ops-loop/evidence/2026-06-15-report.md
  cat report.md | MYINC_PROFILE=opus python3 harness/gate/refuse.py
"""
import sys

try:
    from lib import evaluate, load_profile
except ImportError:
    from .lib import evaluate, load_profile


def main(argv):
    if len(argv) > 1 and argv[1] not in ("-", "--stdin"):
        with open(argv[1], encoding="utf-8") as fh:
            text = fh.read()
    else:
        text = sys.stdin.read()

    result = evaluate(text, profile=load_profile())
    if result.decision == "deny":
        print(result.reason())
        return 1
    if result.warns:
        print(result.reason())
        return 0
    print("fable-overclock gate: clean [profile=%s]. Every claim is sourced." % result.profile_name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
