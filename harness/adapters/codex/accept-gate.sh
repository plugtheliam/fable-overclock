#!/usr/bin/env bash
# Codex worktree-accept gate. Run after Codex produces changes; exit 0 accepts,
# exit 1 rejects (a changed deliverable failed the CFO gate). Thin wrapper over
# harness/gate/accept.py so it works in CI, a pre-merge hook, or by hand.
#
#   MYINC_PROFILE=codex bash harness/adapters/codex/accept-gate.sh
#   bash harness/adapters/codex/accept-gate.sh --base origin/master
#   bash harness/adapters/codex/accept-gate.sh path/to/report.md
set -euo pipefail
HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
: "${MYINC_PROFILE:=codex}"
export MYINC_PROFILE
exec python3 "$HARNESS_DIR/gate/accept.py" "$@"
