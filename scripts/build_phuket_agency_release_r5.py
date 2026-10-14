#!/usr/bin/env python3
"""Reproduce R5 locally from immutable R3 and the unchanged R4 public copy.

Read-only by default. Only a new, isolated Draft may be prepared; existing
RC payloads are never rewritten under the same release identity.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import prepare_phuket_agency_terms_r4 as previous

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / 'deploy/live'
RELEASE = 'PHUKET_UNIVERSE_U1_AGENCY_TERMS_R5_20261014'
BRANCH = 'agent/phuket-universe-agency-terms-integration-local-r1'
PROFILE_PATH = ROOT / 'data/phuket_universe_agency_terms_r5_profile.json'
R4_MANIFEST = '434d18bc0162f8fecf3402de7f65b00d53f95011a8b249db92667e39b564ae1b'
PAYLOAD_SHA = 'e8b41c9e6fed3e6b1f2b9edf66e1ddd227c4253fd1cb70c7030265dba1c63726'


def render() -> dict[str, bytes]:
    files, stats = previous.render()
    if stats['manifest_sha256'] != R4_MANIFEST or stats['payload_sha256'] != PAYLOAD_SHA:
        raise ValueError('R4 source/copy payload drift')
    manifest = json.loads(files['_release.json'])
    manifest['release_id'] = RELEASE
    files['_release.json'] = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode('utf-8')
    previous.verify_payload(files)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-local', action='store_true')
    args = parser.parse_args()
    files = render()
    if args.prepare_local:
        profile = json.loads(PROFILE_PATH.read_text(encoding='utf-8'))
        current = json.loads((LIVE / '_release.json').read_text(encoding='utf-8'))
        if previous.git('branch', '--show-current').decode().strip() != BRANCH:
            raise ValueError('Not the isolated R5 branch')
        if profile.get('status') != 'Draft' or any(profile.get('authority', {}).values()):
            raise ValueError('Draft-only preparation denied')
        if current.get('release_id') != 'PHUKET_UNIVERSE_U1_STATIC_R3_20261014':
            raise ValueError('No overwrite/reseal: preparation requires untouched R3')
        old = previous.r3_payload()
        actual = {p.relative_to(LIVE).as_posix(): p.read_bytes() for p in LIVE.rglob('*') if p.is_file()}
        if actual != old:
            raise ValueError('R3 write baseline drift')
        for name, data in sorted(files.items(), key=lambda row: row[0] == '_release.json'):
            target = LIVE / name
            if target.is_symlink() or not target.resolve().is_relative_to(LIVE.resolve()):
                raise ValueError('Unsafe write target')
            if target.read_bytes() != data:
                target.write_bytes(data)
    actual = {p.relative_to(LIVE).as_posix(): p.read_bytes() for p in LIVE.rglob('*') if p.is_file()}
    if actual != files:
        raise ValueError('R5 reproduction mismatch')
    print('PHUKET_R5_REPRODUCTION_PASS files=' + str(len(files)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
