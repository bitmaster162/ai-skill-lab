#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RECEIVER_DIR = ROOT / "services" / "lead-receiver-cloudflare"
WRANGLER = RECEIVER_DIR / "node_modules" / "wrangler" / "bin" / "wrangler.js"
DB_NAME = "ai-skill-lab-leads-r101b"
TABLE = "lead_intake_r101b"
UUID_V4 = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I)
FORBIDDEN_SQL = re.compile(r"\b(?:insert|update|delete|replace|alter|drop|create|attach|detach|pragma|vacuum)\b", re.I)

LIST_FIELDS = (
    "request_id, received_at, expires_at, audience, locale, "
    "program, source, source_path"
)
SHOW_FIELDS = (
    "request_id, received_at, expires_at, schema, name, audience, contact, goal, "
    "program, locale, privacy_consent, adult_confirmed, source, source_path"
)
def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def assert_read_only_sql(sql: str) -> None:
    normalized = sql.strip()
    if not normalized.lower().startswith("select "):
        raise ValueError("operator inbox permits SELECT only")
    if normalized.count(";") > 1 or (";" in normalized[:-1]):
        raise ValueError("multiple SQL statements are forbidden")
    if FORBIDDEN_SQL.search(normalized):
        raise ValueError("mutating or privileged SQL keyword is forbidden")


def build_list_sql(limit: int, since_hours: int) -> str:
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    if not 1 <= since_hours <= 720:
        raise ValueError("since-hours must be between 1 and 720")
    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    cutoff_iso = cutoff.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    sql = (
        f"SELECT {LIST_FIELDS} FROM {TABLE} "
        f"WHERE received_at >= {sql_literal(cutoff_iso)} "
        f"ORDER BY received_at DESC LIMIT {limit};"
    )
    assert_read_only_sql(sql)
    return sql

def build_show_sql(request_id: str) -> str:
    if not UUID_V4.fullmatch(request_id):
        raise ValueError("request-id must be UUIDv4")
    sql = (
        f"SELECT {SHOW_FIELDS} FROM {TABLE} "
        f"WHERE request_id = {sql_literal(request_id)} LIMIT 2;"
    )
    assert_read_only_sql(sql)
    return sql


def run_d1(sql: str) -> list[dict]:
    assert_read_only_sql(sql)
    if not WRANGLER.exists():
        raise RuntimeError(
            "Wrangler is not installed under services/lead-receiver-cloudflare; run npm install there first"
        )
    proc = subprocess.run(
        [
            "node", str(WRANGLER), "d1", "execute", DB_NAME,
            "--remote", "--command", sql, "--json",
        ],
        cwd=RECEIVER_DIR,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError("D1 read failed")
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("D1 returned non-JSON output") from exc
    if not isinstance(payload, list) or len(payload) != 1 or not payload[0].get("success"):
        raise RuntimeError("D1 read result is invalid")
    rows = payload[0].get("results")
    if not isinstance(rows, list):
        raise RuntimeError("D1 read result has no rows list")
    return rows


def print_list(rows: list[dict], as_json: bool) -> None:
    if as_json:
        print(json.dumps(rows, ensure_ascii=False, sort_keys=True, indent=2))
        return
    if not rows:
        print("No recent leads found.")
        return
    print("request_id\treceived_at\taudience\tlocale\tprogram\tsource_path")
    for row in rows:
        values = [
            row.get("request_id", ""), row.get("received_at", ""),
            row.get("audience", ""), row.get("locale", ""),
            row.get("program", ""), row.get("source_path", "") or "",
        ]
        print("\t".join(str(value) for value in values))

def print_show(rows: list[dict], as_json: bool) -> None:
    if len(rows) > 1:
        raise RuntimeError("request-id lookup returned multiple rows")
    if not rows:
        print("Lead not found.")
        return
    row = rows[0]
    if as_json:
        print(json.dumps(row, ensure_ascii=False, sort_keys=True, indent=2))
        return
    for key in [
        "request_id", "received_at", "expires_at", "schema", "name", "audience",
        "contact", "goal", "program", "locale", "privacy_consent",
        "adult_confirmed", "source", "source_path",
    ]:
        print(f"{key}: {row.get(key, '')}")


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Read-only operator inbox for AI Skill Lab production leads."
    )
    sub = ap.add_subparsers(dest="command", required=True)
    lp = sub.add_parser("list", help="List recent lead metadata without name/contact/goal")
    lp.add_argument("--limit", type=int, default=20)
    lp.add_argument("--since-hours", type=int, default=168)
    lp.add_argument("--json", action="store_true")
    sp = sub.add_parser("show", help="Show one exact lead, including submitted contact/goal")
    sp.add_argument("request_id")
    sp.add_argument("--json", action="store_true")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "list":
            rows = run_d1(build_list_sql(args.limit, args.since_hours))
            print_list(rows, args.json)
            return 0
        if args.command == "show":
            rows = run_d1(build_show_sql(args.request_id))
            print_show(rows, args.json)
            return 0
        raise RuntimeError("unknown command")
    except (ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"lead-inbox error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
