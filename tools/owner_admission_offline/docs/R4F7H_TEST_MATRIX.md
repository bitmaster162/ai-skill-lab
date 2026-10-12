# R4F7H — bounded negative and positive test matrix

**Run:** `python -I -B run_tests.py` from an isolated clean checkout. The original R4F7F test runner and all original R4F7F files are byte-identical to the verified parent commit. All test data are fake; the signed digest and SHA strings refer to selected historical paths but mock CI, previews, lease, public key, private key and ledger are synthetic.

| Scope | Cases |
|---|---|
| v1/v2 separation | `MARK_READY_ONLY` payload/signature/nonce cannot satisfy `MERGE_ONLY`, distinct Ed25519 domain, exact v2 schema and merge method |
| Denied capabilities | `mark_ready`, `deploy`, `production_publish`, `auto_merge`, `force_push`, `delete`, `squash`, `rebase`; no GitHub check publisher, token or network |
| Owner root | pinned mock public key, registry version, revocation, wrong signature, wrong domain, unknown signer, malformed hex/UTF-8, typed strict fields |
| SHA+target | exact repo/PR/branch/base/head commit and tree, path inventory/digest, raw patch/evidence hashes, no extra files |
| Time/freshness | UTC format, lifetime policy, issued-in-future, expiry, changed provider time; **expired despite green merge check** |
| Provider+CI | protected main rule, no bypass/force/deletion, normal merge, three distinct CI sources, duplicate `push`/`pull_request` contexts, neutral/skipped/failed checks, required pinned independent merge check |
| Preview+lease | two exact READY previews, expired or wrong scope/coordination/head lease, draft/closed/unmergeable PR |
| Merge check JIT | correct App ID + context + external payload digest + HEAD + completion time, missing/wrong/duplicate/stale successful check, source drift |
| Ledger | preissue for exact payload only, replay, unissued, cross-action nonce reuse, consumed readback, schema/identity corruption, symlink, absent DB, concurrent consumers, corrupt DB, invalid restore state |
| Stop boundaries | production audience HOLD, authenticated provider port remains disabled, status cannot emit/authorize check, action or deploy |

**Acceptance:** Both R4F7F (88 previously accepted tests) and new R4F7H regression tests pass on a fresh ZIP extraction and bundle restore, with zero exceptions. Record observed counts and branch-aware coverage in a separate evidence receipt, never presume counts from this document. The required production owner trust root, real provider adapter and effect-bearing executor are **not** included.
