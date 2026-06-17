#!/usr/bin/env bash
# myinc-os harness installer. Two adapters; idempotent; no machine-wide changes
# by default.
#
#   harness/install.sh                 # Claude Code: PreToolUse hook + skill (./.claude)
#   harness/install.sh --global        # Claude Code into ~/.claude
#   harness/install.sh --codex         # Codex: managed block in ./AGENTS.md + accept-gate
#   harness/install.sh --uninstall     # remove what the chosen adapter added
#
# Codex AGENTS.md target defaults to the repo root; override with MYINC_TARGET_REPO.
set -euo pipefail

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$HARNESS_DIR/.." && pwd)"

SCOPE="project"
ACTION="install"
ADAPTER="claude"
for arg in "$@"; do
  case "$arg" in
    --global) SCOPE="global" ;;
    --codex) ADAPTER="codex" ;;
    --claude|--claude-code) ADAPTER="claude" ;;
    --uninstall) ACTION="uninstall" ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

command -v python3 >/dev/null 2>&1 || { echo "python3 required" >&2; exit 1; }

# =========================================================================== #
# Codex adapter — managed block in AGENTS.md + executable accept-gate
# =========================================================================== #
if [ "$ADAPTER" = "codex" ]; then
  TARGET_REPO="${MYINC_TARGET_REPO:-$REPO_DIR}"
  AGENTS="$TARGET_REPO/AGENTS.md"
  chmod +x "$HARNESS_DIR/adapters/codex/accept-gate.sh" 2>/dev/null || true

  python3 - "$ACTION" "$AGENTS" "$HARNESS_DIR/adapters/codex/AGENTS.snippet.md" <<'PY'
import os, sys
action, agents_path, snippet_path = sys.argv[1], sys.argv[2], sys.argv[3]
START, END = "<!-- myinc-harness:start -->", "<!-- myinc-harness:end -->"

cur = ""
if os.path.exists(agents_path):
    with open(agents_path, encoding="utf-8") as fh:
        cur = fh.read()

# strip any existing managed block
if START in cur and END in cur:
    pre = cur.split(START)[0].rstrip()
    post = cur.split(END, 1)[1].lstrip()
    cur = (pre + ("\n\n" if pre and post else "") + post).strip()

if action == "install":
    with open(snippet_path, encoding="utf-8") as fh:
        block = fh.read().strip()
    managed = START + "\n" + block + "\n" + END
    cur = (cur.strip() + "\n\n" + managed + "\n") if cur.strip() else (managed + "\n")
    os.makedirs(os.path.dirname(agents_path) or ".", exist_ok=True)
    with open(agents_path, "w", encoding="utf-8") as fh:
        fh.write(cur)
    print("wrote myinc-harness block -> " + agents_path)
else:
    if cur.strip():
        with open(agents_path, "w", encoding="utf-8") as fh:
            fh.write(cur.strip() + "\n")
    elif os.path.exists(agents_path):
        os.remove(agents_path)
    print("removed myinc-harness block <- " + agents_path)
PY

  if [ "$ACTION" = "uninstall" ]; then echo "done. uninstalled (codex)."; exit 0; fi
  cat <<EOF

done. installed (codex).

next:
  1. export MYINC_PROFILE=codex
  2. after Codex produces changes, gate the worktree before accepting:
       MYINC_PROFILE=codex bash "$HARNESS_DIR/adapters/codex/accept-gate.sh"
     -> exit 0 accepts, exit 1 rejects (a deliverable skipped a verdict/source).
  3. wire it as your worktree-accept / pre-merge check.

profiles: $HARNESS_DIR/profiles/  (codex = GPT-5.5; verify by opus)
EOF
  exit 0
fi

# =========================================================================== #
# Claude Code adapter — PreToolUse hook + skill link
# =========================================================================== #
if [ "$SCOPE" = "global" ]; then CLAUDE_DIR="$HOME/.claude"; else CLAUDE_DIR="$REPO_DIR/.claude"; fi
SETTINGS="$CLAUDE_DIR/settings.json"
SKILLS_DIR="$CLAUDE_DIR/skills"
mkdir -p "$CLAUDE_DIR" "$SKILLS_DIR"

python3 - "$ACTION" "$SETTINGS" "$HARNESS_DIR/adapters/claude-code/settings.snippet.json" "$SCOPE" "$HARNESS_DIR" <<'PY'
import copy, json, os, sys
action, settings_path, snippet_path, scope, harness_dir = sys.argv[1:6]

def load(p):
    if os.path.exists(p):
        with open(p, encoding="utf-8") as fh:
            try: return json.load(fh)
            except Exception: return {}
    return {}

settings = load(settings_path)
snippet = load(snippet_path)

# Merge every event type in the snippet (PreToolUse gate + UserPromptSubmit toggle).
# A project install uses $CLAUDE_PROJECT_DIR (portable, commit-friendly). A GLOBAL
# install fires in every project's cwd — where $CLAUDE_PROJECT_DIR won't point at this
# harness — so pin the command to this checkout's absolute path. The gate fails open
# and only acts on prose deliverables, so it's a no-op for ordinary coding elsewhere.
our_entries, our_cmds = {}, set()
for event, entries in (snippet.get("hooks") or {}).items():
    out = []
    for entry in entries:
        e = copy.deepcopy(entry)
        for h in e.get("hooks", []):
            c = h.get("command", "")
            if scope == "global" and "$CLAUDE_PROJECT_DIR/harness" in c:
                c = c.replace("$CLAUDE_PROJECT_DIR/harness", harness_dir)
                h["command"] = c
            our_cmds.add(h.get("command"))
        out.append(e)
    our_entries[event] = out

hooks = settings.setdefault("hooks", {})
for event, entries in our_entries.items():
    bucket = hooks.setdefault(event, [])
    bucket[:] = [x for x in bucket
                 if not any(hh.get("command") in our_cmds for hh in x.get("hooks", []))]
    if action == "install":
        bucket.extend(entries)
    if not bucket:
        hooks.pop(event, None)
if not hooks:
    settings.pop("hooks", None)

os.makedirs(os.path.dirname(settings_path), exist_ok=True)
with open(settings_path, "w", encoding="utf-8") as fh:
    json.dump(settings, fh, indent=2)
    fh.write("\n")
print(("removed" if action == "uninstall" else "wired") + " %d hook(s) -> %s" % (len(our_cmds), settings_path))
PY

SKILL_LINK="$SKILLS_DIR/myinc-harness"
if [ "$ACTION" = "uninstall" ]; then
  [ -L "$SKILL_LINK" ] && rm "$SKILL_LINK" && echo "removed skill link $SKILL_LINK" || true
  echo "done. uninstalled (claude/$SCOPE)."; exit 0
else
  rm -rf "$SKILL_LINK"
  ln -s "$HARNESS_DIR/skill/myinc-harness" "$SKILL_LINK"
  echo "linked skill -> $SKILL_LINK"
fi

cat <<EOF

done. installed (claude/$SCOPE).

next:
  1. export MYINC_PROFILE=sonnet     # cost default (or: opus)
  2. self-test the gate (human form — takes raw text):
       printf 'Upgrade hosting to annual billing, \$400/mo.\n' \\
         | MYINC_PROFILE=sonnet python3 "$HARNESS_DIR/gate/refuse.py"
     -> should BLOCK (spend, no verdict). The PreToolUse hook (spec_gate.py)
        takes a Claude Code event JSON on stdin, not raw text.
  3. run a loop as usual (e.g. loops/ops-loop). The gate blocks any deliverable
     that skips the CFO verdict / source rules.

profiles: $HARNESS_DIR/profiles/  (sonnet, opus, deepseek, codex)
EOF
