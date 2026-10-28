"""Exact R1 checker custody under the pinned SITE-A2 successor."""
from pathlib import Path
from unittest.mock import patch
import unittest
import site_a2_pricing_checker_quarantine as q
import site_a1_a2_r2_successor as release
ROOT=Path(__file__).resolve().parents[1]

class QuarantineTest(unittest.TestCase):
    def test_exact_admission(self):
        self.assertTrue(q.verify(ROOT))
    def test_unknown_release_fails(self):
        with patch.object(release,"active",return_value=False):
            with self.assertRaises(release.SuccessorHold):
                q.verify(ROOT)
    def test_mutated_historic_checker_fails(self):
        with patch.object(q,"CHECKER_SHA","0"*64):
            with self.assertRaisesRegex(ValueError,"checker drift"):
                q.verify(ROOT)
    def test_tampered_catalog_fails(self):
        with patch.object(q,"catalog",return_value={"@type":"OfferCatalog","itemListElement":[]}):
            with self.assertRaisesRegex(ValueError,"pricing offer"):
                q.verify(ROOT)
if __name__=="__main__":unittest.main(verbosity=2)
