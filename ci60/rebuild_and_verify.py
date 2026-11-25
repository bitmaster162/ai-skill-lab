"""Recreate and test one review ZIP from the standard CI labels-candidate directory.
Use python -B rebuild_and_verify.py REPO LABELS_CANDIDATE. All build output is temporary.
"""
import argparse
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

HERE=Path(__file__).resolve().parent
BASE='0e2702981427152474dbdfbe12380bdd02b9ea08fa9dc3ab73ed5931941550b7'
HEAD='a1b776f59d609a99b1ca162ade3aabdf72745a1b'
PATCH='97c31d18e7f35dad28d7517189b08238069512c50021adcfc5911e0ef4945aa6'
FINAL='a679d18882b161a12afd410369e68f042e893153198146d03696f5741f32937b'
FINAL_MANIFEST='01b68a85993c20f34614816df735e33af3c0636f4a787386a037fa453e671926'
PARENT='767936df52b6b4dc6c7420e00530afa91ddd9485ee696c3f45dc16522858855a'
VERIFIER='9cca58a8f85ee3b5cb07cf8160bd1eabb75aa09a90b30d7345f1e11a2f75aab3'

def require(ok,message):
    if not ok: raise ValueError(message)

def digest(data):
    return sha256(data).hexdigest()

def review(repo,base):
    manifest=(base/'_release.json').read_bytes()
    require(digest(manifest)==BASE,'wrong official CI base')
    doc=json.loads(manifest)
    files={entry['path']:(base/entry['path']).read_bytes() for entry in doc['files']}
    require(len(files)==len(doc['files'])==116 and all(len(files[e['path']])==e['size'] and digest(files[e['path']])==e['sha256'] for e in doc['files']),'invalid 116-file base')
    require({p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}==set(files)|{'_release.json'},'extra files in official reference')
    delta=(HERE/'review_delta.json').read_bytes()
    require(digest(delta)==PATCH,'delta SHA')
    for name,rule in json.loads(delta).items():
        require(digest(files[name])==rule['before_sha256'],'source '+name)
        text=files[name].decode()
        for edit in reversed(rule['edits_utf8_codepoints']):
            pos=edit['at']; remove=edit['remove']
            require(text[pos:pos+len(remove)]==remove,'unexpected source window '+name)
            text=text[:pos]+edit['insert']+text[pos+len(remove):]
        files[name]=text.encode()
        require(digest(files[name])==rule['after_sha256'],'candidate '+name)
    for family in ('Onest','Unbounded'):
        name=family+'-OFL.txt'
        files['fonts/'+name]=subprocess.check_output(['git','--no-optional-locks','-C',str(repo),'show',HEAD+':licenses/'+name])
    entries=[{'path':n,'size':len(b),'sha256':digest(b)} for n,b in sorted(files.items())]
    payload=digest(''.join(f"{e['path']}\t{e['size']}\t{e['sha256']}\n" for e in entries).encode())
    identifier='AISL_R2_NOJS_P2P3_LOCAL_REVIEW_'+payload
    doc.update(files=entries,file_count=len(entries),payload_sha256=payload,release_id=identifier,patch_id=identifier,parent_manifest_sha256=PARENT)
    files['_release.json']=(json.dumps(doc,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode()
    require(digest(files['_release.json'])==FINAL_MANIFEST,'wrong reconstructed manifest')
    output=BytesIO()
    with ZipFile(output,'w',compression=ZIP_DEFLATED,compresslevel=9) as archive:
        for name,raw in sorted(files.items()):
            info=ZipInfo(name,(2026,8,15,0,0,0))
            info.create_system=0
            info.external_attr=27525120
            archive.writestr(info,raw,compress_type=ZIP_DEFLATED,compresslevel=9)
    data=output.getvalue()
    require(len(data)==685589 and digest(data)==FINAL,'wrong physical ZIP')
    return data

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo',type=Path)
    parser.add_argument('labels_candidate',type=Path)
    args=parser.parse_args()
    repo=args.repo.resolve(strict=True)
    base=args.labels_candidate.resolve(strict=True)
    temp=Path(os.environ.get('RUNNER_TEMP',tempfile.gettempdir())).resolve(strict=True)
    drives=(Path('C:/'),Path('D:/')) if sys.platform=='win32' else (temp,)
    require(__debug__ and sys.dont_write_bytecode and min(shutil.disk_usage(p).free for p in drives)>4*1024**3+8*1024**2,'storage or Python flags')
    require(repo!=temp and repo not in temp.parents, 'temp outside repo required')
    script=HERE/'verify_ci60.py'
    require(digest(script.read_bytes())==VERIFIER,'wrong standalone verification script')
    data=review(repo,base)
    with tempfile.TemporaryDirectory(dir=temp,prefix='ci60-reproduce-') as scratch:
        output=Path(scratch)/'review.zip'
        output.write_bytes(data)
        proc=subprocess.run([sys.executable,'-B','-X','utf8',str(script),str(repo),str(output),'--temp',str(temp)],stdout=subprocess.PIPE,check=True)
    report=json.loads(proc.stdout)
    # The generated path was intentionally temporary. Preserve how to reproduce it.
    report['artifact']='memory reconstruction staged only for verification'
    report['generated_from_ci_manifest']=BASE
    report['ci_base_verified_files']=116
    report['added_repository_licenses']=['licenses/Onest-OFL.txt','licenses/Unbounded-OFL.txt']
    report['review_delta_sha256']=PATCH
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':
    main()
