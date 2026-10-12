# AI Skill Lab — R4F7H Offline `MERGE_ONLY` Verifier

**Specification:** `R4F7H_OFFLINE_MERGE_CONTRACT_R1` — Draft.  
**Implementation:** Tested in isolated local Git branch; **not deployed / not production-qualified**.  
**Audit:** PASS WITH CONDITIONS for offline synthetic behavior, **HOLD** for external owner and merge authority.  
**Boundary:** no real Ed25519 owner key, GitHub App, provider authentication, check publisher, merge executor, deployment, or changes to GitHub/Vercel/Windows/Scheduler.

## Parent and version isolation

Parent baseline is the **checked clean** R4F7F Git commit `91df0e091eac8b4e33b093034ec75576b577f7bc`, tree `05783ff52490ec7933562635c973e49c9a075195`. All original R4F7F tracked files remain byte-identical; R4F7H contributes **additions only** on `offline/r4f7h-merge-only-r1`.

The R4F7F `MARK_READY_ONLY` code and `AI_SKILL_LAB_OWNER_ADMISSION_V1\x00` signature domain stay unchanged. R4F7H uses a distinct `MERGE_ONLY` payload schema, `AI_SKILL_LAB_OWNER_MERGE_V2\x00` domain, signed action, merge method `merge`, exact PR/base/head Git commit+trees, exact path/patch/evidence digests, coordination ref, issuer registry version, nonce and UTC expiry.

## Execution

On a disposable offline copy with Python and the locally available `cryptography==46.0.4`:

```bash
python -I -B run_tests.py
```

The unchanged R4F7F runner discovers both versions. Existing tests use ephemeral **synthetic Ed25519 keys in memory only**, and test-only SQLite databases in temporary directories. There is **no networking, token handling, host file mutation or real signing service**.

## Two-phase local contract

1. **`PREPARE`**: Verify v2 signed payload, mock owner registry and provider snapshot, exact provider branch rule, required CI from pinned sources, two READY previews on exact HEAD, current signed-scope lease, and a separately preissued nonce committed to the exact payload. Atomically consume the **test** nonce. Output `TEST_ONLY_PASS`, `github_check_publishable=false`, `merge_authorized=false`, `execution_action_performed=false`.
2. **`JIT_EXECUTION`**: Reverify the **same v2 signature** against a **fresh mock provider snapshot**, including an exact-HEAD, completed `success` `owner-merge-admission` check from the independent **synthetic** App ID with external ID binding to the v2 payload digest, and read back the consumed nonce. **It rechecks TTL even if the check remains green.** Output remains test-only with all effects false.

A `MARK_READY_ONLY` signature/check is never accepted for merge. An old green check does not extend an expired signature; a new head/tree, base, branch protection, lease or CI drift results in STOP/HOLD/DENY. Check `neutral` and `skipped` are *not* treated as success. No real check-run can be published by this package.

## New files

- `owner_admission/merge_v2.py` — strict v2 validation and two-phase synthetic verifier.
- `owner_admission/merge_v2_contracts.py` — explicit *unauthenticated* mock provider, branch and policy contracts.
- `owner_admission/merge_v2_ledger.py` — version-isolated, test-only transactional SQLite nonce model.
- `owner_admission/merge_v2_provider_port.py` — all real provider and GitHub actions raise `IndependentProviderNotInstalled`.
- `tests/merge_v2_support.py`, `tests/test_merge_v2.py`, `tests/test_merge_v2_ledger.py`, `tests/test_merge_v2_safety.py` — synthetic fixtures and negative tests.
- `docs/R4F7H_SECURITY_CONTRACT.md`, `docs/R4F7H_TEST_MATRIX.md`, `evidence/R4F7H_READ_ONLY_JIT_20261012.json`, this README and `R4F7H_SOURCE_SHA256_MANIFEST_20261012.json`.

## Known blockers — NOT bypassed

At live GitHub JIT, PR #226 remains **OPEN/DRAFT**, `main=0ab438a...`, head `c4dc530...`, 9/9 CI SUCCESS, owner-merge check is not required/installed, public preview on exact head is CANCELED, ingress preview absent and coordination lease expired. **The real PR cannot satisfy this synthetic MERGE gate.** The current branch protection must remain in place; no rulesets or new App was created.

Future system must independently host the real owner public-key registry, authenticated provider readback, independent GitHub App/check, durable nonce ledger and rollback protection, and an execution path that **immediately** revalidates TTL and SHA before merge. Neither a Python receipt nor a GitHub green status provides expiring authorization by itself. Real key custody and hosting remain owner decisions.

**Operator stop:** `OWNER_TRUST_ROOT_HOLD / INDEPENDENT_PROVIDER_HOLD / NONCE_LEDGER_HOLD / OWNER_MERGE_CHECK_HOLD / CURRENT_LEASE_HOLD / BOTH_PREVIEW_READY_HOLD / MARK_READY_HOLD / MERGE_HOLD / PUBLICATION_HOLD / HOST_RESOURCE_HOLD`.
