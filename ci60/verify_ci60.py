"""Review only: verify one specified local ZIP with the unchanged release validator.
Usage: python -B verify_ci60.py REPO ARTIFACT.zip [--temp RUNNER_TEMP]
No repository edits, notifications, provider credentials or network access required.
"""
import argparse
from contextlib import redirect_stdout
from hashlib import sha256
from io import BytesIO, StringIO
import json
from pathlib import Path, PurePosixPath
import re
import runpy
import shutil
import socket
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch
from xml.etree import ElementTree
from zipfile import ZipFile

HEAD = 'a1b776f59d609a99b1ca162ade3aabdf72745a1b'
ARCHIVE = 'a679d18882b161a12afd410369e68f042e893153198146d03696f5741f32937b'
MANIFEST = '01b68a85993c20f34614816df735e33af3c0636f4a787386a037fa453e671926'
PARENT = '767936df52b6b4dc6c7420e00530afa91ddd9485ee696c3f45dc16522858855a'
PAYLOAD = '9b5e13d9441e8716cd9306e4ab10d77c35ddfe303b17bb1aba70997624f26425'
RELEASE = 'AISL_R2_NOJS_P2P3_LOCAL_REVIEW_'+PAYLOAD

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def sha(b):
    return sha256(b).hexdigest()

def room(temp):
    locations = [Path('C:/'),Path('D:/')] if sys.platform=='win32' else [temp]
    require(all(shutil.disk_usage(p).free > 4*1024**3+8*1024**2 for p in locations), 'free space threshold')

def reject(fn, reason):
    try:
        fn()
    except (ValueError, RuntimeError) as e:
        require(reason in str(e), 'unexpected rejection '+str(e))
        return str(e)
    raise AssertionError('expected rejection: '+reason)

def main():
    import tempfile
    args=argparse.ArgumentParser(description=__doc__)
    args.add_argument('repo',type=Path)
    args.add_argument('zip',type=Path)
    args.add_argument('--temp',type=Path,default=Path(tempfile.gettempdir()))
    options=args.parse_args()
    require(__debug__ and sys.dont_write_bytecode,'run python -B')
    repo=options.repo.resolve(strict=True)
    artifact=options.zip.resolve(strict=True)
    scratch_root=options.temp.resolve(strict=True)
    require(scratch_root!=repo and repo not in scratch_root.parents, 'scratch must be outside source repository')
    room(scratch_root)
    git=lambda *args: subprocess.check_output(['git','--no-optional-locks','-C',str(repo),*args])
    discover=lambda: (git('rev-parse','HEAD').decode().strip(), git('status','--porcelain=v1','--untracked-files=all'))
    require(Path(git('rev-parse','--show-toplevel').decode().strip()).resolve()==repo and discover()==(HEAD,b''),'unrecognized source checkout')
    require(artifact.stat().st_size==685589, 'unexpected size')
    buf=artifact.read_bytes()
    require(sha(buf)==ARCHIVE,'ZIP SHA mismatch')
    with ZipFile(BytesIO(buf)) as z:
        names=z.namelist()
        require(len(names)==len(set(n.casefold() for n in names))==119 and z.testzip() is None,'ZIP structure and CRC')
        require(all(not PurePosixPath(n).is_absolute() and '\\' not in n and ':' not in n and '..' not in PurePosixPath(n).parts and not n.endswith('/') for n in names),'unsafe name')
        raw=z.read('_release.json')
        require(sha(raw)==MANIFEST,'unexpected manifest SHA')
        assets={n:z.read(n) for n in names if n!='_release.json'}
    manifest=json.loads(raw)
    require((manifest['release_id'],manifest['payload_sha256'],manifest['parent_manifest_sha256'])==(RELEASE,PAYLOAD,PARENT),'wrong release identity')
    # Reconstruct the CI inputs from Git objects at the pinned commit. This does
    # not import Python modules from the candidate artifact or publish the archive.
    tracked=git('archive','--format=zip',HEAD,'scripts','.github/workflows/indexnow.yml','public')
    with TemporaryDirectory(prefix='aisl-ci60-',dir=scratch_root) as scratch:
        stage=Path(scratch); live=stage/'deploy/live'
        scripts=stage/'scripts'
        with ZipFile(BytesIO(tracked)) as src:
            for n in src.namelist():
                simple_public_key=bool(re.fullmatch(r'public/[0-9a-f-]{36}\.txt',n))
                if (n.startswith('scripts/') and n.endswith('.py')) or n=='.github/workflows/indexnow.yml' or simple_public_key:
                    dest=stage/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(src.read(n))
        for n, value in {**assets,'_release.json':raw}.items():
            dest=live/PurePosixPath(n);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(value)
        sys.path.insert(0,str(scripts))
        try:
            import guide_route_admission as gate
            from prepare_phuket_universe_static_r1 import verify_manifest
            verified=verify_manifest(assets,raw)
            require(verified['file_count']==118,'file count')
            checkpoint=dict(gate.PILOT_ROUTE_MANIFESTS)
            require(len(checkpoint)==3 and RELEASE not in checkpoint, 'unexpected baseline registry')
            require(gate.pilot_snapshot_routes(live) is None and len(gate.admitted_routes())==52,'baseline registry already admits candidate')
            urls=[node.text for node in ElementTree.fromstring(assets['sitemap.xml']).findall('{*}url/{*}loc')]
            require(len(urls)==len(set(urls))==60,'sitemap count')
            llms=re.findall(r'\]\((https://[^)]+)\)',assets['llms.txt'].decode())
            def check_native():
                output=StringIO()
                with redirect_stdout(output):
                    runpy.run_path(str(scripts/'check_indexnow.py'),run_name='__main__')
                return output.getvalue().strip()
            with patch.object(socket.socket,'connect',side_effect=RuntimeError('network disabled')), patch.object(socket,'getaddrinfo',side_effect=RuntimeError('DNS disabled')):
                before=reject(check_native,'unexpected=')
                with patch.dict(gate.PILOT_ROUTE_MANIFESTS,{RELEASE:MANIFEST}):
                    require({k:v for k,v in gate.PILOT_ROUTE_MANIFESTS.items() if k!=RELEASE}==checkpoint, 'prior registry entries changed')
                    accepted=gate.pilot_snapshot_routes(live)
                    require(isinstance(accepted,frozenset) and len(accepted)==60, 'pinned input failed')
                    result=check_native()
                    require('sitemap_urls=60' in result and 'INDEXNOW_CONTRACT_PASS' in result, 'native contract failed')
                    require(gate.require_canonical_urls(urls)==gate.require_canonical_urls(llms)==gate.require_public_html(live)==60,'policy consistency')
                    extra=sorted(accepted-gate.BASELINE_ROUTES)
                    wrong_digest=reject(lambda:gate.require_canonical_urls(urls+urls[-1:]),'duplicate')
                    with patch.dict(gate.PILOT_ROUTE_MANIFESTS,{RELEASE:PARENT}):
                        wrong_pair=reject(lambda:gate.pilot_snapshot_routes(live),'digest mismatch')
                    file=live/'business.html'
                    try:
                        file.write_bytes(assets['business.html']+b'\n')
                        wrong_payload=reject(lambda:gate.pilot_snapshot_routes(live),'Payload bytes differ')
                    finally:
                        file.write_bytes(assets['business.html'])
                    for name, value in assets.items():
                        require((live/name).read_bytes()==value,'restored scratch bytes')
                require(gate.PILOT_ROUTE_MANIFESTS==checkpoint and gate.pilot_snapshot_routes(live) is None,'registry not restored')
        finally:
            sys.path.remove(str(scripts))
    require(discover()==(HEAD,b'') and sha(artifact.read_bytes())==ARCHIVE,'source or artifact changed')
    return {'status':'OFFLINE_EXACT_ZIP_ROUTE_QA_PASS','zip_sha256':ARCHIVE,'zip_bytes':len(buf),'release_id':RELEASE,'manifest_sha256':MANIFEST,'payload_sha256':PAYLOAD,'parent_manifest_sha256':PARENT,'git_head':HEAD,'repo':str(repo),'artifact':str(artifact),'payload_verified':len(assets),'unmodified_gate_count':52,'unmodified_contract_result':before,'exact_process_only_pin':result,'sitemap_unique':len(set(urls)),'public_html_routes':len(accepted),'llms_unique':len(set(llms)),'extra_routes':extra,'wrong_manifest':wrong_pair,'changed_payload':wrong_payload,'duplicate_url':wrong_digest,'existing_registry_unchanged':checkpoint==gate.PILOT_ROUTE_MANIFESTS,'working_tree_clean_before_and_after':True,'provider_ci_runs_started':0,'deployments':0,'indexnow_submissions':0}
if __name__=='__main__':
    print(json.dumps(main(),ensure_ascii=False,indent=2))
