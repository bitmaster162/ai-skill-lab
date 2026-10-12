# R4F7F executable test matrix

Run: `python -I -B run_tests.py`. The suite uses ephemeral synthetic Ed25519 keys in RAM and disposable SQLite databases. No real account, API, private key or check-run is accessed.

| Deterministic area | Test coverage |
|---|---|
| Canonical encoding | deterministic serialization, duplicate JSON fields, JSON floats/NaN, malformed UTF-8, UTC strictness, size/depth checks |
| Signature and trust | unknown/revoked/wrong key, malformed signature, field/schema mismatch, no independent registry |
| Exact authority scope | only `MARK_READY_ONLY`, all effects false, wrong repo/PR/base/head/tree, wrong review mode, wrong policy |
| Integrity | tampered raw patch/evidence, changed-path inventory, duplicate paths, wrong digest |
| Provider status | missing/failing CI, wrong App/head/event, duplicate push+PR check names, forged candidate `owner-admission` |
| Branch enforcement | missing protection, bypass, force pushes, deletion, missing or wrong independently required App, normal merge compatibility |
| Preview and lease | both source-bound READY previews required; canceled/wrong/missing previews, expired/incorrect lease |
| Freshness | future/expired attestation, oversized owner-configured TTL, stale provider facts |
| CAS ledger | explicit test bootstrap, no implicit create, preregistered nonce commitment, unissued/replayed/mismatched nonce, schema corruption, two consumers |
| Capability confinement | production audience HOLD, no signer API, no network or subprocess imports, no credentials, no check publisher |

**Passing test ≠ permission.** The only positive code is `TEST_ONLY_PASS`, whose receipt explicitly has every production/merge/check publication flag set to false. A live source-derived owner approval remains unavailable.

## Mandatory blockers visible from current JIT

- `owner-admission` status not installed as a required check from an independently trusted App;
- no owner public-key registry in an external trust domain, no real signer;
- last coordination lease expired;
- GitHub context names `static-release` and `language-parity` duplicated between events (this pure gate holds such an input);
- both exact-HEAD Vercel previews not proven READY;
- `HOST_RESOURCE_HOLD`, `MERGE_HOLD`, `PUBLICATION_HOLD` remain in force.

For exact unittest names and actual observed counts, see `run_tests.py` output and the generated local test receipt. Test names must never be fabricated or used as substitutes for execution output.
