# R4F7F → R4F7G / H explicit decision gates

## Observed facts vs future authority

At JIT (12 Oct 2026), PR #226 remains `OPEN/DRAFT` with 9/9 CI success; main production deployment is unchanged and READY. R4F7E *browser readback* confirmed existing classic `main` protection: PR required, `static-release`/`language-parity`/`CodeQL` pinned to GitHub-app sources, up-to-date branch required, conversation resolution required, no bypass, force push and deletion denied. Approvals are currently OFF. GitHub API administration protection detail returned 403 for the connected App; UI audit is provider observed but not yet an automated verifier feed. Rulesets list is empty.

The coordination lease remains expired, the two Vercel PR previews have not been demonstrated READY, and candidate-owned `release_admission/authority.py` cannot act as issuer. None of this is overridden by historical replay.

## Separate owner decisions before real deployment

1. **Signer custody:** where will the owner keep and recover the *real* Ed25519 signing key? Select a separate trust domain, recovery, rotation and revocation. The owner must personally approve any real key creation; no key is generated here.
2. **Independent verifier runtime:** approve separate repository/hosting account, verifier App identity, GitHub `Contents:read`, `Pull requests:read`, `Checks:read+write` as specifically necessary, `Administration:read` only if needed, Vercel read-only source, budget and operational on-call. Do not give candidate branch the App private key or config access.
3. **Replay ledger custody:** deploy a separate authoritative CAS ledger with authenticated issuance and exact payload commitment; determine scope, TTL, retention and recovery. Test SQLite code in this package is not production storage.
4. **Ruleset/protection enforcement:** with fresh owner settings readback, add *one* required `owner-admission` status pinned to that dedicated App. Preserve classic main protection; no direct push, bypass, force push or deletion. Must prove source-ID constraint actually enforces. Separate explicit provider-admin mutation approval required.
5. **CI ambiguity:** current required job names `static-release`, `language-parity` appear on `push` and `pull_request`. Define unique identities/event handling and test that real GitHub required status is unambiguous. Do not change workflows without isolated PR approval.
6. **Preview policy:** prior coordination required GitHub CI plus both Vercel previews. Decide whether source-only PR #226 must still have both `READY` previews, or explicitly version and approve an exception. **No implicit waiver**.
7. **New coordination gate:** old lease has expired. Prior owner approval cannot be reused. Get exact main/head/tree/PR check sources, scope and expiry before any write.
8. **High-impact actions:** mark-ready, merge, release/publish each require a *different* bounded owner approval, JIT and execution gate. R4F7F does not approve any of them.

## Safe terminal state of R4F7F

`R4F7F_LOCAL_TESTED / AUTHORITY_UNIMPLEMENTED / PROVIDER_ENFORCEMENT_UNCHANGED / MERGE_HOLD / PUBLICATION_HOLD / HOST_RESOURCE_HOLD`.
