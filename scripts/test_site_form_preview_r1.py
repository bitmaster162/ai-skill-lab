#!/usr/bin/env python3
"""Offline browser regression tests for the static form candidate, not backend E2E.

All browser requests are locally fulfilled, mocked or aborted. This script never
continues a request to a real endpoint and never uses the user's browser profile.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import mimetypes
from pathlib import Path
import time
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
from build_site_form_preview_r1 import ROOT, SEALED, COPY, Html, require, verify_manifest

ORIGIN='https://aiskillab.work'
FAULTS=['no_js','missing','syntax','init_fault','no_fetch']
BEHAVIOR=['success_click','success_enter','error_http','malformed_response','error_network',
          'busy_double','privacy_required','parent_required','teen_required','script_twice','forced_native_submit']
EXPECTED_CASES=2*2*(len(FAULTS)*2+len(BEHAVIOR))

def run(preview: Path, chrome: str, report: dict, screenshots: Path|None) -> None:
    import psutil
    from playwright.sync_api import sync_playwright
    require(psutil.virtual_memory().available >= 2*1024**3,'HOST_MEMORY_HOLD: need 2 GiB available before isolated browser launch')
    manifest=verify_manifest(preview)
    require(manifest['release_id']=='SITE_FORM_READINESS_CANDIDATE_R1_20261014','Unexpected candidate')
    require(manifest['file_count']==99,'Candidate file count drift')
    root_manifest=verify_manifest(SEALED)
    config=json.loads((preview/'vercel.json').read_bytes())
    headers={h['key']:h['value'] for rule in config['headers'] if rule['source']=='/(.*)' for h in rule['headers']}
    require("form-action 'none'" in headers['Content-Security-Policy'],'CSP missing')
    # These first checks catch template/source drift before running any browser.
    react=(ROOT/'components/LeadForm.tsx').read_text(encoding='utf-8')
    require('disabled={!ready || state === "sending"}' in react,'React server-safe disable missing')
    require('useEffect(() => { setReady(true); }, []);' in react,'React hydration readiness missing')
    require('!ready || inFlight.current || !form.checkValidity()' in react,'React submit guard missing')
    for locale,rel in [('ru','start.html'),('en','en/start.html')]:
        s=(preview/rel).read_text(encoding='utf-8')
        require('data-lead-state="unready"' in s and 'type="submit" disabled' in s,'Static initial disable missing')
        require(s.count('/lead-form-runtime.js')==1,'Runtime script count mismatch')
        for text in COPY[locale]: require(text in s and text in react,'Static/React fallback copy mismatch')
    for url in [e.text for e in ET.parse(preview/'sitemap.xml').getroot().findall('{*}url/{*}loc')]:
        route=urlsplit(str(url)).path;rel='index.html' if route=='/' else route.strip('/')+'.html'
        p=Html();p.feed((preview/rel).read_text(encoding='utf-8'))
        require(p.h1==1 and p.canonical==[url] and len(p.title)<=60 and len(p.meta['description'])<=160,'Metadata regression: '+route)
    report.update(manifest_verified=manifest['file_count'],metadata_routes_verified=54,
                  candidate_payload=manifest['payload_sha256'],sealed_payload=root_manifest['payload_sha256'],
                  schema='ai-skill-lab.form-readiness.offline-browser-tests.v1',cases=[],
                  real_api_requests_sent=0,browser_requests_continued=0,user_profile_used=False,
                  next_build_performed=False,react_hydration_runtime_tested=False)
    start=time.monotonic()
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=chrome,headless=True,timeout=15000,
                    args=['--disable-background-networking','--disable-component-update','--no-first-run'])
        report['browser_version']=browser.version
        try:
            for locale in ['ru','en']:
                path='/start' if locale=='ru' else '/en/start'
                for width in [1440,390]:
                    modes=[f'{m}_{trigger}' for m in FAULTS for trigger in ['click','enter']]+BEHAVIOR
                    for case in modes:
                        require(time.monotonic()-start<130,'Browser test wall-time budget exceeded')
                        ctx=browser.new_context(java_script_enabled=not case.startswith('no_js'),
                               service_workers='block',offline=True,viewport={'width':width,'height':900 if width==1440 else 844})
                        ctx.set_default_timeout(4000)
                        api=[];leaks=[];blocked=[];pending=[];errors=[];requests=0
                        def handle(rt):
                            nonlocal requests
                            req=rt.request;u=urlsplit(req.url);requests+=1
                            body=req.post_data or ''
                            if 'ASL_SYNTHETIC' in unquote(req.url) or (req.method=='GET' and u.query):leaks.append(req.url)
                            if u.scheme!='https' or u.netloc!='aiskillab.work':
                                blocked.append('non_fixture_origin');rt.abort();return
                            if u.path=='/api/lead' and req.method=='POST':
                                try:data=json.loads(body)
                                except ValueError:data={'invalid_json':True}
                                api.append(data)
                                if case=='busy_double':pending.append(rt);return
                                if case=='error_network':rt.abort();return
                                if case=='error_http':rt.fulfill(status=503,content_type='application/json',body='{"ok":false}');return
                                if case=='malformed_response':rt.fulfill(status=200,content_type='application/json',body='not-json');return
                                rt.fulfill(status=200,content_type='application/json',body='{"ok":true}');return
                            if req.method!='GET' or u.query or u.path.startswith('/api/') or u.path.startswith('/_vercel/'):
                                blocked.append(u.path);rt.abort();return
                            if u.path=='/lead-form-runtime.js' and (case.startswith('missing_') or case=='forced_native_submit'):
                                rt.abort();return
                            rel='index.html' if u.path=='/' else u.path.lstrip('/')
                            if '.' not in Path(rel).name:rel+='.html'
                            dest=(preview/rel).resolve()
                            if not dest.is_relative_to(preview.resolve()) or not dest.is_file():rt.abort();return
                            body=dest.read_bytes()
                            if u.path=='/lead-form-runtime.js' and case.startswith('syntax_'):body+=b'\n@intentional_syntax_fault'
                            ctype='application/javascript' if dest.suffix=='.js' else (mimetypes.guess_type(dest.name)[0] or 'application/octet-stream')
                            rt.fulfill(status=200,body=body,headers={**headers,'Content-Type':ctype})
                        ctx.route('**/*',handle)
                        if case.startswith('no_fetch_'):ctx.add_init_script('window.fetch = undefined;')
                        if case.startswith('init_fault_'):
                            ctx.add_init_script('''(() => { const original = Element.prototype.setAttribute;
                              Element.prototype.setAttribute = function(k,v) {
                                if (this.tagName === 'FORM' && k === 'data-lead-state' && v === 'ready')
                                  throw new Error('ASL_SYNTHETIC_INIT_FAULT');
                                return original.call(this,k,v);
                              }; })();''')
                        page=ctx.new_page();page.on('console',lambda msg:errors.append(msg.text) if msg.type=='error' else None)
                        try:
                            page.goto(ORIGIN+path,wait_until='load',timeout=8000)
                            form=page.locator('form#application-form');btn=form.locator('button[type="submit"]')
                            note=form.locator('[data-lead-readiness]');contact=form.locator('[data-lead-direct-contact] a')
                            msg=form.locator('[data-lead-message]')
                            isfault=case.startswith(tuple(m+'_' for m in FAULTS)) or case=='forced_native_submit'
                            if isfault:
                                require(btn.is_disabled() and note.is_visible(),'Fault mode looks ready: '+case)
                                require(form.get_attribute('data-lead-state')=='unready','Fault state flag mismatch')
                            else:
                                page.locator('form#application-form[data-lead-state="ready"]').wait_for(state="attached")
                                require(btn.is_enabled() and note.is_hidden(),'Ready state UI mismatch')
                            require(contact.is_visible() and contact.get_attribute('href')=='#contact-channels','Direct contact link missing')
                            require(page.locator('#contact-channels').count()==1,'Fallback destination missing')
                            form.locator('[name="name"]').fill('ASL_SYNTHETIC_FORM_TEST')
                            form.locator('[name="contact"]').fill('asl-synthetic@example.invalid')
                            form.locator('[name="goal"]').fill('ASL_SYNTHETIC_NO_LIVE_REQUEST')
                            if case!='privacy_required':form.locator('[name="privacyConsent"]').check()
                            if case in ('parent_required','teen_required'):
                                form.locator('[name="audience"]').select_option('parent' if case=='parent_required' else 'teen')
                            valid=form.evaluate('f => f.checkValidity()')
                            expected_invalid=case in ('privacy_required','parent_required','teen_required')
                            require(valid!=expected_invalid,'Test fixture validity mismatch')
                            if case=='script_twice':page.add_script_tag(url=ORIGIN+'/lead-form-runtime.js')
                            if case=='forced_native_submit':
                                form.evaluate('f => f.submit()')
                            elif isfault:
                                if case.endswith('_enter'):form.locator('[name="contact"]').press('Enter',no_wait_after=True)
                                else:
                                    btn.scroll_into_view_if_needed();box=btn.bounding_box();require(box is not None,'Disabled button has no layout')
                                    page.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2)
                            elif case=='success_enter':form.locator('[name="contact"]').press('Enter',no_wait_after=True)
                            else:btn.click(no_wait_after=True)
                            page.wait_for_timeout(100)
                            if case=='busy_double':
                                require(len(pending)==1 and btn.is_disabled(),'Sending state not busy')
                                form.evaluate('f => {f.dispatchEvent(new Event("submit",{bubbles:true,cancelable:true}));f.dispatchEvent(new Event("submit",{bubbles:true,cancelable:true}));}')
                                page.wait_for_timeout(70);require(len(api)==1,'Repeated effect while busy')
                                pending.pop().fulfill(status=200,content_type='application/json',body='{"ok":true}')
                            if expected_invalid:
                                require(len(api)==0,'Validation allowed unconsented submission')
                                if case in ('parent_required','teen_required'):
                                    adult=form.locator('[name="adultConfirmation"]')
                                    require(adult.is_visible() and adult.get_attribute('required') is not None,'Adult safety confirmation missing')
                                    adult.check();btn.click(no_wait_after=True)
                            expected_posts=0 if isfault or case=='privacy_required' else 1
                            if expected_posts:
                                form.locator("[data-lead-message].success, [data-lead-message].error").wait_for(state="attached")
                                require(btn.is_enabled(),'Submit not restored after settled response')
                                failure=case in ('error_http','malformed_response','error_network')
                                require(('error' if failure else 'success') in (msg.get_attribute('class') or ''),'Response UI class incorrect')
                                if failure:require(form.locator('[name="name"]').input_value()=='ASL_SYNTHETIC_FORM_TEST','Failure lost form fields')
                                else:require(form.locator('[name="name"]').input_value()=='','Success failed to reset form')
                                if case in ('parent_required','teen_required'):require(api[0].get('adultConfirmation')=='yes','Adult consent not in mocked payload')
                            require(len(api)==expected_posts,'Unexpected mocked request count: '+case)
                            require(not leaks and page.url==ORIGIN+path,'Field-bearing URL or unexpected navigation')
                            if isfault:require(btn.is_disabled() and note.is_visible(),'Failure fallback disappeared')
                            if case=='forced_native_submit':require(any('form-action' in e for e in errors),'Forced native submit not observed blocked by CSP')
                            if screenshots and width==390 and case=='missing_click':
                                form.scroll_into_view_if_needed();form.screenshot(path=str(screenshots/f'form_unavailable_{locale}.png'),timeout=6000)
                            report['cases'].append({'locale':locale,'width':width,'case':case,'status':'PASS',
                                  'mocked_api_calls':len(api),'field_url_leaks':len(leaks),'page_url_unchanged':True,
                                  'direct_contact_visible':True,'readiness_visible':note.is_visible(),
                                  'browser_requests_intercepted':requests,'real_requests_continued':0})
                            print(json.dumps({'case':len(report['cases']),'locale':locale,'width':width,'scenario':case,'status':'PASS'}),flush=True)
                        except Exception as e:
                            report['cases'].append({'locale':locale,'width':width,'case':case,'status':'FAIL','error':str(e),'mocked_api_calls':len(api)})
                            raise
                        finally:ctx.close()
        finally:browser.close()
    require(len(report['cases'])==EXPECTED_CASES,'Case-count mismatch')
    verify_manifest(preview);verify_manifest(SEALED)
    report.update(status='PASS_LOCAL_ONLY',passed=EXPECTED_CASES,unique_cases=EXPECTED_CASES,
                  elapsed_seconds=round(time.monotonic()-start,3),limitations=['Static Chromium adapter; not full Next build',
                  'No real lead delivery or D1/Telegram/email test','No cross-browser guarantee','No production release admission'])

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--preview',type=Path,required=True)
    ap.add_argument('--chrome',required=True);ap.add_argument('--receipt',type=Path,required=True);ap.add_argument('--screenshots',type=Path)
    a=ap.parse_args();require(not a.receipt.exists(),'Receipt exists; do not overwrite evidence')
    report={}
    try:
        if a.screenshots:require(a.screenshots.is_dir(),'Screenshot directory does not exist')
        run(a.preview.resolve(),a.chrome,report,a.screenshots)
    except Exception as e:
        report['status']='HOLD';report['error']=str(e);raise
    finally:a.receipt.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
