"""myinc-os harness — core gate logic (stdlib only, py3.8+).

The gate ENFORCES, deterministically, the general reliability rules (gate/rules/
reliability.json) plus any layered domain pack (e.g. gate/rules/cfo.json, see
examples/cfo-pack/). Philosophy: these are TRIPWIRES, not verdicts. The gate flags an
unsourced/fabricated claim; the agent's reasoning writes the fix. A domain pack can
require an extra artifact (e.g. a CFO VERDICT block on a spend) — the gate only checks
that the required artifact (source / verdict / escalate) is present.

Per-model behavior comes from the active profile's `strictness` dial:
  lenient  (opus)      — ambiguous unsourced claims warn, hard rules still block
  strict   (sonnet)    — ambiguous unsourced claims block
  strictest(deepseek)  — same as strict + future abstention hooks (phase 2)
Hard rules (spend-without-verdict, escalate-domain-without-escalate) block on
every profile.
"""
import json
import os
import re

# --------------------------------------------------------------------------- #
# Detection patterns (heuristic tripwires — intentionally conservative).
# --------------------------------------------------------------------------- #
MONEY_AMOUNT_RE = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?|\b\d[\d,]*\s?(?:USD|dollars)\b", re.I)
# Spend is judged by ACTION/commitment keywords, never by a bare $ figure — stating
# "MRR is $12,400" is a metric claim, not a spend. Keyword presence => verdict required.
# Action/commitment keywords only. NOT rate units like "$9,100/mo" or "per month" —
# those are how metrics are reported, not a spend (they caused false verdict trips).
SPEND_KW_RE = re.compile(
    r"\b(spend\w*|buy\w*|purchas\w*|approv\w*|subscri\w*|renew\w*|commit\w*|upgrad\w*|"
    r"annual billing|vendor contract|seat license|monthly plan|pay for|paying for)\b",
    re.I,
)
ESCALATE_DOMAIN_RE = re.compile(
    r"\b(M&A|merger|acquisition|equity dilution|cap table|stock option grant|"
    r"tax strategy|tax structuring)\b",
    re.I,
)
VERDICT_RE = re.compile(r"^\s*VERDICT:\s*(refuse|conditional|escalate)\b", re.I | re.M)
FLIPS_RE = re.compile(r"^\s*FLIPS IF:\s*\S", re.I | re.M)

# A line is a "factual quantified claim" worth sourcing if it states a specific
# number presented as fact: a $ figure, a named metric + number, a percentage, a
# count ("14,000 users"), a technical unit ("240ms"), or a score ("scores 87").
# General by design — reliability is not finance-only. A tolerance/hedge band
# ("within +/-20%") is NOT a claim; HEDGE_RE below suppresses it.
CLAIM_LINE_RE = re.compile(
    r"\$\s?\d[\d,]*"                                                       # money
    r"|\b(?:MRR|ARR|burn|runway|CAC|LTV|NRR|churn|gross margin|margin|"    # metric + number
    r"revenue|cash flow|cash|conversion|retention|uptime|ROAS|ROI)\b[^.\n]*?\d"
    r"|\d[\d,.]*\s?%"                                                      # a percentage
    r"|\b\d[\d,]*\s?(?:users?|customers?|subscribers?|installs?|signups?|" # count nouns
    r"downloads?|requests?|sessions?|members?|visitors?|leads?|deals?)\b"
    r"|\b\d[\d,.]*\s?(?:ms|µs|ns|kb|mb|gb|tb|fps|rps|qps)\b"               # technical units
    r"|\b(?:scores?|scored|rated|ranks?|ranked)\s+\d",                    # score / rating
    re.I,
)
# A tolerance/hedge band is not a factual point-claim (keeps precision high).
HEDGE_RE = re.compile(r"\+/-|±|within\s+[+\-]?\s?\d", re.I)
# A claim is "sourced" if the line carries a source signal: a parenthetical cue, an
# "as of"/"source"/"per" cue, OR a bare ISO date anywhere on the line (covers table
# rows like `| MRR | $12,400 | Stripe, 2026-06-15 |`). Structural only — whether the
# cited number is REAL is the semantic verifier's job (gate/verify.py), not this regex.
SOURCE_HINT_RE = re.compile(
    r"\((?=[^)]*(?:source|as of|per\b|query|\d{4}-\d{2}-\d{2}))[^)]*\)|"
    r"\bas of\b|\bsource\b|\bper\s+\w|"
    r"\d{4}-\d{2}-\d{2}",
    re.I,
)
# Lines that are part of the verdict scaffold are never themselves "claims".
SCAFFOLD_LINE_RE = re.compile(r"^\s*(VERDICT|TRIPWIRE|GROUNDS|FLIPS IF):", re.I)

DEFAULT_DELIVERABLE_RE = re.compile(
    r"(evidence/|/reports?/|founder|verdict|/loops/[^/]+/(evidence|out)/)", re.I
)
# Broadened default scope: any prose / document file, anywhere — these are where
# unsourced claims actually ship. Code files are deliberately excluded (numbers in
# code are not factual claims). MYINC_GATE_ALL=1 checks every write regardless.
DOC_EXT_RE = re.compile(r"\.(md|markdown|mdx|txt|text|rst)$", re.I)


def _truthy(v):
    return str(v or "").strip().lower() in ("1", "true", "yes", "on", "enable", "enabled")


def _falsy(v):
    return str(v or "").strip().lower() in ("0", "false", "no", "off", "disable", "disabled")


# --------------------------------------------------------------------------- #
# Loaders
# --------------------------------------------------------------------------- #
def harness_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resolve_profile_name():
    """Env first (MYINC_PROFILE), then model env mapping, then cost-default sonnet."""
    name = os.environ.get("MYINC_PROFILE", "").strip().lower()
    if name:
        return name
    model = os.environ.get("MYINC_MODEL", os.environ.get("ANTHROPIC_MODEL", "")).lower()
    if "opus" in model:
        return "opus"
    if "sonnet" in model:
        return "sonnet"
    if "deepseek" in model:
        return "deepseek"
    if "gpt" in model or "codex" in model:
        return "codex"
    return "sonnet"  # cost default


def load_profile(name=None):
    name = name or resolve_profile_name()
    path = os.path.join(harness_root(), "profiles", name + ".json")
    if not os.path.exists(path):
        # Unknown profile -> safe strict fallback, never crash the agent.
        return {"name": name, "strictness": "strict", "_fallback": True}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_rules():
    path = os.path.join(harness_root(), "gate", "rules", "cfo.json")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #
def has_spend_signal(text):
    """A real spend PROPOSAL = an action/commitment keyword AND a money amount on the
    SAME line. This is line-scoped on purpose:
      - prose that merely mentions the word ("no spend needed", "commits no spend",
        "breaks SPEND => VERDICT") has the keyword but no $ on that line -> not a spend
      - a reported metric ("Burn $9,100/mo") has a $ but no action keyword -> not a spend
    Verbose models (Opus) were false-tripping the verdict rule on commentary; this fixes
    it without weakening detection of an actual proposal like
    'upgrade to annual billing, commit $3,720/year'.
    """
    for line in text.splitlines():
        if SPEND_KW_RE.search(line) and MONEY_AMOUNT_RE.search(line):
            return True
    return False


def valid_verdict(text):
    """Return (ok, verdict_word_or_None). Requires VERDICT + FLIPS IF both."""
    m = VERDICT_RE.search(text)
    if not m or not FLIPS_RE.search(text):
        return (False, None)
    return (True, m.group(1).lower())


def escalate_domains(text):
    return sorted({m.group(0) for m in ESCALATE_DOMAIN_RE.finditer(text)})


def unsourced_claims(text):
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if SCAFFOLD_LINE_RE.match(line):
            continue
        if SPEND_KW_RE.search(line):
            continue  # a spend proposal — governed by the verdict rule, not source
        if HEDGE_RE.search(line):
            continue  # a tolerance band ("within +/-20%") is not a point-claim
        if CLAIM_LINE_RE.search(line) and not SOURCE_HINT_RE.search(line):
            out.append((i, line.strip()))
    return out


def is_deliverable_path(path):
    if not path:
        return False
    if _truthy(os.environ.get("MYINC_GATE_ALL")):
        return True  # aggressive opt-in: check every write
    override = os.environ.get("MYINC_GATE_PATHS")
    if override:
        return bool(re.search(override, path, re.I))
    if DEFAULT_DELIVERABLE_RE.search(path):
        return True
    # default: any prose/document file (markdown, text, rst), not code
    return bool(DOC_EXT_RE.search(os.path.basename(path).lower()))


# --------------------------------------------------------------------------- #
# Enable / disable — env override, else a state file (project > machine).
# --------------------------------------------------------------------------- #
def gate_state_path(scope="project"):
    home = os.path.expanduser("~")
    if scope == "machine":
        return os.path.join(home, ".myinc", "gate")
    return os.path.join(os.getcwd(), ".myinc", "gate")


def _read_state(scope):
    p = gate_state_path(scope)
    try:
        if os.path.exists(p):
            return open(p, encoding="utf-8").read().strip().lower()
    except Exception:
        pass
    return None


def gate_enabled():
    """True unless explicitly turned off. MYINC_GATE env wins; else project state
    file, else machine state file; default on."""
    env = os.environ.get("MYINC_GATE", "").strip().lower()
    if _falsy(env):
        return False
    if _truthy(env):
        return True
    for scope in ("project", "machine"):  # most-specific wins
        val = _read_state(scope)
        if val in ("off", "0", "false", "no"):
            return False
        if val in ("on", "1", "true", "yes"):
            return True
    return True


def set_gate_state(on, scope="project"):
    p = gate_state_path(scope)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write("on" if on else "off")
    return p


# --------------------------------------------------------------------------- #
# Evaluation
# --------------------------------------------------------------------------- #
class Result:
    def __init__(self, decision, blocks, warns, profile_name):
        self.decision = decision          # "allow" | "deny"
        self.blocks = blocks              # list[str]
        self.warns = warns                # list[str]
        self.profile_name = profile_name

    def reason(self):
        parts = []
        if self.blocks:
            parts.append("BLOCKED by the fable-overclock gate [profile=%s]:" % self.profile_name)
            parts += ["  - " + b for b in self.blocks]
            parts.append("Fix: add the missing source (or, with a domain pack, the verdict), then retry.")
        if self.warns:
            parts.append("reliability gate warnings [profile=%s]:" % self.profile_name)
            parts += ["  ! " + w for w in self.warns]
        return "\n".join(parts)


def evaluate(text, profile=None, rules=None):
    profile = profile or load_profile()
    rules = rules or load_rules()
    strictness = (profile.get("gate") or {}).get("strictness") or profile.get("strictness") or "strict"
    blocks, warns = [], []

    # Hard rule 1: escalate-only domains require an explicit `VERDICT: escalate`.
    esc = escalate_domains(text)
    ok, verdict = valid_verdict(text)
    if esc:
        if not (ok and verdict == "escalate"):
            blocks.append(
                "Mentions escalate-only domain %s without `VERDICT: escalate`. "
                "Licensed-professional territory — no reasoning override." % esc
            )

    # Hard rule 2: spend/commitment requires a valid reasoned verdict block.
    if has_spend_signal(text) and not ok:
        blocks.append(
            "Spend/financial commitment present but no valid CFO verdict "
            "(need `VERDICT: refuse|conditional|escalate` + `FLIPS IF:`). "
            "ops-loop stage 5 gate."
        )

    # Graded rule 3: quantified factual claims must cite a source.
    missing = unsourced_claims(text)
    if missing:
        lines = ", ".join(str(n) for n, _ in missing[:6])
        msg = "%d claim(s) with no source (need an inline `(source, date)` / `as of …`): line(s) %s" % (
            len(missing), lines,
        )
        if strictness in ("strict", "strictest"):
            blocks.append(msg)
        else:
            warns.append(msg + " [lenient profile -> warning, not block]")

    decision = "deny" if blocks else "allow"
    return Result(decision, blocks, warns, profile.get("name", strictness))


# --------------------------------------------------------------------------- #
# Hook IO (Claude Code PreToolUse contract)
# --------------------------------------------------------------------------- #
def read_hook_event(stdin_text):
    try:
        return json.loads(stdin_text)
    except Exception:
        return {}


def extract_target(event):
    """Return (tool_name, file_path, text) from a PreToolUse event."""
    tool = event.get("tool_name", "")
    ti = event.get("tool_input", {}) or {}
    path = ti.get("file_path") or ti.get("path") or ""
    text = ti.get("content")
    if text is None:
        text = ti.get("new_string")
    if text is None and isinstance(ti.get("edits"), list):
        text = "\n".join(
            (e.get("new_string") or "") for e in ti["edits"] if isinstance(e, dict)
        )
    return tool, path, (text or "")
