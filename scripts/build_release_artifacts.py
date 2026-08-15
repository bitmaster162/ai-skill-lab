#!/usr/bin/env python3
from __future__ import annotations
import argparse, base64, hashlib, io, json, lzma, os, shutil, subprocess, tarfile, tempfile, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LIVE=ROOT/'deploy'/'live'
EPOCH=(2026,8,15,0,0,0)
CHUNK=7000

def sha256(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def file_sha(p:Path)->str: return sha256(p.read_bytes())

def normalized_tar(paths:list[Path])->bytes:
    buf=io.BytesIO()
    with tarfile.open(fileobj=buf,mode='w',format=tarfile.PAX_FORMAT) as tf:
        for p in paths:
            rel=p.relative_to(LIVE).as_posix()
            data=p.read_bytes()
            ti=tarfile.TarInfo(rel)
            ti.size=len(data); ti.mode=0o644; ti.uid=0; ti.gid=0; ti.uname=''; ti.gname=''; ti.mtime=0
            tf.addfile(ti,io.BytesIO(data))
    return buf.getvalue()

def deterministic_zip(path:Path, files:dict[str,bytes])->None:
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(files):
            info=zipfile.ZipInfo(name); info.date_time=EPOCH; info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16
            z.writestr(info,files[name])

def build(release:str,outdir:Path)->dict:
    manifest=json.loads((LIVE/'_release.json').read_text(encoding='utf-8'))
    if manifest.get('release_id')!=release: raise RuntimeError(f'_release.json release_id={manifest.get("release_id")} expected={release}')
    paths=sorted([p for p in LIVE.rglob('*') if p.is_file()],key=lambda p:p.relative_to(LIVE).as_posix())
    if len(paths)!=manifest['file_count']+1: raise RuntimeError(f'file count mismatch live={len(paths)} manifest+release={manifest["file_count"]+1}')
    tar_raw=normalized_tar(paths)
    tar_xz=lzma.compress(tar_raw,format=lzma.FORMAT_XZ,preset=9|lzma.PRESET_EXTREME)
    archive_sha=sha256(tar_xz); payload_sha=manifest['payload_sha256']
    outdir.mkdir(parents=True,exist_ok=True)
    static_path=outdir/f'AI_SKILL_LAB_{release}_STATIC.tar.xz'; static_path.write_bytes(tar_xz)
    ready_path=outdir/f'AI_SKILL_LAB_{release}_VERCEL_READY.zip'
    deterministic_zip(ready_path,{p.relative_to(LIVE).as_posix():p.read_bytes() for p in paths})
    # Manifest SHA list includes the 44 payload files and _release.json itself.
    lines=[]
    for p in paths:
        rel=p.relative_to(LIVE).as_posix(); lines.append(f'{file_sha(p)}  {rel}\n')
    manifest_sha=''.join(lines).encode()
    tag=release.lower()
    b64=base64.b64encode(tar_xz).decode('ascii')
    chunks=[b64[i:i+CHUNK].encode() for i in range(0,len(b64),CHUNK)]
    build_sh=f'''#!/usr/bin/env bash\nset -euo pipefail\necho {release}_TRANSPORT_START\ncat {tag}_[0-9][0-9] > payload.b64\nbase64 -d payload.b64 > {tag}.tar.xz\necho "{archive_sha}  {tag}.tar.xz" | sha256sum -c -\n[ "$(stat -c%s {tag}.tar.xz)" = "{len(tar_xz)}" ]\nrm -rf stage out; mkdir -p stage out\ntar -xJf {tag}.tar.xz -C stage\n[ "$(find stage -type f | wc -l | tr -d ' ')" = "{len(paths)}" ]\n(cd stage && sha256sum -c ../{tag}_manifest.sha256)\ngrep -q '"release_id": "{release}"' stage/_release.json\ngrep -q '{payload_sha}' stage/_release.json\nfind stage -mindepth 1 -maxdepth 1 ! -name vercel.json -exec cp -a {{}} out/ \\;\n[ "$(find out -type f | wc -l | tr -d ' ')" = "{len(paths)-1}" ]\necho {release}_TRANSPORT_PASS stage_files={len(paths)} output_files={len(paths)-1} payload_sha={payload_sha}\n'''.encode()
    wrapper_files={'build.sh':build_sh,'vercel.json':(LIVE/'vercel.json').read_bytes(),f'{tag}_manifest.sha256':manifest_sha}
    for i,c in enumerate(chunks): wrapper_files[f'{tag}_{i:02d}']=c
    wrapper_path=outdir/f'AI_SKILL_LAB_{release}_VERCEL_ASCII_WRAPPER.zip'
    deterministic_zip(wrapper_path,wrapper_files)
    return {'release':release,'payload_sha256':payload_sha,'live_files':len(paths),'served_files':len(paths)-1,'archive_sha256':archive_sha,'archive_size':len(tar_xz),'chunks':len(chunks),'paths':{'static':str(static_path),'ready':str(ready_path),'wrapper':str(wrapper_path)}}

def selftest(receipt:dict)->None:
    wrapper=Path(receipt['paths']['wrapper'])
    with tempfile.TemporaryDirectory(prefix='ai_skill_release_test_') as td:
        td=Path(td)
        with zipfile.ZipFile(wrapper) as z: z.extractall(td)
        os.chmod(td/'build.sh',0o755)
        p=subprocess.run(['bash','build.sh'],cwd=td,text=True,capture_output=True)
        if p.returncode!=0: raise RuntimeError('wrapper build failed\n'+p.stdout+'\n'+p.stderr)
        out=td/'out'
        expected=[p for p in LIVE.rglob('*') if p.is_file() and p.name!='vercel.json']
        if len(expected)!=receipt['served_files']: raise RuntimeError('expected served count mismatch')
        for src in expected:
            rel=src.relative_to(LIVE); dst=out/rel
            if not dst.exists(): raise RuntimeError(f'missing reconstructed {rel}')
            if src.read_bytes()!=dst.read_bytes(): raise RuntimeError(f'byte mismatch {rel}')
        extras=[p.relative_to(out) for p in out.rglob('*') if p.is_file() and not (LIVE/p.relative_to(out)).exists()]
        if extras: raise RuntimeError(f'extra reconstructed files: {extras}')
        print(p.stdout.strip())
        print(f'RELEASE_ARTIFACT_SELFTEST_PASS served_byte_match={len(expected)}/{len(expected)}')

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--release',required=True); ap.add_argument('--out-dir'); ap.add_argument('--receipt')
    args=ap.parse_args()
    if args.out_dir:
        out=Path(args.out_dir).resolve(); cleanup=None
    else:
        cleanup=tempfile.TemporaryDirectory(prefix='ai_skill_release_build_'); out=Path(cleanup.name)
    receipt=build(args.release,out); selftest(receipt)
    if args.receipt:
        rp=Path(args.receipt); rp.parent.mkdir(parents=True,exist_ok=True); rp.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(f'RELEASE_ARTIFACT_BUILDER_PASS release={args.release} live_files={receipt["live_files"]} chunks={receipt["chunks"]} archive_sha={receipt["archive_sha256"]}')
    if cleanup: cleanup.cleanup()
    return 0
if __name__=='__main__': raise SystemExit(main())
