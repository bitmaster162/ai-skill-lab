# D1 recovery runbook

This runbook covers recovery evidence for the AI Skill Lab lead database only.

Database identity:

- name: `ai-skill-lab-leads-r101b`
- database ID: `1de9ec7f-5d92-4edd-a069-ec5296b54b82`
- schema reference: `schema/lead_intake_r101b.sql`

The schema file is not a data backup. A successful schema check does not prove that lead rows can be restored.

## Observed recovery capability

On 2026-09-25 UTC, Wrangler 4.129.0 successfully returned a current Time Travel bookmark for this database.

The same read-only command also returned a bookmark for `2026-09-08T00:00:00Z`.

No restore was executed. No lead rows were read. The schema-capture query reported `rows_written=0` and `changed_db=false`.

Current Wrangler help states that timestamp-based Time Travel restore targets must be within the last 30 days. Treat that as provider/runtime behavior to re-check at incident time, not as a permanent repository guarantee.

## Read-only incident preflight

Start from a clean operator shell and verify the exact database before doing anything destructive:

```powershell
npx wrangler@4.129.0 d1 info ai-skill-lab-leads-r101b
npx wrangler@4.129.0 d1 time-travel info ai-skill-lab-leads-r101b --json
```
For a candidate recovery timestamp, resolve a bookmark without restoring:

```powershell
npx wrangler@4.129.0 d1 time-travel info ai-skill-lab-leads-r101b --timestamp "<RFC3339_TIMESTAMP>" --json
```

Record before approval:

- current UTC time;
- incident reason and evidence;
- exact database name and ID;
- current bookmark;
- target timestamp and resolved target bookmark;
- current repository `main` SHA;
- current schema SHA-256;
- intended verification steps.

If the timestamp cannot be resolved to a bookmark, stop. Do not substitute a nearby timestamp without a new decision.

## Restore approval gate

A Time Travel restore is a production database mutation.

Do not run a restore from CI, release preflight, scheduled automation, or an agent-generated command without separate explicit owner approval.

Approval must bind the exact database ID and the exact target bookmark or timestamp. A general release approval does not authorize a database restore.

Before any approved restore, establish a verified write-freeze method for the intake path. This repository does not currently claim that a write-freeze mechanism has been tested as part of disaster recovery.

The Wrangler mutation surface currently exposed is:

```text
wrangler d1 time-travel restore <database> --bookmark <BOOKMARK>
wrangler d1 time-travel restore <database> --timestamp <RFC3339_TIMESTAMP>
```
Those commands are documented mutation surfaces, not pre-approved instructions.

## Post-restore verification

After an explicitly approved restore:

1. Re-read D1 database identity.
2. Capture a fresh current Time Travel bookmark.
3. Re-read `sqlite_master` for `lead_intake_r101b` and compare the table definition to the repository schema reference.
4. Verify the intake receiver configuration and rate-limit binding before reopening writes.
5. Verify application health independently; a successful database restore does not prove ingress, notification, or public-form health.
6. Keep row-level inspection minimal. Do not expose lead PII unless the incident scope requires it.

Do not replay form submissions automatically. Do not synthesize missing leads. Do not infer restored row correctness from schema parity alone.

## Boundaries

This runbook does not:

- create a backup;
- export production lead data;
- authorize a restore;
- prove the scheduled retention job has executed;
- prove a complete disaster-recovery exercise;
- change Cloudflare, Vercel, or production configuration.

A real recovery drill that mutates production requires a separate plan, explicit approval, and fresh evidence.
