#!/usr/bin/env python3
"""Tests for the Claude-CLI verify backend. No real `claude` invocation.
python3 harness/tests/test_verify_cli.py"""
import os
import sys
import unittest

HARNESS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HARNESS, "gate"))
import verify    # noqa: E402
from provider import ProviderError  # noqa: E402

OPUS = "anthropic/claude-opus-4-8"


class TestModelMapping(unittest.TestCase):
    def test_strip_vendor(self):
        self.assertEqual(verify._strip_vendor(OPUS), "claude-opus-4-8")
        self.assertEqual(verify._strip_vendor("claude-opus-4-8"), "claude-opus-4-8")

    def test_cmd_shape(self):
        cmd = verify.build_claude_cli_cmd(OPUS)
        self.assertEqual(cmd[:2], ["claude", "-p"])
        self.assertIn("--model", cmd)
        self.assertEqual(cmd[cmd.index("--model") + 1], "claude-opus-4-8")
        self.assertIn("--output-format", cmd)
        self.assertEqual(cmd[cmd.index("--output-format") + 1], "text")

    def test_unwrap_envelopes(self):
        import json as _j
        arr = _j.dumps([{"type": "system"},
                        {"type": "result", "result": '{"overall":"fail"}'}])
        self.assertEqual(verify._unwrap_cli_output(arr), '{"overall":"fail"}')
        self.assertEqual(verify._unwrap_cli_output('{"result":"hi"}'), "hi")
        self.assertEqual(verify._unwrap_cli_output('{"overall":"pass"}'), '{"overall":"pass"}')


class TestBackendResolution(unittest.TestCase):
    def setUp(self):
        self._env = os.environ.get("MYINC_VERIFY_BACKEND")
        self._avail = verify.claude_cli_available

    def tearDown(self):
        verify.claude_cli_available = self._avail
        if self._env is None:
            os.environ.pop("MYINC_VERIFY_BACKEND", None)
        else:
            os.environ["MYINC_VERIFY_BACKEND"] = self._env

    def test_explicit_claude_cli(self):
        os.environ["MYINC_VERIFY_BACKEND"] = "claude-cli"
        self.assertEqual(verify.resolve_backend(OPUS), "claude-cli")

    def test_explicit_openrouter(self):
        os.environ["MYINC_VERIFY_BACKEND"] = "openrouter"
        verify.claude_cli_available = lambda: True
        self.assertEqual(verify.resolve_backend(OPUS), "openrouter")

    def test_auto_anthropic_with_cli(self):
        os.environ["MYINC_VERIFY_BACKEND"] = "auto"
        verify.claude_cli_available = lambda: True
        self.assertEqual(verify.resolve_backend(OPUS), "claude-cli")

    def test_auto_anthropic_without_cli(self):
        os.environ["MYINC_VERIFY_BACKEND"] = "auto"
        verify.claude_cli_available = lambda: False
        self.assertEqual(verify.resolve_backend(OPUS), "openrouter")

    def test_auto_non_anthropic_stays_openrouter(self):
        os.environ["MYINC_VERIFY_BACKEND"] = "auto"
        verify.claude_cli_available = lambda: True
        self.assertEqual(verify.resolve_backend("deepseek/deepseek-v4-flash"), "openrouter")


class TestNoCliRaises(unittest.TestCase):
    def test_raises_without_cli(self):
        saved = verify.claude_cli_available
        verify.claude_cli_available = lambda: False
        try:
            with self.assertRaises(ProviderError):
                verify._verify_via_claude_cli("prompt", OPUS)
        finally:
            verify.claude_cli_available = saved


if __name__ == "__main__":
    unittest.main(verbosity=2)
