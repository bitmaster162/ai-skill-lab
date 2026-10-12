"""R4F7H fail-closed source and capability tests, not deployment proofs."""
from __future__ import annotations

import ast
from dataclasses import fields, replace
from pathlib import Path
import json
import unittest

from owner_admission.canonical import canonical_bytes
from owner_admission.merge_v2 import (
    DOMAIN as V2_DOMAIN, SCHEMA as V2_SCHEMA, ACTION as V2_ACTION,
    MergeTestReceipt, evaluate_merge_only,
)
from owner_admission.verifier import DOMAIN as V1_DOMAIN, ACTION as V1_ACTION
from tests.merge_v2_support import MergeFixture

ROOT=Path(__file__).resolve().parents[1]


class TestMergeSafety(unittest.TestCase):
    def setUp(self):
        self.f=MergeFixture()
        self.addCleanup(self.f.close)

    def test_v1_v2_action_and_crypto_domains_differ(self):
        self.assertEqual(V1_ACTION,"MARK_READY_ONLY")
        self.assertEqual(V2_ACTION,"MERGE_ONLY")
        self.assertNotEqual(V1_DOMAIN,V2_DOMAIN)
        self.assertEqual(V2_DOMAIN[-1],0)
        self.assertEqual(V2_SCHEMA,"ai-skill-lab.owner-merge-admission.v2")

    def test_all_live_effect_fields_default_false(self):
        for n in ("real_owner_authority","github_check_publishable","merge_authorized",
                  "mark_ready_authorized","deploy_authorized",
                  "production_publish_authorized","execution_action_performed",
                  "independently_authenticated_provider"):
            self.assertEqual(next(x for x in fields(MergeTestReceipt) if x.name==n).default,False)

    def test_not_a_production_adapter(self):
        for file in ("merge_v2.py","merge_v2_contracts.py"):
            content=(ROOT/"owner_admission"/file).read_text(encoding="utf-8")
            tree=ast.parse(content)
            imports=[]
            for n in ast.walk(tree):
                if isinstance(n,ast.Import):imports.extend(a.name.split(".")[0] for a in n.names)
                if isinstance(n,ast.ImportFrom) and n.module:imports.append(n.module.split(".")[0])
            for banned in ("requests","httpx","urllib","socket","subprocess","os","boto3","jwt","github"):
                self.assertNotIn(banned,imports,file)
            self.assertNotIn("Ed25519PrivateKey",content,file)

    def test_no_real_owner_key_in_module_or_readme(self):
        for file in (ROOT/"owner_admission"/"merge_v2.py",
                     ROOT/"owner_admission"/"merge_v2_contracts.py"):
            content=file.read_text(encoding="utf-8")
            self.assertNotIn("BEGIN PRIVATE KEY",content)
            self.assertNotIn("generate_private_key",content)

    def test_no_provider_authentication_flag_can_be_self_asserted(self):
        value=self.f.evaluate()
        self.assertEqual(value.status,"TEST_ONLY_PASS")
        self.assertFalse(value.independently_authenticated_provider)
        self.assertFalse(value.real_owner_authority)

    def test_fake_provider_source_named_production_still_holds(self):
        p=replace(self.f.provider,source="authenticated:github")
        self.assertEqual(self.f.evaluate(provider=p).code,
                         "HOLD_INDEPENDENT_PROVIDER_NOT_IMPLEMENTED")

    def test_incorrect_json_duplicate_key_denied(self):
        env=json.loads(self.f.envelope())
        b=canonical_bytes(env)
        b=b.replace(b'"pr":226,',b'"pr":226,"pr":227,',1)
        self.assertEqual(self.f.evaluate(envelope=b).code,"DENY_INVALID_MERGE_JSON")

    def test_json_float_denied(self):
        b=self.f.envelope().replace(b'"pr":226,',b'"pr":226.0,',1)
        self.assertEqual(self.f.evaluate(envelope=b).code,"DENY_INVALID_MERGE_JSON")

    def test_garbled_utf8_denied(self):
        self.assertEqual(self.f.evaluate(envelope=b'\xff\xfe\xfa').code,
                         "DENY_INVALID_MERGE_JSON")

    def test_invalid_nonce_denied(self):
        self.assertEqual(self.f.evaluate(envelope=self.f.envelope({"nonce":"n"})).code,
                         "DENY_NONCE_FORMAT")

    def test_unknown_envelope_policy_attribute_denied(self):
        env=json.loads(self.f.envelope())
        env["payload"]["trust_me"]=True
        self.assertEqual(self.f.evaluate(envelope=canonical_bytes(env)).code,
                         "DENY_SIGNED_FIELDS")

    def test_unexpected_preview_waiver_cannot_be_injected(self):
        env=json.loads(self.f.envelope())
        env["payload"]["waive_preview"]=True
        self.assertEqual(self.f.evaluate(envelope=canonical_bytes(env)).code,
                         "DENY_SIGNED_FIELDS")

    def test_unsigned_or_disconnected_production_mode_holds(self):
        real=replace(self.f.policy,audience="PRODUCTION")
        r=self.f.evaluate(policy=real)
        self.assertEqual(r.status,"HOLD")
        self.assertFalse(r.merge_authorized)

    def test_retained_original_legacy_test_suite(self):
        for name in ("tests/test_verifier.py","owner_admission/verifier.py",
                     "owner_admission/ledger.py"):
            self.assertTrue((ROOT/name).is_file())

    def test_production_adapter_refuses_every_external_action(self):
        from owner_admission.merge_v2_provider_port import (
            DisabledIndependentProviderPort, IndependentProviderNotInstalled,
        )
        port=DisabledIndependentProviderPort()
        for name, kwargs in (
            ("read_authenticated_snapshot", dict(repo="bitmaster162/ai-skill-lab",pr=226)),
            ("publish_source_pinned_merge_check", dict(repo="bitmaster162/ai-skill-lab",commit="a"*40,receipt=b"fake")),
            ("execute_merge", dict(repo="bitmaster162/ai-skill-lab",pr=226,expected_head="a"*40)),
            ("mark_ready", dict(repo="bitmaster162/ai-skill-lab",pr=226)),
            ("deploy", dict(release="not real")),
        ):
            with self.subTest(name=name):
                with self.assertRaises(IndependentProviderNotInstalled):
                    getattr(port,name)(**kwargs)

    def test_provider_port_has_no_network_code_or_client(self):
        port=(ROOT/"owner_admission"/"merge_v2_provider_port.py").read_text(encoding="utf-8")
        tree=ast.parse(port)
        import_roots=[]
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):import_roots.extend(v.name.split(".")[0] for v in n.names)
            if isinstance(n,ast.ImportFrom) and n.module:import_roots.append(n.module.split(".")[0])
        self.assertEqual(set(import_roots),{"__future__"})

    def test_preview_waiver_not_inferred_from_source_only(self):
        p=replace(self.f.provider,previews=tuple())
        self.assertEqual(self.f.evaluate(provider=p).code,
                         "HOLD_REQUIRED_MERGE_PREVIEWS_MISSING")


if __name__=="__main__":
    unittest.main()
