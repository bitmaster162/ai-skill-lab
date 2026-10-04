#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import hmac
import io
import json
import os
from pathlib import Path
import sys
import unittest
import urllib.error
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from public_monitor import (
    RELAY_SCHEMA,
    RELAY_SIGNATURE_DOMAIN,
    RELAY_URL,
    TARGETS,
    Result,
    main,
    relay_payload,
    run_checks,
    send_monitor_alert,
)


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

    def test_relay_payload_contains_only_bounded_failure_metadata(self):
        request_id = "11111111-2222-4333-8444-555555555555"
        payload = relay_payload(
            [Result("aiskillab-start", "https://aiskillab.work/start", 200, 503, "unexpected_status=503")],
            request_id,
        )
        self.assertEqual(payload["schema"], RELAY_SCHEMA)
        self.assertEqual(payload["requestId"], request_id)
        self.assertEqual(
            payload["failures"],
            [{"name": "aiskillab-start", "expected": 200, "actual": 503, "error": "unexpected_status=503"}],
        )
        self.assertNotIn("url", payload["failures"][0])

    def test_relay_alert_is_skipped_without_strong_secret_or_failures(self):
        with patch("urllib.request.urlopen") as opener:
            self.assertFalse(send_monitor_alert([], "x" * 32))
            self.assertFalse(
                send_monitor_alert(
                    [Result("bitevo-home", "https://bitevo.work/", 200, 500, "unexpected_status=500")],
                    "",
                )
            )
            self.assertFalse(
                send_monitor_alert(
                    [Result("bitevo-home", "https://bitevo.work/", 200, 500, "unexpected_status=500")],
                    "short",
                )
            )
            opener.assert_not_called()

    def test_relay_alert_posts_only_to_fixed_cloudflare_endpoint_with_domain_separated_hmac(self):
        captured = {}
        secret = "0123456789abcdef0123456789abcdef"
        request_id = "11111111-2222-4333-8444-555555555555"
        now_seconds = 1791099000
        failure = Result("bitevo-start", "https://bitevo.work/start", 200, 500, "unexpected_status=500")

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["method"] = request.get_method()
            captured["headers"] = dict(request.header_items())
            captured["body"] = request.data
            return FakeResponse(200)

        with patch("urllib.request.urlopen", opener):
            ok = send_monitor_alert(
                [failure],
                secret,
                now_seconds=now_seconds,
                request_id=request_id,
            )

        self.assertTrue(ok)
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["url"], RELAY_URL)
        body = captured["body"]
        payload = json.loads(body.decode("utf-8"))
        self.assertEqual(payload["requestId"], request_id)
        expected = hmac.new(
            secret.encode("utf-8"),
            f"{RELAY_SIGNATURE_DOMAIN}.{now_seconds}.{request_id}.".encode("utf-8") + body,
            hashlib.sha256,
        ).hexdigest()
        self.assertEqual(
            captured["headers"]["X-ai-skill-lab-public-monitor-signature"],
            f"v1={expected}",
        )

    def test_main_green_never_reads_or_posts_relay_secret(self):
        with patch(
            "public_monitor.run_checks",
            return_value=[Result(name, url, expected, 200, None) for name, url, expected in TARGETS],
        ), patch("public_monitor.send_monitor_alert") as alert:
            with patch.dict(os.environ, {}, clear=True):
                rc = main()
        self.assertEqual(rc, 0)
        alert.assert_not_called()

    def test_main_failure_attempts_one_relay_alert_then_fails(self):
        failed = Result("bitevo-start", "https://bitevo.work/start", 200, 500, "unexpected_status=500")
        with patch("public_monitor.run_checks", return_value=[failed]), \
             patch("public_monitor.send_monitor_alert", return_value=True) as alert, \
             patch.dict(os.environ, {"PUBLIC_MONITOR_RELAY_SECRET": "x" * 32}, clear=True):
            rc = main()
        self.assertEqual(rc, 1)
        alert.assert_called_once_with([failed], "x" * 32)


if __name__ == "__main__":
    unittest.main(verbosity=2)
