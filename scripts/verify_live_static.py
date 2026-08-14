#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen
import argparse, hashlib, json, sys

CONFIG_NAME = 'vercel.json'
SECURITY_HEADERS = {
    'x-content-type-options': 'nosniff',
    'referrer-policy': 'strict-origin-when-cross-origin',
    'x-frame-options': 'DENY',
    'permissions-policy': 'camera=(), microphone=(), geolocation=()',
}

def web_path(rel: str) -> str | None:
    if rel == CONFIG_NAME or rel == '404.html':
        return None
    if rel == 'index.html':
        return '/'
    if rel.endswith('/index.html'):
        return '/' + rel[:-11]
    if rel.endswith('.html'):
        return '/' + rel[:-5]
    return '/' + rel

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def fetch(url: str):
    req=Request(url, headers={'User-Agent':'ai-skill-lab-release-verifier/1','Accept-Encoding':'identity'})
    with urlopen(req, timeout=20) as r:
        return r.status, {k.lower():v for k,v in r.headers.items()}, r.read()

def main() -> int:
    ap=argparse.ArgumentParser(description='Verify a live static deployment against local release bytes.')
    ap.add_argument('--local-dir', required=True)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--check-security-headers', action='store_true')
    ap.add_argument('--expect-release-id')
    args=ap.parse_args()

    local=Path(args.local_dir).resolve()
    if not local.is_dir():
        print(f'FAIL: local dir not found: {local}')
        return 2
    base=args.base_url.rstrip('/')+'/'
    problems=[]; checked=0
    files=sorted((p for p in local.rglob('*') if p.is_file()), key=lambda p:p.relative_to(local).as_posix())
    for p in files:
        rel=p.relative_to(local).as_posix(); path=web_path(rel)
        if path is None: continue
        url=urljoin(base, path.lstrip('/')) if path != '/' else base
        try:
            status,headers,body=fetch(url)
        except HTTPError as e:
            problems.append(f'{path}: HTTP {e.code}')
            continue
        except URLError as e:
            problems.append(f'{path}: fetch error {e.reason}')
            continue
        checked += 1
        expected=p.read_bytes()
        if status != 200:
            problems.append(f'{path}: status {status} != 200')
        if body != expected:
            problems.append(f'{path}: byte mismatch live={sha256(body)} local={sha256(expected)} live_size={len(body)} local_size={len(expected)}')
        if args.check_security_headers and path == '/':
            for key,value in SECURITY_HEADERS.items():
                if headers.get(key) != value:
                    problems.append(f'/: header {key}={headers.get(key)!r} != {value!r}')

    sentinel=urljoin(base,'__ai_skill_lab_missing_readback__')
    try:
        status,_,_=fetch(sentinel)
        problems.append(f'404 sentinel unexpectedly returned {status}')
    except HTTPError as e:
        if e.code != 404: problems.append(f'404 sentinel returned HTTP {e.code}')
    except URLError as e:
        problems.append(f'404 sentinel fetch error {e.reason}')

    if args.expect_release_id:
        release=local/'_release.json'
        if not release.exists():
            problems.append('expected release id but local _release.json is absent')
        else:
            obj=json.loads(release.read_text(encoding='utf-8'))
            if obj.get('release_id') != args.expect_release_id:
                problems.append(f"local release_id {obj.get('release_id')!r} != {args.expect_release_id!r}")

    print(f'live_files_checked={checked} local_files={len(files)} base_url={base}')
    if problems:
        for p in problems: print('FAIL:',p)
        return 1
    print('LIVE_STATIC_READBACK_PASS')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
