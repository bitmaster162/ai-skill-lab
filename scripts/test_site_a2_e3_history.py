"""Fail-closed historic R6/R7 projection for SITE-A2 E3 gates."""
from pathlib import Path
import unittest
from unittest.mock import patch
import site_a2_e3_history as hist
import site_a1_a2_r2_successor as successor

class E3Historical(unittest.TestCase):
    def test_exact_historic_route(self):
        raw=hist.legacy_r6_html("about.html")
        self.assertEqual(successor.sha(raw),hist.historical_profile()["r6_file_pins"]["about.html"]["sha256"])
    def test_unknown_route_denied(self):
        with self.assertRaisesRegex(ValueError,"SITE_A2_E3_DENY route"):
            hist.legacy_r6_html("not-approved.html")
    def test_historic_blob_tamper_denied(self):
        getter=successor.git_blob
        def corrupt(commit,path):
            blob=getter(commit,path)
            return blob+b"tamper" if commit==hist.R6 and path=="deploy/live/about.html" else blob
        with patch.object(successor,"git_blob",side_effect=corrupt):
            with self.assertRaisesRegex(ValueError,"historical R6/R7 replay"):
                hist.legacy_r6_html("about.html")
    def test_manifest_unknown_fails(self):
        with patch.object(successor,"active",return_value=False):
            hist.authorize.cache_clear()
            with self.assertRaisesRegex(ValueError,"unauthorized release"):
                hist.legacy_r6_html("about.html")
        hist.authorize.cache_clear()
    def test_profile_hash_fails(self):
        with patch.object(hist,"PROFILE_SHA","0"*64):
            with self.assertRaisesRegex(ValueError,"profile SHA"):
                hist.historical_profile()

if __name__=="__main__":
    unittest.main(verbosity=2)
