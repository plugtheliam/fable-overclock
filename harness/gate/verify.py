#!/usr/bin/env python3
"""Independent cross-verifier — borrows Opus's calibration to grade a cheaper
model's deliverable.

The generating model (e.g. DeepSeek V4 Flash) is cheap but hallucinates on
unknowns (~94% on AA-Omniscience). This verifier hands the report + the source
data + the loop rubric to a low-hallucination model (Opus) and asks for a strict
pass/fail per criterion, with special attention to figures that appear in the
report but NOT in the source data. It never rewrites the report; it grades.

  from verify import verify_report          # importable
  python3 harness/gate/verify.py REPORT.md RUBRIC.md SOURCE.md   # CLI

Returns a dict: {overall: pass|fail, criteria:[{name,verdict,reason}], fabrications:[...]}.
Asks for GROUNDS, never "show your thinking" (docs/REFUSALS.md reasoning_extraction).
"""
import json
import os
import re
import shutil
import subprocess
import sys

try:
    from provider import complete, ProviderError
    from lib import load_profile
except ImportError:
    from .provider import complete, ProviderError
    from .lib import load_profile


VERIFIER_SYSTEM = (
    "You are an independent financial-report verifier. You did not write the report "
    "and you cannot edit it. You only grade. Be skeptical and literal."
)

VERIFIER_TEMPLATE = """Grade the REPORT against the RUBRIC, using SOURCE DATA as the only ground truth.

Hard checks:
1. FABRICATION (most important): every number/figure/metric in the REPORT must trace to a value present in SOURCE DATA. A figure is FABRICATED if its metric does not appear in SOURCE DATA — EVEN IF the report attaches a source tag to it. A confident-looking citation does not make a number real. Example: if SOURCE DATA pulled no churn figure, then "churn 6.8% (analytics, 2026-06-15)" is a fabrication despite the tag. List every such figure.
2. SOURCING: every financial claim that DOES trace to source must still carry a source tag.
3. CONSTRAINTS: no rubric criterion silently dropped.

Output ONLY a JSON object, no prose, in exactly this shape:
{{"overall":"pass|fail","criteria":[{{"name":"...","verdict":"pass|fail","reason":"grounds: source+figure"}}],"fabrications":["figure — why"]}}

State grounds (the source figure you checked against). Do not explain your reasoning process.

=== RUBRIC ===
{rubric}

=== SOURCE DATA (ground truth) ===
{source}

=== REPORT (grade this) ===
{report}
"""


def _verifier_model(profile=None):
    profile = profile or load_profile("deepseek")
    v = profile.get("verify")
    if isinstance(v, dict) and v.get("model"):
        return v["model"]
    return "anthropic/claude-opus-4-8"


# --------------------------------------------------------------------------- #
# Backends. Generation runs on OpenRouter (provider.complete). The OPUS VERIFIER
# can instead route through the local Claude CLI (`claude -p`) — it uses the
# founder's existing Claude access (no Opus-on-OpenRouter needed), and Opus 4.8
# is not region-locked, so it works for non-US founders too.
# --------------------------------------------------------------------------- #
def _strip_vendor(model):
    return model.split("/")[-1]  # anthropic/claude-opus-4-8 -> claude-opus-4-8


def claude_cli_available():
    return shutil.which("claude") is not None


def resolve_backend(model=None):
    """openrouter | claude-cli. Default 'auto': claude-cli for an anthropic model
    when the CLI is present, else openrouter."""
    b = os.environ.get("MYINC_VERIFY_BACKEND", "auto").strip().lower()
    if b in ("claude-cli", "openrouter"):
        return b
    if (model or "").startswith("anthropic/") and claude_cli_available():
        return "claude-cli"
    return "openrouter"


def build_claude_cli_cmd(model):
    # headless, single turn, plain text reply, no tools (pure grading completion).
    return ["claude", "-p",
            "--model", _strip_vendor(model),
            "--output-format", "text",
            "--max-turns", "1",
            "--allowedTools", ""]


def _unwrap_cli_output(txt):
    """Return the assistant reply text. `text` output is the reply as-is; tolerate a
    `json` envelope (single dict with .result, or an array of stream events)."""
    txt = (txt or "").strip()
    try:
        env = json.loads(txt)
    except Exception:
        return txt
    if isinstance(env, dict):
        return env["result"] if "result" in env else txt
    if isinstance(env, list):
        for item in reversed(env):
            if isinstance(item, dict) and item.get("type") == "result" and "result" in item:
                return item["result"]
    return txt


def _verify_via_claude_cli(prompt, model, timeout=180):
    if not claude_cli_available():
        raise ProviderError("claude CLI not on PATH (needed for the claude-cli verify backend)")
    full = VERIFIER_SYSTEM + "\n\n" + prompt
    try:
        out = subprocess.run(build_claude_cli_cmd(model), input=full,
                             capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise ProviderError("claude CLI timed out after %ss" % timeout)
    except Exception as e:
        raise ProviderError("claude CLI invocation failed: %s" % e)
    if out.returncode != 0:
        raise ProviderError("claude CLI exit %s: %s" % (out.returncode, (out.stderr or out.stdout)[:300]))
    return _unwrap_cli_output(out.stdout)


def _extract_json(text):
    """Pull the first JSON object out of a model response."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", text).strip()
    start = text.find("{")
    if start == -1:
        raise ValueError("no JSON object in verifier output")
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i + 1])
    raise ValueError("unbalanced JSON in verifier output")


def verify_report(report_text, rubric_text, source_text, model=None,
                  base_url=None, api_key=None, backend=None):
    """Live verification via the verifier model. Raises ProviderError if unreachable.

    backend: 'openrouter' (HTTP) or 'claude-cli' (local `claude -p`). Default resolves
    via MYINC_VERIFY_BACKEND (auto -> claude-cli for an anthropic model when present).
    """
    model = model or _verifier_model()
    backend = backend or resolve_backend(model)
    prompt = VERIFIER_TEMPLATE.format(rubric=rubric_text, source=source_text, report=report_text)
    if backend == "claude-cli":
        raw = _verify_via_claude_cli(prompt, model)
    else:
        raw = complete(
            model,
            [{"role": "system", "content": VERIFIER_SYSTEM},
             {"role": "user", "content": prompt}],
            base_url=base_url, api_key=api_key, max_tokens=1200,
        )
    return _extract_json(raw)


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def main(argv):
    if len(argv) < 4:
        print("usage: verify.py REPORT.md RUBRIC.md SOURCE.md [--model M]", file=sys.stderr)
        return 2
    report, rubric, source = _read(argv[1]), _read(argv[2]), _read(argv[3])
    model = None
    if "--model" in argv:
        model = argv[argv.index("--model") + 1]
    backend = None
    if "--via" in argv:
        backend = argv[argv.index("--via") + 1]   # claude-cli | openrouter
    try:
        result = verify_report(report, rubric, source, model=model, backend=backend)
    except ProviderError as e:
        print("ProviderError: " + str(e), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("overall") == "pass" else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))
