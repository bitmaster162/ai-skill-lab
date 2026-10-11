#!/usr/bin/env python3
"""R4E standard-library negative fixtures. Not an owner approval test."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from release_admission import (
 AdmissionDenied, APPROVED_HISTORICAL_PINS, BASELINE_ROUTE_SHA256,
 accepted_routes, load_archived_profile, verify_profile_identity, validate_full,
)
from release_admission.baseline import BASELINE_ROUTES, route_digest

ID_F2="T1_6F2_ADULT_FIRST_TASKS_R1"
ID_E36="E3_6_WORKSHOP_HERO_PANEL_R1"


class ReleaseProfileAdmissionTest(unittest.TestCase):
    def test_baseline_52(self):
        self.assertEqual(len(BASELINE_ROUTES), 52)
        self.assertEqual(route_digest(BASELINE_ROUTES), BASELINE_ROUTE_SHA256)

    def test_immutable_historical_identity(self):
        for release_id, num_files, num_routes in ((ID_E36,96,52),(ID_F2,98,54)):
            with self.subTest(release_id=release_id):
                raw=load_archived_profile(release_id)
                self.assertEqual(hashlib.sha256(raw).hexdigest(), APPROVED_HISTORICAL_PINS[release_id])
                receipt=verify_profile_identity(release_id,raw)
                self.assertEqual(receipt.file_count,num_files)
                self.assertEqual(receipt.route_count,num_routes)
                self.assertFalse(receipt.publication_authorized)
                self.assertFalse(receipt.live_bytes_verified)

    def test_unknown_release_denied(self):
        for candidate in ("NEXT_R1", "T1_6F3_R4E", "", "somebad", "E3_6_WORKSHOP_HERO_PANEL_R2"):
            with self.subTest(value=candidate), self.assertRaises((ValueError, AdmissionDenied)):
                load_archived_profile(candidate)

    def test_profile_tamper_denied(self):
        data=bytearray(load_archived_profile(ID_F2))
        data[30]^=1
        with self.assertRaises(AdmissionDenied):
            verify_profile_identity(ID_F2,bytes(data))

    def test_cross_release_profile_denied(self):
        with self.assertRaises(AdmissionDenied):
            verify_profile_identity(ID_E36,load_archived_profile(ID_F2))

    def test_extra_unpinned_slug_denied(self):
        routes=accepted_routes(["new-test-guide"])
        self.assertEqual(len(routes),54)  # construction is not owner admission
        self.assertNotIn("new-test-guide", {"ai-first-tasks-for-adults"})
        with self.assertRaises(AdmissionDenied):
            validate_full("FAKE_RELEASE",load_archived_profile(ID_F2),b"{}",{}, {},[],[],[])

    def test_invalid_slugs(self):
        for bad in ("../admin","a--b","Hello","a_b","", "a/a"):
            with self.subTest(slug=bad),self.assertRaises(AdmissionDenied):
                accepted_routes([bad])

    def test_duplicate_slugs(self):
        with self.assertRaises(AdmissionDenied):
            accepted_routes(["x","x"])

    def test_baseline_route_collision(self):
        with self.assertRaises(AdmissionDenied):
            accepted_routes(["ai-safety-for-kids"])

    def test_manifest_mismatch_denied(self):
        with self.assertRaises(AdmissionDenied):
            validate_full(ID_F2,load_archived_profile(ID_F2),b"{}",{}, {},[],[],[])

    def test_historical_self_approval_not_supported(self):
        self.assertFalse(hasattr(__import__("release_admission.authority",fromlist=["x"]),"approve_release"))
        self.assertNotIn("NEW_R1",APPROVED_HISTORICAL_PINS)

    def test_missing_full_checkout_holds(self):
        sys.path.insert(0,str(ROOT/"scripts"))
        try:
            from check_release_profile_admission import run, Hold
            with tempfile.TemporaryDirectory(prefix="r4e_empty_") as tmp:
                with self.assertRaises(Hold):
                    run(Path(tmp))
        finally:
            sys.path.remove(str(ROOT/"scripts"))

    def test_no_merge_or_publish_capability(self):
        from release_admission.validator import ValidationReceipt, ProfileIdentity
        fields=ValidationReceipt.__dataclass_fields__
        self.assertEqual(fields["publication_authorized"].default,False)
        self.assertFalse(ProfileIdentity(ID_F2,"historical","0"*64,98,54).publication_authorized)

    def test_unknown_release_manifest_denied(self):
        sys.path.insert(0,str(ROOT/"scripts"))
        try:
            from check_release_profile_admission import run, Deny
            with tempfile.TemporaryDirectory() as tmp:
                file=Path(tmp)/"deploy/live/_release.json"
                file.parent.mkdir(parents=True)
                file.write_text(json.dumps({"release_id":"T1_6F3_R4E_UNAPPROVED","files":[]}))
                with self.assertRaises(Deny): run(Path(tmp))
        finally:
            sys.path.remove(str(ROOT/"scripts"))

    def test_manifest_count_mismatch_denied(self):
        sys.path.insert(0,str(ROOT/"scripts"))
        try:
            from check_release_profile_admission import run, Deny
            with tempfile.TemporaryDirectory() as tmp:
                file=Path(tmp)/"deploy/live/_release.json"
                file.parent.mkdir(parents=True)
                file.write_text(json.dumps({"release_id":ID_F2,"files":[]}))
                with self.assertRaises(Deny): run(Path(tmp))
        finally:
            sys.path.remove(str(ROOT/"scripts"))

    def test_manifest_traversal_denied(self):
        sys.path.insert(0,str(ROOT/"scripts"))
        try:
            from check_release_profile_admission import run, Deny
            with tempfile.TemporaryDirectory() as tmp:
                file=Path(tmp)/"deploy/live/_release.json"
                file.parent.mkdir(parents=True)
                file.write_text(json.dumps({"release_id":ID_F2,
                    "files":[{"path":"../outside"}]*98}))
                with self.assertRaises(Deny): run(Path(tmp))
        finally:
            sys.path.remove(str(ROOT/"scripts"))

    def test_duplicate_asset_list_denied(self):
        sys.path.insert(0,str(ROOT/"scripts"))
        try:
            from check_release_profile_admission import run, Deny
            with tempfile.TemporaryDirectory() as tmp:
                file=Path(tmp)/"deploy/live/_release.json"
                file.parent.mkdir(parents=True)
                file.write_text(json.dumps({"release_id":ID_F2,
                    "files":[{"path":"a.html"}]*98}))
                with self.assertRaises(Deny): run(Path(tmp))
        finally:
            sys.path.remove(str(ROOT/"scripts"))

    def test_manifest_symlink_denied(self):
        sys.path.insert(0,str(ROOT/"scripts"))
        try:
            from check_release_profile_admission import run, Deny
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)
                original=root/"original.json"
                original.write_text(json.dumps({"release_id":ID_F2,"files":[]}))
                leaf=root/"deploy/live/_release.json"
                leaf.parent.mkdir(parents=True)
                leaf.symlink_to(original)
                with self.assertRaises(Deny): run(root)
        finally:
            sys.path.remove(str(ROOT/"scripts"))

    def test_corrupt_manifest_denied(self):
        sys.path.insert(0,str(ROOT/"scripts"))
        try:
            from check_release_profile_admission import run, Deny
            with tempfile.TemporaryDirectory() as tmp:
                leaf=Path(tmp)/"deploy/live/_release.json"
                leaf.parent.mkdir(parents=True)
                leaf.write_bytes(b"{invalid-json")
                with self.assertRaises(Deny): run(Path(tmp))
        finally:
            sys.path.remove(str(ROOT/"scripts"))

if __name__=="__main__":
    unittest.main(verbosity=2)
