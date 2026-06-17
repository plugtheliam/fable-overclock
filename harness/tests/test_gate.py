#!/usr/bin/env python3
"""Gate tests — stdlib unittest, no deps.  python3 harness/tests/test_gate.py"""
import json
import os
import subprocess
import sys
import unittest

HARNESS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HARNESS, "gate"))
import lib  # noqa: E402

SPEND_NO_VERDICT = "Recommendation: upgrade hosting to annual billing, $400/mo committed."
SPEND_WITH_VERDICT = (
    "Recommendation: upgrade hosting to annual billing, $400/mo.\n"
    "VERDICT: conditional\n"
    "TRIPWIRE: spend-runway\n"
    "GROUNDS: runway 14.2 months (bookkeeping, 2026-06-15)\n"
    "FLIPS IF: runway drops below 12 months next cycle.\n"
)
CLAIM_NO_SOURCE = "MRR is $12,400 this week and burn is $9,100."
CLAIM_WITH_SOURCE = "MRR is $12,400 (Stripe, 2026-06-15) and burn is $9,100 (bank, 2026-06-15)."
ESCALATE_NO_VERDICT = "We should explore an acquisition of the smaller competitor."
NO_CHANGE = "No change recommended. All categories within +/-20% of the 4-week baseline."


class TestEvaluate(unittest.TestCase):
    def ev(self, text, profile):
        return lib.evaluate(text, profile=lib.load_profile(profile))

    def test_spend_without_verdict_blocks(self):
        self.assertEqual(self.ev(SPEND_NO_VERDICT, "sonnet").decision, "deny")

    def test_spend_with_verdict_allows(self):
        self.assertEqual(self.ev(SPEND_WITH_VERDICT, "sonnet").decision, "allow")

    def test_unsourced_claim_blocks_on_sonnet(self):
        self.assertEqual(self.ev(CLAIM_NO_SOURCE, "sonnet").decision, "deny")

    def test_unsourced_claim_warns_on_opus(self):
        r = self.ev(CLAIM_NO_SOURCE, "opus")
        self.assertEqual(r.decision, "allow")
        self.assertTrue(r.warns)

    def test_sourced_claim_allows(self):
        self.assertEqual(self.ev(CLAIM_WITH_SOURCE, "opus").decision, "allow")

    def test_table_source_recognized(self):
        # a date on the line counts as a source (covers table rows), strictest profile
        row = "| MRR | $12,400 | Stripe, 2026-06-15 |\n| Burn | $9,100 | bank, 2026-06-15 |"
        self.assertEqual(self.ev(row, "deepseek").decision, "allow")

    def test_rate_unit_not_spend(self):
        # "$9,100/mo" is a reported rate, not a spend commitment -> no verdict required
        rep = "Burn: $9,100/mo (bank, 2026-06-15). Runway 14.2 months (bookkeeping, 2026-06-15). No change recommended."
        self.assertEqual(self.ev(rep, "deepseek").decision, "allow")

    def test_spend_word_in_prose_not_flagged(self):
        # the WORD "spend" with no $ on its line is commentary, not a proposal
        prose = "Hosting is within the threshold; no further spend planned. No change recommended."
        self.assertEqual(self.ev(prose, "deepseek").decision, "allow")

    def test_real_proposal_needs_verdict(self):
        # action keyword + $ on the same line = a real spend proposal -> verdict required
        prop = "Recommend: approve $5,000 for the new tooling this quarter."
        self.assertEqual(self.ev(prop, "deepseek").decision, "deny")

    def test_escalate_domain_requires_escalate(self):
        self.assertEqual(self.ev(ESCALATE_NO_VERDICT, "opus").decision, "deny")

    def test_clean_report_allows(self):
        self.assertEqual(self.ev(NO_CHANGE, "sonnet").decision, "allow")


class TestHook(unittest.TestCase):
    """End-to-end through spec_gate.py with a real PreToolUse event."""
    def hook(self, event, profile):
        env = dict(os.environ, MYINC_PROFILE=profile)
        p = subprocess.run(
            [sys.executable, os.path.join(HARNESS, "gate", "spec_gate.py")],
            input=json.dumps(event), capture_output=True, text=True, env=env,
        )
        return json.loads(p.stdout)["hookSpecificOutput"]["permissionDecision"]

    def test_deliverable_spend_denied(self):
        ev = {"tool_name": "Write",
              "tool_input": {"file_path": "loops/ops-loop/evidence/2026-06-15-report.md",
                             "content": SPEND_NO_VERDICT}}
        self.assertEqual(self.hook(ev, "sonnet"), "deny")

    def test_non_deliverable_path_allowed(self):
        ev = {"tool_name": "Write",
              "tool_input": {"file_path": "scratch/notes.py", "content": SPEND_NO_VERDICT}}
        self.assertEqual(self.hook(ev, "sonnet"), "allow")

    def test_non_write_tool_allowed(self):
        ev = {"tool_name": "Bash", "tool_input": {"command": "ls"}}
        self.assertEqual(self.hook(ev, "sonnet"), "allow")


class TestScopeAndToggle(unittest.TestCase):
    """Broadened scope (docs, not code) + the on/off controls."""

    def test_doc_path_is_checked(self):
        # a plain markdown doc anywhere is now in scope (not just report/evidence)
        self.assertTrue(lib.is_deliverable_path("notes/meeting.md"))
        self.assertTrue(lib.is_deliverable_path("a/b/journal.txt"))

    def test_code_path_not_checked(self):
        self.assertFalse(lib.is_deliverable_path("src/app.py"))
        self.assertFalse(lib.is_deliverable_path("lib/index.ts"))

    def test_gate_all_env_checks_everything(self):
        old = os.environ.get("MYINC_GATE_ALL")
        os.environ["MYINC_GATE_ALL"] = "1"
        try:
            self.assertTrue(lib.is_deliverable_path("src/app.py"))
        finally:
            os.environ.pop("MYINC_GATE_ALL", None)
            if old is not None:
                os.environ["MYINC_GATE_ALL"] = old

    def test_gate_disabled_by_env(self):
        old = os.environ.get("MYINC_GATE")
        os.environ["MYINC_GATE"] = "off"
        try:
            self.assertFalse(lib.gate_enabled())
        finally:
            os.environ.pop("MYINC_GATE", None)
            if old is not None:
                os.environ["MYINC_GATE"] = old

    def test_toggle_command_writes_state_and_blocks(self):
        import tempfile
        cwd = os.getcwd()
        tmp = tempfile.mkdtemp()
        try:
            os.chdir(tmp)
            env = dict(os.environ)
            env.pop("MYINC_GATE", None)
            p = subprocess.run(
                [sys.executable, os.path.join(HARNESS, "gate", "toggle.py")],
                input=json.dumps({"prompt": "foc off"}), capture_output=True, text=True, env=env,
            )
            out = json.loads(p.stdout)
            self.assertEqual(out["decision"], "block")
            self.assertIn("OFF", out["reason"])
            self.assertFalse(lib.gate_enabled())  # state file now off in this cwd
        finally:
            os.chdir(cwd)

    def test_non_command_prompt_passes_through(self):
        p = subprocess.run(
            [sys.executable, os.path.join(HARNESS, "gate", "toggle.py")],
            input=json.dumps({"prompt": "write the quarterly report"}), capture_output=True, text=True,
        )
        self.assertEqual(p.stdout.strip(), "")  # no interception


if __name__ == "__main__":
    unittest.main(verbosity=2)
