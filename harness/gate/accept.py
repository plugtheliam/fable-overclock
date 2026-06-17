#!/usr/bin/env python3
"""Worktree-accept gate — the Codex enforcement surface.

Codex has no PreToolUse hook. Instead, after Codex produces changes in a
worktree, run this gate over the CHANGED deliverable files and accept only if
they pass. This is the why-was-fable-banned Codex path, applied to business
deliverables instead of code edits.

  python3 harness/gate/accept.py                      # gate git-changed deliverables in cwd
  python3 harness/gate/accept.py --base origin/master # diff against a base ref
  python3 harness/gate/accept.py FILE [FILE ...]      # gate explicit files (no git)

Exit 0 = accept (allow merge). Exit 1 = reject. Profile from MYINC_PROFILE
(default codex via env, or pass --profile).
"""
import os
import subprocess
import sys

try:
    from lib import evaluate, load_profile, is_deliverable_path, resolve_profile_name
except ImportError:
    from .lib import evaluate, load_profile, is_deliverable_path, resolve_profile_name


def _git(args):
    try:
        out = subprocess.run(["git"] + args, capture_output=True, text=True)
        return out.stdout.splitlines() if out.returncode == 0 else []
    except Exception:
        return []


def discover_changed(base=None):
    files = set()
    if base:
        files.update(_git(["diff", "--name-only", "%s...HEAD" % base]))
    files.update(_git(["diff", "--name-only"]))          # unstaged
    files.update(_git(["diff", "--name-only", "--cached"]))  # staged
    files.update(_git(["ls-files", "--others", "--exclude-standard"]))  # untracked
    return [f for f in files if f]


def gate_paths(paths, profile_name=None):
    """Return (ok: bool, lines: list[str]) gating each deliverable file path."""
    profile = load_profile(profile_name) if profile_name else load_profile()
    lines, ok = [], True
    checked = 0
    for path in paths:
        if not is_deliverable_path(path):
            continue
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        result = evaluate(text, profile=profile)
        checked += 1
        if result.decision == "deny":
            ok = False
            lines.append("REJECT  %s" % path)
            lines.append(result.reason())
        elif result.warns:
            lines.append("accept (warn)  %s" % path)
            lines.append(result.reason())
        else:
            lines.append("accept  %s" % path)
    if checked == 0:
        lines.append("no deliverable files changed — nothing to gate.")
    return ok, lines


def main(argv):
    profile_name = None
    base = None
    explicit = []
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--profile":
            profile_name = argv[i + 1]; i += 2
        elif a == "--base":
            base = argv[i + 1]; i += 2
        else:
            explicit.append(a); i += 1

    paths = explicit if explicit else discover_changed(base)
    ok, lines = gate_paths(paths, profile_name)
    name = profile_name or resolve_profile_name()
    print("== worktree-accept gate [profile=%s] ==" % name)
    print("\n".join(lines))
    print("\nRESULT: " + ("ACCEPT" if ok else "REJECT"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
