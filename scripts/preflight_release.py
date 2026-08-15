#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path(__file__).resolve().parents[1]

def run(name:str, cmd:list[str], env:dict[str,str]|None=None)->dict:
    merged=os.environ.copy()
    if env: merged.update(env)
    p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,env=merged)
    out=(p.stdout+p.stderr).strip()
    print(f'[{name}] {"PASS" if p.returncode==0 else "FAIL"}')
    if out: print(out)
    return {'name':name,'status':'PASS' if p.returncode==0 else 'FAIL','returncode':p.returncode,'output':out[-8000:]}

def git(*args:str)->str:
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--release',required=True)
    ap.add_argument('--output')
    args=ap.parse_args()
    gates=[]
    gates.append(run('build_csp',['python','scripts/build_csp.py']))
    gates.append(run('build_manifest',['python','scripts/build_static_manifest.py',args.release]))
    checks=[
      ('static_release',['python','scripts/check_static_release.py']),
      ('search_metadata',['python','scripts/check_search_metadata.py']),
      ('structured_data',['python','scripts/check_structured_data.py']),
      ('faq_parity',['python','scripts/check_faq_parity.py']),
      ('session_scope',['python','scripts/check_session_scope.py']),
      ('youth_policy_freshness',['python','scripts/check_youth_policy_freshness.py']),
      ('youth_route_parity',['python','scripts/check_youth_route_parity.py']),
      ('curriculum_package_mapping',['python','scripts/check_curriculum_package_mapping.py']),
      ('parent_route_parity',['python','scripts/check_parent_route_parity.py']),
      ('trust_route_parity',['python','scripts/check_trust_route_parity.py']),
      ('business_decision_gate',['python','scripts/check_business_decision_gate.py']),
      ('security_headers',['python','scripts/check_security_headers.py']),
      ('static_performance',['python','scripts/check_static_performance.py']),
      ('contrast_tokens',['python','scripts/check_contrast_tokens.py']),
      ('inline_scripts',['python','scripts/check_inline_scripts.py']),
      ('matcher_runtime',['node','scripts/check_matcher_runtime.mjs']),
      ('start_runtime',['node','scripts/check_start_runtime.mjs']),
      ('commercial_parity',['python','scripts/check_commercial_parity.py']),
      ('contact_funnel',['python','scripts/check_contact_funnel.py']),
      ('cta_semantics',['python','scripts/check_cta_semantics.py']),
      ('navigation_parity',['python','scripts/check_navigation_parity.py']),
      ('static_accessibility',['python','scripts/check_static_accessibility.py']),
      ('client_privacy',['python','scripts/check_client_privacy.py']),
      ('launch_gate',['npm','run','check:launch']),
      ('git_diff_check',['git','diff','--check']),
    ]
    for name,cmd in checks:
        env=None
        if name=='launch_gate':
            env={'NEXT_PUBLIC_SITE_URL':'https://ai-skill-lab.vercel.app','NEXT_PUBLIC_TELEGRAM_URL':'https://t.me/BiTFormer'}
        gates.append(run(name,cmd,env))
        if gates[-1]['status']=='FAIL': break
    manifest=json.loads((ROOT/'deploy/live/_release.json').read_text(encoding='utf-8'))
    status='PASS' if all(x['status']=='PASS' for x in gates) else 'FAIL'
    receipt={
      'schema':'ai-skill-lab.preflight.v1',
      'release':args.release,
      'status':status,
      'created_at_utc':datetime.now(timezone.utc).isoformat(),
      'git':{'head':git('rev-parse','HEAD'),'tree':git('rev-parse','HEAD^{tree}'),'branch':git('branch','--show-current')},
      'static_release':{'file_count':manifest['file_count'],'payload_sha256':manifest['payload_sha256']},
      'gates':gates,
    }
    if args.output:
        out=Path(args.output)
        if not out.is_absolute(): out=ROOT/out
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(f'RECEIPT={out}')
    print(f'RELEASE_PREFLIGHT_{status} release={args.release} gates={len(gates)} payload_sha256={manifest["payload_sha256"]}')
    return 0 if status=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
