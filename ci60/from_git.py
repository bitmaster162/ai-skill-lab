"""Reproduce the upstream CI input at a pinned Git checkout, then replay the review QA.
Usage: python -B from_git.py SOURCE_CHECKOUT. Writes only to a temporary directory.
"""
from io import BytesIO
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZipFile

HERE=Path(__file__).resolve().parent
HEAD='a1b776f59d609a99b1ca162ade3aabdf72745a1b'
PUBLISHED='2444bd77f7616ba916c37b2b3bcba11898926be0'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo',type=Path)
    parser.add_argument('--windows-artifact-only',action='store_true',help='Allow the exact Windows symlink privilege failure only after verifying joint artifact bytes. Never for full CI.')
    options=parser.parse_args()
    if not sys.dont_write_bytecode or (options.windows_artifact_only and os.name!='nt'):
        raise ValueError('use python -B; artifact-only is a Windows diagnostic')
    repo=options.repo.resolve(strict=True)
    git=lambda *args: subprocess.check_output(['git','--no-optional-locks','-C',str(repo),*args])
    if git('rev-parse','HEAD').decode().strip()!=HEAD or git('status','--porcelain=v1','--untracked-files=all'):
        raise ValueError('expected separate clean checkout at the pinned source commit')
    temp=Path(os.environ.get('RUNNER_TEMP',tempfile.gettempdir())).resolve(strict=True)
    for loc in ([Path('C:/'),Path('D:/')] if sys.platform=='win32' else [temp]):
        if shutil.disk_usage(loc).free<=4*1024**3+512*1024**2:
            raise ValueError('less than disk budget for two temporary checkouts')
    if temp==repo or repo in temp.parents: raise ValueError('temporary checkout must be outside repo')
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONIOENCODING':'utf-8','TMPDIR':str(temp),'TMP':str(temp),'TEMP':str(temp)}
    with tempfile.TemporaryDirectory(prefix='ci60-source-',dir=temp) as tmp:
        work=Path(tmp)
        data=git('archive','--format=zip',PUBLISHED,'deploy/live')
        with ZipFile(BytesIO(data)) as archive:
            for member in archive.infolist():
                n=PurePosixPath(member.filename)
                if member.is_dir(): continue
                if n.parts[:2]!=('deploy','live') or '..' in n.parts: raise ValueError('unexpected Git archive member')
                path=work.joinpath(*n.parts);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(archive.read(member))
        def run(*args):
            cp=subprocess.run([sys.executable,'-B','-X','utf8',*(str(a) for a in args)],cwd=repo,env=env,capture_output=True)
            if cp.returncode:
                raise RuntimeError((cp.stderr or cp.stdout).decode('utf8',errors='replace')[-3500:])
            return cp.stdout
        run('scripts/build_business_pilot_audience_preview.py',work/'r4','--parent-root',work/'deploy/live')
        upstream_joint_status='PASS'
        try:
            run('scripts/rebuild_joint_pilot_review.py',work/'r4',work/'joint')
        except RuntimeError as error:
            details=str(error)
            if not options.windows_artifact_only or not all(t in details for t in ('WinError 1314','extra.symlink_to(guide)','test_pilot_snapshot_routes.py')):
                raise
            manifest=(work/'joint/_release.json').read_bytes()
            if hashlib.sha256(manifest).hexdigest()!='8e7824978e4e4d7a898e8214ab4b337b92209b80b06d51dcf2dc2133d6e84793':
                raise ValueError('incorrect intermediate artifact')
            # The official labels builder verifies the complete joint snapshot before use.
            upstream_joint_status='ARTIFACT_EXACT / SYMLINK_FIXTURE_UNEXECUTED_WINERROR_1314'
        run('scripts/build_business_simulator_labels_preview.py',work/'joint',work/'labels')
        report=json.loads(run(HERE/'rebuild_and_verify.py',repo,work/'labels'))
        report['upstream_joint_fixture']=upstream_joint_status
        report['rebuilt_from_git_head']=HEAD
        print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':
    main()
