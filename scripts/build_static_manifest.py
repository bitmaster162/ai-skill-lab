#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[1]
LIVE = ROOT / 'deploy' / 'live'
OUT = LIVE / '_release.json'

def main() -> int:
    release_id = sys.argv[1] if len(sys.argv) > 1 else 'LOCAL'
    files=[]
    paths=sorted((p for p in LIVE.rglob('*') if p.is_file() and p != OUT), key=lambda p: p.relative_to(LIVE).as_posix())
    for p in paths:
        b=p.read_bytes()
        files.append({
            'path': p.relative_to(LIVE).as_posix(),
            'size': len(b),
            'sha256': hashlib.sha256(b).hexdigest(),
        })
    aggregate=''.join(f"{x['path']}\t{x['size']}\t{x['sha256']}\n" for x in files).encode()
    manifest={
        'schema':'ai-skill-lab.static-release.v1',
        'release_id':release_id,
        'file_count':len(files),
        'payload_sha256':hashlib.sha256(aggregate).hexdigest(),
        'files':files,
    }
    OUT.write_text(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(f"release_id={release_id} files={len(files)} payload_sha256={manifest['payload_sha256']}")
    return 0

if __name__ == '__main__': raise SystemExit(main())
