# AI Skill Lab — R4F7F Offline Owner-Admission Verifier

**Specification:** `R4F7F_OFFLINE_CONTRACT_R1` — **Draft** (derived from `R4F7D_DEF_FIRST_R1`).
**Implementation:** locally **Tested**, independent deployment **Unimplemented**.
**Security/audit:** `PASS WITH CONDITIONS` for synthetic contract behavior, `HOLD` for all real owner authority.
**Scope:** local isolated Git repo only. Not PR #226, not a GitHub App, not a merge/publish gate.

## What is implemented

- Strict JSON parsing rejecting duplicate fields, floats/NaN, bad UTF-8 and untyped fields.
- Deterministic canonical JSON UTF-8 (`sort_keys=True`, compact separators, no floats). **Not RFC 8785/JCS.** Changing canonicalization requires a new version and all signatures reissued.
- Ed25519 signature **verification only** with domain separation `AI_SKILL_LAB_OWNER_ADMISSION_V1\x00` and a separately passed public-key registry. No owner private key generated or stored.
- A **test-only** `MARK_READY_ONLY` attestation contract bound to repository/PR, base and head commit+tree, SHA-256 of exact patch and evidence bytes, exact changed paths and path digest, issuer, nonce, UTC TTL, scope limits and coordination ref.
- Offline test of provider facts: required CI context+source IDs, ambiguity of duplicate check names, protected branch conditions, independently pinned `owner-admission` App, two Vercel previews on exact HEAD, active coordination lease and fresh provider snapshot.
- SQLite nonce **preissuance + atomic consume**: the nonce must be bound to the exact signed payload *before* use. An unissued, reused or differently-scoped nonce is denied. The ledger path must already exist; evaluation never bootstraps it.
- Test harness and fail-closed negative scenarios. **Every positive receipt explicitly says `TEST_ONLY_PASS` and denies all live actions**, including publishing a GitHub check, mark-ready, merge and deployment.

## Reproduce safely

Run on a disposable copy with Python 3.11+ and the already-available `cryptography==46.0.4` dependency. **Do not install packages on the Windows production host** to run this demonstration.

```bash
python -I -B run_tests.py
```

This runner explicitly loads only the local project to work with `-I`. Tests create disposable SQLite files and temporary **synthetic in-memory Ed25519 keys**; they never create an actual owner signing key or call a remote API.

For the known input schema, refer to `owner_admission/verifier.py` and `docs/SECURITY_CONTRACT.md`.

## Invariants / intentional limitations

1. **No real authorization can ever result from this package.** The return type always has `eligible_for_real_action=false`, `github_check_publishable=false`, `merge_authorized=false`, `production_publish_authorized=false`.
2. Caller-provided `ProviderSnapshot` has **no provider-origin authentication**. All successful tests are simulations. A real verifier must independently obtain GitHub/Vercel/coordination facts with restricted credentials, and ensure exact provenance; it must not accept candidate-supplied snapshots.
3. The public-key registry, independent GitHub App, owner key custody, signature issuance policy, durable independently owned ledger service, actual required `owner-admission` check source and provider rules are **not installed**.
4. Existing CI uses duplicate `static-release` and `language-parity` check names from both `push` and `pull_request`. This contract returns `HOLD_DUPLICATE_CHECK_NAME_AMBIGUITY`, not a false PASS, for that shape.
5. Both production preview surfaces and coordination lease are required by current policy; missing READY previews or an expired lease stay HOLD. No source-only waiver has been authorized.
6. Actual `main` has an existing **classic branch protection rule**. This demo does not replace or modify it; it adds no GitHub rulesets and does not alter normal-merge policy.
7. A real human must separately approve `MARK_READY_ONLY`, `MERGE_ONLY`, and `PRODUCTION_PUBLISH_ONLY`. This local test only models the first action's contract; it cannot approve any action.
8. `bootstrap_test_ledger` is intentionally test-only. Real nonce issuance, ledger custody, rotation, recovery, authorization and high-availability design remain separate decisions.
9. ZIP input is source code, not a certificate. Never treat archive checksums, successful historical replay or PR green CI as release authority.

## Source context, not permission

- Repository: `bitmaster162/ai-skill-lab`, PR [#226](https://github.com/bitmaster162/ai-skill-lab/pull/226), review-only DRAFT.
- Baseline `main`: `0ab438a2568e562603b707c377c91bee1c836a8a` / tree `7eaced40ab4b21c621d37b072d1558343574a801`.
- PR HEAD: `c4dc530b1c62694c6c8f9dbac25bf9d26c46d690` / tree `2848b8684ea8766d52195e958e98983ae42bcffd`.
- Spark historical replay receipt SHA-256: `2a6a8dc5251726a7298c01f6e8c1dc9aca874e579887f78a64bf4f586a065ca1`. This is independent evidence only with stated provenance limitations.
- R4F7D source design SHA-256: `f915176e19f924b821f60dcd4287458161bbec9d0acd201182f6f2556e013492`.
- No secrets, GitHub token, signer's private key, or actual GitHub App credentials are packaged.

## Next gates

See `docs/REMAINING_OWNER_DECISIONS.md`. External owner key, App/check publisher, independently controlled ledger and effective branch enforcement require **separate explicit approvals**, JIT verification and a new Git baseline in their own trust domain before implementation. PR #226 stays DRAFT and merge/publication remain HOLD.
