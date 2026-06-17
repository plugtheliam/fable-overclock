#!/usr/bin/env python3
"""Print the active harness profile — used by the skill and for debugging.

  python3 harness/gate/profile.py            # active (env-resolved)
  MYINC_PROFILE=opus python3 harness/gate/profile.py
"""
import json
import sys

try:
    from lib import load_profile, resolve_profile_name
except ImportError:
    from .lib import load_profile, resolve_profile_name


def main():
    name = resolve_profile_name()
    print(json.dumps(load_profile(name), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
