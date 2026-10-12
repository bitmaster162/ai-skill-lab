# R4F7H — `MERGE_ONLY` synthetic security contract

**Policy version:** `R4F7H_OFFLINE_MERGE_CONTRACT_R1`, schema `ai-skill-lab.owner-merge-admission.v2`, versioned without modifying the R4F7F normative payload. Specification **Draft**. Local implementation **Tested**; production integration **Unimplemented**. The only output called PASS is `TEST_ONLY_PASS`. Its effect flags are **all false**.

## Cryptography and exact signed scope

- Domain separation: ASCII `AI_SKILL_LAB_OWNER_MERGE_V2` followed by byte `00`; v1 owner-ready signatures **never** verify in v2.
- Signed preimage: `DOMAIN + canonical_bytes(payload)` from the unchanged local canonicalization implementation; sorted object keys, minified UTF-8, no floats/NaN/duplicate fields, not RFC 8785/JCS.
- Strict v2 envelope is exactly `{"payload": {...}, "signature_hex": "<128 lowercase hex>"}`.
- Signed field set: `schema`, `policy_version`, `owner_registry_version`, `issuer_key_id`, `repo`, `pr`, `base_branch`, `merge_method`, `action`, `base_commit`, `base_tree`, `head_commit`, `head_tree`, `patch_sha256`, `evidence_sha256`, `allowed_paths_digest`, `coordination_ref_sha`, `issued_at_utc`, `expires_at_utc`, `nonce`, `review_mode`, `required_merge_context`, `prohibited_effects`.
- Required action `MERGE_ONLY`, method `merge`, branch `main`, review mode `SOURCE_ONLY_NO_RELEASE`, check `owner-merge-admission`. Signed `prohibited_effects` disallow `mark_ready`, `deploy`, `production_publish`, `auto_merge`, `force_push`, `branch_delete`, `squash`, `rebase`.
- SHA fields are lower-case hex only. Paths must be unique normalized relative ASCII paths without traversal. UTC time is canonical `YYYY-MM-DDTHH:MM:SSZ`.
- Signature must match synthetic test registry and nonrevoked issuer. A real independently administered registry does **not** exist.

## Phase 1 — `PREPARE` (offline test-only)

1. Audience must be `OFFLINE_TEST_ONLY`; all production audiences stop at `HOLD_REAL_MERGE_VERIFIER_UNIMPLEMENTED`.
2. Verify signed schema, action, prohibited effects, owner registry version/key, time and fixed versioned policy.
3. Source-less mock provider facts must match exact repo/PR/head/base Git commits and trees, changed paths and hashes. PR must be **OPEN, not DRAFT, mergeable**.
4. Mock protected `main` rule must require PR, checks, freshness, conversation resolution and no bypass/force/deletion. Normal merge only, no linear-history requirement. Source-pinned `owner-merge-admission` must be required **from the different independent App ID**.
5. Required `static-release`, `language-parity`, `CodeQL` checks are each uniquely named, source-matched, exact-head, `pull_request`, `completed/success`. Duplicate context names from simultaneous push/PR events cause `HOLD_DUPLICATE_CHECK_NAMES`.
6. Require both policy-named Vercel previews `READY` on signed HEAD, no synthetic waiver; current production app and ingress do not satisfy these as currently observed.
7. Require exact conflict-free `MERGE_ONLY` lease, unexpired with matching coordination SHA and head.
8. Consume **preissued** `(issuer, nonce)` in an existing SQLite **test** ledger, committed to exact `MERGE_ONLY`, repo/PR/base/head/payload SHA/expiry, with a unique issuer+nonce key across actions.
9. Only `TEST_ONLY_PASS` with `github_check_publishable=false`; no real check is ever published.

## Phase 2 — `JIT_EXECUTION` (offline test-only)

- Re-evaluate the same signed envelope against a *new fresh snapshot* and new clock: no implicit reuse of prior PREPARE facts.
- Require a **single** completed `success` merge check at `owner-merge-admission`, exact signed HEAD, expected independent App ID and `external_id=owner-merge-admission:v2:<payload_sha256>`. Check completion must occur between owner issuance and observation, before signature expiry. Neutral/skipped do not pass.
- Revalidate the signed expiry, provider snapshot age, policy, CI, exact Git SHAs/trees, branch protection, two previews, lease and consumed nonce ledger readback.
- An old green check **does not expire automatically on GitHub**, so actual merge requires its own live source-authenticated gate. These test-only checks **do not** constitute one.
- No JIT function calls `merge`, `push`, `publish`, `mark_ready` or a remote API. `DisabledIndependentProviderPort` throws for all such methods.

## Out-of-scope / residual risk

- Provider input dataclasses are caller-supplied mocks, not authenticated GitHub/Vercel readbacks; a malicious party can fabricate them outside tests. The receipt explicitly reports `independently_authenticated_provider=false`.
- Local test ledger is not under independent custody and cannot prove monotonically durable replay prevention after stale backup restore. A real shared owner ledger, unique nonce across all actions, transactional preissue/consume/audit and backed-up monotonic recovery are separate work.
- No real owner key generation, public-key publication, revocation API, GitHub App installation, check-run publisher, branch rule write, SHA compare-and-swap merge executor, postmerge commit/tree evidence, cloud VM/database or production publication is implemented.
- A green check alone cannot impose expiring approval; owner-authorized, independently controlled execution must recheck expiry/nonce/sha immediately before an actual merge.
- Old v1 `MARK_READY_ONLY` and new v2 `MERGE_ONLY` are intentionally incompatible. Actual mark-ready and publish remain separate explicitly owner-approved actions and are not inferred from a merge attestation.
- Local coverage/test SUCCESS only applies to synthetic contracts at the verified local commit and environment. No claim of production readiness, independent code review, or provider enforcement is made.

## Prohibited rollout shortcuts

Do not set v1 `owner-admission` as required merge status, disable existing classic protection, create unpinned status check, reinterpret `neutral`/`skipped` as PASS, turn on linear history with merge-only strategy, run local fixtures against the Windows host, send secrets through PR/Actions/ChatGPT, deploy verifier beside candidate-controlled production code, or silently retry/reissue a consumed nonce after a failed publication.
