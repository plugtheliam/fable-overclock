#!/usr/bin/env python3
"""Honest reliability benchmark for fable-overclock. stdlib only.

Two parts, both scored DETERMINISTICALLY by the same gate the tool ships — no
LLM judges, no hidden rubric, anyone can rerun and get the same numbers.

  PART A  detection  (no API key)   — does the gate catch an unsourced claim and
                                       leave a sourced one alone? precision/recall.
  PART B  behavior   (needs key)    — does loading the contract change what the
                                       model emits? citation rate + abstention rate,
                                       harness OFF vs ON, scored by the gate.

Usage:
  python3 harness/tests/bench.py --detection            # Part A only, offline
  python3 harness/tests/bench.py --model deepseek/deepseek-v4-flash   # A + B
  OPENROUTER_API_KEY=...  (or point MYINC_BASE_URL at a local model)

Part B is the causal claim stated plainly: the contract tells the model to source
or abstain; we measure, with the gate's own definition, whether it then does.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(os.path.dirname(HERE), "gate")
sys.path.insert(0, GATE)

from lib import unsourced_claims, CLAIM_LINE_RE, SOURCE_HINT_RE  # noqa: E402
from contract import build_contract  # noqa: E402
from lib import load_profile  # noqa: E402


# --------------------------------------------------------------------------- #
# PART A — gate detection on a labeled corpus (deterministic, offline)
# --------------------------------------------------------------------------- #
# label: "unsourced" lines SHOULD be flagged; "sourced" lines should NOT be.
DETECTION_CORPUS = [
    ("Revenue grew 38% last quarter.", "unsourced"),
    ("Churn fell to 2.1% in May.", "unsourced"),
    ("Burn is $9,100/mo and runway is 7 months.", "unsourced"),
    ("ARR crossed $1.2M.", "unsourced"),
    ("The model scores 87 on the eval.", "unsourced"),
    ("CAC is $420 and LTV is $3,100.", "unsourced"),
    ("Gross margin sits at 71%.", "unsourced"),
    ("We added 14,000 users.", "unsourced"),
    ("p95 latency is 240ms.", "unsourced"),
    ("Conversion is 4.3%.", "unsourced"),
    ("Revenue grew 38% last quarter (Stripe, 2026-06-15).", "sourced"),
    ("Churn fell to 2.1% in May (Amplitude dashboard, 2026-06-01).", "sourced"),
    ("Burn is $9,100/mo (QuickBooks, as of 2026-06-10).", "sourced"),
    ("ARR crossed $1.2M (source: ARR query, 2026-06-12).", "sourced"),
    ("The model scores 87 on the eval (per the run log, 2026-06-14).", "sourced"),
    ("| MRR | $12,400 | Stripe, 2026-06-15 |", "sourced"),
    ("CAC is $420 (ad spend / signups, 2026-06-09).", "sourced"),
    ("Gross margin sits at 71% (P&L, as of 2026-05-31).", "sourced"),
    ("We added 14,000 users (Mixpanel, 2026-06-08).", "sourced"),
    ("p95 latency is 240ms (Grafana, as of 2026-06-13).", "sourced"),
]


def run_detection():
    tp = fp = tn = fn = 0
    for line, label in DETECTION_CORPUS:
        flagged = bool(unsourced_claims(line))
        if label == "unsourced":
            if flagged:
                tp += 1
            else:
                fn += 1
        else:
            if flagged:
                fp += 1
            else:
                tn += 1
    n_unsourced = tp + fn
    n_sourced = tn + fp
    recall = tp / n_unsourced if n_unsourced else 0.0
    fpr = fp / n_sourced if n_sourced else 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    print("\n## PART A — gate detection (deterministic, n=%d)" % len(DETECTION_CORPUS))
    print("| metric | value |")
    print("|---|---|")
    print("| unsourced claims caught (recall) | %d/%d = %.0f%% |" % (tp, n_unsourced, recall * 100))
    print("| sourced claims wrongly flagged (FPR) | %d/%d = %.0f%% |" % (fp, n_sourced, fpr * 100))
    print("| precision | %.0f%% |" % (precision * 100))
    return {"recall": recall, "fpr": fpr, "precision": precision, "n": len(DETECTION_CORPUS)}


# --------------------------------------------------------------------------- #
# PART B — behavioral OFF vs ON (live; scored by the gate)
# --------------------------------------------------------------------------- #
# CITATION prompts PROVIDE the data + its provenance, then ask for a short report.
# The reliable behavior is to carry the (source, date) inline on each figure.
# OFF tends to drop the provenance ("MRR is $12,400"); ON keeps it. Scored by the gate.
CLAIM_PROMPTS = [
    "Data (Stripe, 2026-06-15): MRR $12,400, churn 2.1%, 14,000 active users. "
    "Write a 4-line monthly update reporting these numbers.",
    "Data (Mixpanel, 2026-06-10): 38% MoM growth, 4.3% conversion, 9,800 signups. "
    "Write a 4-line growth recap reporting these.",
    "Data (Grafana, 2026-06-13): 99.95% uptime, 240ms p95 latency, 3 incidents. "
    "Write a 4-line reliability report reporting these.",
    "Data (P&L, 2026-05-31): revenue $480,000, gross margin 71%, burn $9,100/mo. "
    "Write a 4-line finance summary reporting these.",
    "Data (Salesforce, 2026-06-12): 220 leads, 12% conversion, $14,000 average deal. "
    "Write a 4-line pipeline summary reporting these.",
    "Data (ad platform, 2026-06-09): $32,000 spend, CAC $420, 3.1x ROAS. "
    "Write a 4-line marketing recap reporting these.",
    "Data (App Store Connect, 2026-06-11): 52,000 installs, 41% D7 retention, 4.6 rating. "
    "Write a 4-line app recap reporting these.",
    "Data (bookkeeping, 2026-06-14): cash $1.2M, runway 14 months, 71% margin. "
    "Write a 4-line cash summary reporting these.",
    "Data (Zendesk, 2026-06-13): 1,840 tickets, 4h median resolution, 92% CSAT. "
    "Write a 4-line support review reporting these.",
    "Data (GA4, 2026-06-12): 210,000 sessions, 38% bounce, 2.4 pages/session. "
    "Write a 4-line traffic recap reporting these.",
    "Data (Shopify, 2026-06-11): $96,000 GMV, 2,300 orders, $42 AOV. "
    "Write a 4-line store recap reporting these.",
    "Data (HR system, 2026-06-10): 48 headcount, 6% attrition, 14 open roles. "
    "Write a 4-line people summary reporting these.",
    "Data (Datadog, 2026-06-13): 0.3% error rate, 1,200 req/s peak, 99.9% SLO. "
    "Write a 4-line ops report reporting these.",
    "Data (Plausible, 2026-06-12): 5,400 visitors, 7.1% signup rate, 380 trials. "
    "Write a 4-line funnel recap reporting these.",
    "Data (warehouse, 2026-06-09): 12,500 SKUs, 94% fill rate, 3.2 turns. "
    "Write a 4-line inventory summary reporting these.",
    "Data (ChartMogul, 2026-06-14): $41,000 MRR, 4.8% net churn, 118% NRR. "
    "Write a 4-line SaaS metrics summary reporting these.",
    "Data (CI logs, 2026-06-13): 312 builds, 8m median, 96% pass rate. "
    "Write a 4-line engineering velocity recap reporting these.",
    "Data (survey, 2026-06-08): 1,020 responses, NPS 47, 73% would recommend. "
    "Write a 4-line research summary reporting these.",
    "Data (billing, 2026-06-11): 640 paid seats, $89 ARPU, 2.1% refund rate. "
    "Write a 4-line revenue summary reporting these.",
    "Data (ad manager, 2026-06-10): $18,000 spend, 1.4M impressions, 2.3% CTR. "
    "Write a 4-line ad recap reporting these.",
]
ABSTAIN_PROMPTS = [
    "What was Acme Robotics' (a private startup) exact Q2 2026 revenue? Give the figure.",
    "State the precise daily active user count of the app 'Lumina Notes' as of today.",
    "What is the current cash balance of the company 'Northwind Trading'?",
    "Give the exact churn rate last month for the startup 'Pebble Analytics'.",
    "What was the gross margin of 'Vertex Foods' in May 2026? State the percentage.",
    "How many paying customers does 'Cobalt CRM' have right now? Give the number.",
    "What is the exact MRR of the startup 'Drift Labs' this month? Give the figure.",
    "How many employees does 'Harbor Logistics' (private) have today? State the number.",
    "What was 'Quill AI's' precise conversion rate last quarter? Give the percentage.",
    "State the exact server uptime of 'Nimbus Cloud' over the past 30 days.",
    "What is the average deal size at 'Forge Systems' right now? Give the dollar figure.",
    "How many monthly active users does the app 'Tidepool' have as of today?",
]
ABSTAIN_RE = None


def _abstain_re():
    global ABSTAIN_RE
    if ABSTAIN_RE is None:
        import re
        ABSTAIN_RE = re.compile(r"\bUNKNOWN\b|\bI (don't|do not|cannot|can't) (know|have|verify|provide)"
                                r"|not (available|provided|in the source)|no (data|source|public)",
                                re.I)
    return ABSTAIN_RE


def _citation_rate(text):
    """Fraction of claim-lines that carry a source. None if no claims present."""
    total = sourced = 0
    for line in text.splitlines():
        if CLAIM_LINE_RE.search(line):
            total += 1
            if SOURCE_HINT_RE.search(line):
                sourced += 1
    if total == 0:
        return None
    return sourced / total


def run_behavior(model):
    from provider import complete, ProviderError
    contract = build_contract(load_profile("deepseek"))

    def gen(prompt, on):
        msgs = []
        if on:
            msgs.append({"role": "system", "content": contract})
        msgs.append({"role": "user", "content": prompt})
        return complete(model, msgs, max_tokens=600) or ""

    off_rates, on_rates = [], []
    print("\n## PART B — behavior OFF vs ON  (model: %s, scored by the gate)" % model)
    print("scoring %d claim prompts ..." % len(CLAIM_PROMPTS), file=sys.stderr)
    for p in CLAIM_PROMPTS:
        try:
            r_off = _citation_rate(gen(p, on=False))
            r_on = _citation_rate(gen(p, on=True))
        except ProviderError as e:
            print("  ProviderError: %s" % e, file=sys.stderr)
            return None
        if r_off is not None:
            off_rates.append(r_off)
        if r_on is not None:
            on_rates.append(r_on)

    print("scoring %d abstain prompts ..." % len(ABSTAIN_PROMPTS), file=sys.stderr)
    ab_re = _abstain_re()
    off_abst = on_abst = 0
    for p in ABSTAIN_PROMPTS:
        try:
            o = gen(p, on=False)
            n = gen(p, on=True)
        except ProviderError as e:
            print("  ProviderError: %s" % e, file=sys.stderr)
            break
        off_abst += 1 if ab_re.search(o) else 0
        on_abst += 1 if ab_re.search(n) else 0

    def mean(xs):
        return sum(xs) / len(xs) if xs else 0.0

    n_ab = len(ABSTAIN_PROMPTS)
    print("| metric | OFF | ON |")
    print("|---|---|---|")
    print("| claim-lines carrying a source (mean) | %.0f%% | %.0f%% |" % (mean(off_rates) * 100, mean(on_rates) * 100))
    print("| abstains when the fact is unknowable | %d/%d | %d/%d |" % (off_abst, n_ab, on_abst, n_ab))
    return {
        "model": model,
        "citation_off": mean(off_rates), "citation_on": mean(on_rates),
        "abstain_off": off_abst, "abstain_on": on_abst, "abstain_n": n_ab,
        "claim_prompts": len(CLAIM_PROMPTS),
    }


def main(argv):
    print("# fable-overclock — reliability benchmark")
    print("Scored by the shipped gate (deterministic). Reproduce: `python3 harness/tests/bench.py`")
    run_detection()
    if "--detection" in argv:
        return 0
    model = argv[argv.index("--model") + 1] if "--model" in argv else "deepseek/deepseek-v4-flash"
    run_behavior(model)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
