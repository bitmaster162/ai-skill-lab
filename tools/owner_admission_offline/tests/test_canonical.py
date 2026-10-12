import unittest

from owner_admission.canonical import (
    InvalidDocument, canonical_bytes, canonical_sha256, strict_json_bytes, sha256_bytes,
    utc_timestamp,
)


class CanonicalJsonTest(unittest.TestCase):
    def test_sorted_minimal_serialization(self):
        self.assertEqual(canonical_bytes({"z": 1, "a": [True, False]}),
                         b'{"a":[true,false],"z":1}')

    def test_not_claimed_as_jcs_float_rejected(self):
        with self.assertRaises(InvalidDocument):
            canonical_bytes({"a": 1.5})

    def test_duplicate_rejected_any_nesting(self):
        with self.assertRaises(InvalidDocument):
            strict_json_bytes(b'{"outer":{"x":1,"x":2}}')

    def test_nan_or_float_rejected(self):
        for raw in (b'{"x":NaN}', b'{"x":1.0}', b'{"x":Infinity}'):
            with self.subTest(raw=raw), self.assertRaises(InvalidDocument):
                strict_json_bytes(raw)

    def test_root_must_be_object(self):
        with self.assertRaises(InvalidDocument):
            strict_json_bytes(b'[]')

    def test_nonstring_object_keys_rejected(self):
        with self.assertRaises(InvalidDocument):
            canonical_bytes({1: "bad"})

    def test_max_canonical_nesting(self):
        value={"leaf": True}
        for _ in range(15):
            value={"nested": value}
        with self.assertRaises(InvalidDocument):
            canonical_bytes(value)

    def test_sha256_input_requires_bytes(self):
        with self.assertRaises(InvalidDocument):
            sha256_bytes("not bytes")

    def test_invalid_utf8_rejected(self):
        with self.assertRaises(InvalidDocument):
            strict_json_bytes(b'{"x":"\xff"}')

    def test_utc_exact(self):
        self.assertEqual(utc_timestamp("2026-10-12T13:00:00Z").year, 2026)
        for t in ("2026-10-12T13:00:00+00:00", "2026-99-12T13:00:00Z",
                  "2026-10-12T13:00:00.000Z"):
            with self.subTest(t=t), self.assertRaises(InvalidDocument):
                utc_timestamp(t)

    def test_digest_stable_insertion_order(self):
        self.assertEqual(canonical_sha256({"b": 2, "a": 1}),
                         canonical_sha256({"a": 1, "b": 2}))

    def test_limit_oversized_input(self):
        with self.assertRaises(InvalidDocument):
            strict_json_bytes(b"{" + b" " * 20000 + b"}")

    def test_surrogates_rejected(self):
        with self.assertRaises(InvalidDocument):
            canonical_bytes({"x": "\ud800"})


if __name__ == "__main__":
    unittest.main()
