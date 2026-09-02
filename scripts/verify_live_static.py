#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

CONFIG_NAME = "vercel.json"
SECURITY_HEADERS = {
    "x-content-type-options": "nosniff",
    "referrer-policy": "strict-origin-when-cross-origin",
    "x-frame-options": "DENY",
    "permissions-policy": "camera=(), microphone=(), geolocation=()",
}
ALLOWED_EXACT_HOSTS = {"ai-skill-lab.vercel.app"}
ALLOWED_HOST_SUFFIXES = ("-bitevo-s-projects.vercel.app",)


def validate_target_url(url: str, *, require_root: bool = False) -> str:
    parsed = urlsplit(url)
    if parsed.scheme != "https":
        raise ValueError("target must use https")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("target must not contain credentials")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("target contains an invalid port") from exc
    if port not in (None, 443):
        raise ValueError("target must use the default HTTPS port")
    host = (parsed.hostname or "").rstrip(".").casefold()
    if not host:
        raise ValueError("target host is missing")
    if not (
        host in ALLOWED_EXACT_HOSTS
        or any(host.endswith(suffix) for suffix in ALLOWED_HOST_SUFFIXES)
    ):
        raise ValueError(f"target host is not allowlisted: {host}")
    if parsed.query or parsed.fragment:
        raise ValueError("target must not contain query or fragment")
    if require_root and parsed.path not in ("", "/"):
        raise ValueError("base URL must point to the deployment root")
    return url


class SafeRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        try:
            validate_target_url(newurl)
        except ValueError as exc:
            raise HTTPError(
                newurl,
                code,
                f"unsafe redirect target: {exc}",
                headers,
                fp,
            ) from exc
        return super().redirect_request(req, fp, code, msg, headers, newurl)


OPENER = build_opener(SafeRedirectHandler())


def web_path(rel: str) -> str | None:
    if rel == CONFIG_NAME or rel == "404.html":
        return None
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[:-11]
    if rel.endswith(".html"):
        return "/" + rel[:-5]
    return "/" + rel


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str):
    validate_target_url(url)
    req = Request(
        url,
        headers={
            "User-Agent": "ai-skill-lab-release-verifier/2",
            "Accept-Encoding": "identity",
        },
    )
    with OPENER.open(req, timeout=20) as response:
        return (
            response.status,
            {key.lower(): value for key, value in response.headers.items()},
            response.read(),
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify an allowlisted live static deployment against local release bytes."
    )
    parser.add_argument("--local-dir", required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--check-security-headers", action="store_true")
    parser.add_argument("--expect-release-id")
    args = parser.parse_args()

    local = Path(args.local_dir).resolve()
    if not local.is_dir():
        print(f"FAIL: local dir not found: {local}")
        return 2

    try:
        base = validate_target_url(args.base_url, require_root=True).rstrip("/") + "/"
    except ValueError as exc:
        print(f"FAIL: unsafe base URL: {exc}")
        return 2

    problems = []
    checked = 0
    files = sorted(
        (path for path in local.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(local).as_posix(),
    )
    for path in files:
        rel = path.relative_to(local).as_posix()
        web = web_path(rel)
        if web is None:
            continue
        url = urljoin(base, web.lstrip("/")) if web != "/" else base
        try:
            status, headers, body = fetch(url)
        except HTTPError as exc:
            problems.append(f"{web}: HTTP {exc.code}")
            continue
        except (URLError, ValueError) as exc:
            problems.append(f"{web}: fetch error {exc}")
            continue
        checked += 1
        expected = path.read_bytes()
        if status != 200:
            problems.append(f"{web}: status {status} != 200")
        if body != expected:
            problems.append(
                f"{web}: byte mismatch live={sha256(body)} local={sha256(expected)} "
                f"live_size={len(body)} local_size={len(expected)}"
            )
        if args.check_security_headers and web == "/":
            for key, value in SECURITY_HEADERS.items():
                if headers.get(key) != value:
                    problems.append(
                        f"/: header {key}={headers.get(key)!r} != {value!r}"
                    )

    sentinel = urljoin(base, "__ai_skill_lab_missing_readback__")
    try:
        status, _, _ = fetch(sentinel)
        problems.append(f"404 sentinel unexpectedly returned {status}")
    except HTTPError as exc:
        if exc.code != 404:
            problems.append(f"404 sentinel returned HTTP {exc.code}")
    except (URLError, ValueError) as exc:
        problems.append(f"404 sentinel fetch error {exc}")

    if args.expect_release_id:
        release = local / "_release.json"
        if not release.exists():
            problems.append("expected release id but local _release.json is absent")
        else:
            obj = json.loads(release.read_text(encoding="utf-8"))
            if obj.get("release_id") != args.expect_release_id:
                problems.append(
                    f"local release_id {obj.get('release_id')!r} != "
                    f"{args.expect_release_id!r}"
                )

    print(
        f"live_files_checked={checked} local_files={len(files)} base_url={base}"
    )
    if problems:
        for problem in problems:
            print("FAIL:", problem)
        return 1
    print("LIVE_STATIC_READBACK_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
