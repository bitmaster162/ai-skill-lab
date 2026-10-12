# R4F7K — Synthetic owner-admission integration into AI Skill Lab

**Source-only test fixture**, imported byte-for-byte from the offline R4F7H bundle (32 files), except this added R4F7K integration README. All original R4F7H bytes remain unchanged. The original nested `R4F7H_SOURCE_SHA256_MANIFEST_20261012.json` retains its original historical scope.

Source repo: `bitmaster162/ai-skill-lab`, proposed parent main commit `0ab438a2568e562603b707c377c91bee1c836a8a`, tree `7eaced40ab4b21c621d37b072d1558343574a801`. These SHA values are the **provider read-only baseline** and must be revalidated before writing. This portable patch was NOT produced from a full checkout of main: direct network Git cloning is unavailable in the current ChatGPT container.

The `owner_admission/merge_v2_provider_port.py` real I/O adapter remains disabled and fails closed. No owner private key, public-key trust root, installed GitHub App, independent nonce-ledger, real check publisher, trusted merge executor or production-publish authority is created or claimed.

Run local tests from the repository root with Python 3.13 and cryptography==46.0.4:

```bash
python -I -B tools/owner_admission_offline/run_tests.py
```

The added `.github/workflows/owner-admission-offline.yml` runs the same isolated tests with `contents:read`, no write permissions or secrets, and a **nonrequired, unique check name**. It is intended to be introduced only in a separately approved PR; tests prove CI portability, not merge authorization.

**CI policy hold:** current `scripts/check_preflight_safety.py` pins exactly 5 workflows. The new workflow makes 6; the accompanying patch under `policy_review_only/` changes only 5→6 (two lines). That protected QA-policy modification requires explicit owner approval before any remote GitHub write. Existing `static-release`, `language-parity`, `CodeQL` settings and workflows must remain unchanged.

No `pull_request_target`, `workflow_run`, branch-protection edits, required-check edits, PR #226 edits, push, deployment, real nonce issuance, or merge is permitted by this source-only candidate.

For the original full test suite and detailed architecture, see `README_R4F7H.md`, `docs/R4F7H_SECURITY_CONTRACT.md` and `docs/R4F7H_TEST_MATRIX.md`.
