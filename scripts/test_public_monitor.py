#!/usr/bin/env python3
from __future__ import annotations

import io
import os
from pathlib import Path
import sys
import unittest
import urllib.error
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from public_monitor import TARGETS, Result, format_alert, main, run_checks, send_telegram_alert


class FakeResponse:
    def __init__(self, status: int):
        self.status = status
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False


class PublicMonitorTests(unittest.TestCase):
    def test_exact_target_inventory(self):
        self.assertEqual(
            TARGETS,
            (
                ("bitevo-home", "https://bitevo.work/", 200),
                ("bitevo-pricing", "https://bitevo.work/pricing", 200),
                ("bitevo-start", "https://bitevo.work/start", 200),
                ("aiskillab-home", "https://aiskillab.work/", 200),
                ("aiskillab-start", "https://aiskillab.work/start", 200),
            ),
        )

    def test_all_green(self):
        results = run_checks(lambda url, timeout: 200)
        self.assertEqual(len(results), 5)
        self.assertTrue(all(item.error is None for item in results))

    def test_unexpected_status_fails(self):
        results = run_checks(lambda url, timeout: 500 if url.endswith("/pricing") else 200)
        failures = [item for item in results if item.error]
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0].name, "bitevo-pricing")
        self.assertEqual(failures[0].actual, 500)

    def test_network_error_is_redacted_to_type(self):
        def fail(_url, _timeout):
            raise RuntimeError("private resolver detail")
        result = run_checks(fail)[0]
        self.assertIsNone(result.actual)
        self.assertEqual(result.error, "request_error=RuntimeError")
        self.assertNotIn("private resolver detail", result.error)

    def test_alert_contains_only_bounded_failure_metadata(self):
        message = format_alert([
            Result("aiskillab-start", "https://aiskillab.work/start", 200, 503, "unexpected_status=503")
        ])
        self.assertIn("aiskillab-start", message)
        self.assertIn("expected=200", message)
        self.assertIn("observed=503", message)
        self.assertIn("https://aiskillab.work/start", message)

    def test_telegram_alert_is_skipped_without_both_secrets(self):
        with patch("urllib.request.urlopen") as opener:
            self.assertFalse(send_telegram_alert("failure", "", "123"))
            self.assertFalse(send_telegram_alert("failure", "1234:abcdefghijklmnopqrstuv", ""))
            opener.assert_not_called()

    def test_telegram_alert_posts_only_to_telegram_api(self):
        captured = {}
        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["method"] = request.get_method()
            captured["data"] = request.data.decode("utf-8")
            return FakeResponse(200)
        with patch("urllib.request.urlopen", opener):
            ok = send_telegram_alert("monitor failed", "123456:abcdefghijklmnopqrstuv", "-100123")
        self.assertTrue(ok)
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["url"], "https://api.telegram.org/bot123456:abcdefghijklmnopqrstuv/sendMessage")
        self.assertIn("chat_id=-100123", captured["data"])
        self.assertIn("monitor+failed", captured["data"])

    def test_main_green_never_reads_or_posts_telegram_secrets(self):
        with patch("public_monitor.run_checks", return_value=[
            Result(name, url, expected, 200, None) for name, url, expected in TARGETS
        ]), patch("public_monitor.send_telegram_alert") as alert:
            with patch.dict(os.environ, {}, clear=True):
                rc = main()
        self.assertEqual(rc, 0)
        alert.assert_not_called()

    def test_main_failure_attempts_one_alert_then_fails(self):
        failed = Result("bitevo-start", "https://bitevo.work/start", 200, 500, "unexpected_status=500")
        with patch("public_monitor.run_checks", return_value=[failed]), \
             patch("public_monitor.send_telegram_alert", return_value=True) as alert, \
             patch.dict(os.environ, {
                 "PUBLIC_MONITOR_TELEGRAM_BOT_TOKEN": "123456:abcdefghijklmnopqrstuv",
                 "PUBLIC_MONITOR_TELEGRAM_CHAT_ID": "-100123",
             }, clear=True):
            rc = main()
        self.assertEqual(rc, 1)
        alert.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
