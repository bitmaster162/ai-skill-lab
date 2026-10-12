# R4F7F security contract — draft, test-only

## Deterministic representation

`owner_admission/canonical.py` is the source of truth. **This is not JCS/RFC 8785.** Input must be UTF-8 bytes, <=16,384 bytes. The parser rejects duplicate keys (including nested), NaN/Infinity, floats, surrogate codepoints, unknown fields, mixed/non-ASCII signed schema strings and noncanonical UTC timestamp formats.

The Ed25519 signed input is exactly:

```
Exact `DOMAIN` byte literal in code: ASCII `AI_SKILL_LAB_OWNER_ADMISSION_V1` followed by one NUL byte (hex `00`).
+ UTF-8 JSON(payload, sort_keys=true, separators=(',', ':'), ensure_ascii=false)
```

**Use the actual `DOMAIN` byte constant; do not copy this prose notation as a signing preimage.** JSON string values in the admitted schema are ASCII and strictly typed. The incoming envelope has **exactly** `payload` and `signature_hex` keys. Signature hexadecimal must be lowercase 128 characters.

Payload key set (exact): `schema`, `policy_version`, `issuer_key_id`, `repo`, `pr`, `action`, `base_commit`, `base_tree`, `head_commit`, `head_tree`, `evidence_sha256`, `allowed_paths_digest`, `patch_sha256`, `issued_at_utc`, `expires_at_utc`, `nonce`, `review_mode`, `coordination_ref_sha`, `limits`.

Allowed positive synthetic action: `MARK_READY_ONLY`; mode `SOURCE_ONLY_NO_RELEASE`; **all** effect limits false: `merge`, `production_publish`, `force_push`, `deploy`. An attestation for merge, publish or arbitrary actions must fail, regardless of signature.

`allowed_paths_digest = SHA256(canonical_bytes(sorted(exact_changed_paths)))`, where paths are unique, ASCII, slash-separated and free of `.`/`..` components. `patch_sha256` and `evidence_sha256` are SHA-256 of **raw input bytes**, not JSON descriptions of those bytes.

## Ordered fail-closed checks

1. **Test audience guard:** `TestPolicy(audience='OFFLINE_TEST_ONLY')`. Any production audience => `HOLD_PRODUCTION_VERIFIER_UNIMPLEMENTED`.
2. Exact schema, format, typed payload, ASCII and action/limits (`DENY` on drift).
3. Out-of-candidate `TrustRegistry` with a pinned Ed25519 public key and non-revoked key ID. Verify owner signature (`DENY` if unknown/wrong/revoked). In these tests, the public registry and key are *synthetic in-memory fixtures*.
4. Injected UTC clock, issuance time, expiry and TTL constraints from policy (`DENY` if expired/future/oversized).
5. Current simulated provider snapshot: exact repo/PR/base/head SHA+trees, OPEN/DRAFT state, fresh source observation, exact changed-path and patch/evidence digests.
6. Simulated protected branch policy: require PR, checks, up-to-date, conversations resolved, no bypass/force/deletion, normal-merge compatibility. **Pinned** `owner-admission` App ID must be present as a required check, separate from CI Apps.
7. CI check evidence: one unambiguous successful `pull_request` check per required distinct job name and source App ID, exact head SHA. Duplicate `push`+`pull_request` names => `HOLD`, never count both as independent approvals.
8. Both policy-named previews must be `READY` for the exact head SHA. No waiver in this version.
9. Current conflict-free coordination lease: signed ref SHA, target, action and UTC expiry match. Expired/missing => `HOLD`.
10. **Previously registered** nonce commitment in an existing SQLite test ledger. It must match `issuer`, `nonce`, `payload_sha256`, `action`, `head_commit` and `expires_at`. Atomic `BEGIN IMMEDIATE + INSERT OR IGNORE` prevents replay. Ledger failure => `HOLD`, unissued nonce => `DENY`, consumed nonce => `DENY`.
11. Return `TEST_ONLY_PASS` with every external effect authorization field **false**. Test ledger consumption is the only side effect; it is confined to the disposable local test directory.

## Trust boundaries not yet implemented

Actual GitHub/Vercel/coordination APIs; authenticated provider responses and immutable current readback; key custody, issuer registration, revocation and rotation; independent durable ledger and CAS service; verified App identity and GitHub check-run publisher; pinned required status of App in GitHub main protection; key signing UI; owner human approval workflow; workflow double-trigger removal; user-approved preview-policy exception (none now); mark-ready/merge/deploy action dispatch.

**Never connect this local code directly to the provider as a check publisher.** The output type itself says `github_check_publishable=False`. Separate independent infrastructure and owner approval are needed before a real status can be emitted.

## Developer note

Test data uses actual GitHub SHA strings from a historical read-only reference, but the patches, CI source IDs, previews, leases, public key, nonce issuance and ownership assertions are **entirely synthetic**. A passing fixture cannot demonstrate current provider readiness. `policy_version` and `schema` changes must be versioned, with an updated manifest and independent tests.
