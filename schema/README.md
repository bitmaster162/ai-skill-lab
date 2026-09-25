# Captured lead-intake schema

`lead_intake_r101b.sql` is the observed D1 table definition, not a production migration.

## Provenance

- Database: `ai-skill-lab-leads-r101b` / `1de9ec7f-5d92-4edd-a069-ec5296b54b82`.
- Captured on 2026-09-25 at 22:26 UTC through Wrangler 4.129.0.
- Repository baseline: `3c780ac12cdf31350c47953da906b8623c52d7e7`.
- Read-only query: `SELECT type, name, tbl_name, sql FROM sqlite_master WHERE (type='table' AND name='lead_intake_r101b') OR (type IN ('index','trigger') AND tbl_name='lead_intake_r101b') ORDER BY type, name;`
- Provider result: `success=true`, `rows_written=0`, `changed_db=false`.
- Result: one table and its implicit primary-key index; no other table indexes or triggers returned.
- SQL text is preserved from `sqlite_master.sql`, with only a terminating semicolon and LF added.
- SQL file: 874 bytes; SHA-256 `8d0c8f0f18c63a36b2602c7c323dda985860230ac9b7bc536c541ea347213e44`.
- No lead rows, credentials, or secret values were retrieved or included.

## Scope and verification

Run `python scripts/check_lead_schema.py` from the repository root. The check uses only SQLite `:memory:` and synthetic records; it performs no network calls or remote database writes.

It checks the captured constraints, the receiver's actual INSERT/deduplication and cleanup SQL, and the operator inbox's SELECT projections. SQL `length()` constraints count characters; the ingress and receiver also impose separate UTF-8 byte limits. These are not claimed to be equivalent.

This snapshot is not a data backup, migration history, or proof of live delivery, retention execution, or disaster recovery. It does not modify or normalize existing production constraints. Do not apply it to the existing production database. Any future migration needs its own evidence, compatibility review, and approval.

CI and release preflight run the offline check. Changing the captured SQL requires a new, independently obtained schema readback and fingerprint.
