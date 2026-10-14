#!/usr/bin/env python3
"""Targeted source-copy and offline-browser acceptance, not release approval."""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
import unittest
from urllib.parse import urlsplit, unquote
import prepare_phuket_agency_terms_r4 as candidate


class Tags(HTMLParser):
    def __init__(self, raw):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.feed(raw)
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class AgencyTermsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = candidate.r3_payload()
        cls.files, cls.stats = candidate.render()
        cls.copy = candidate.copy_data()

    def test_reproduction_and_manifest(self):
        self.assertEqual(candidate.render(), (self.files, self.stats))
        candidate.verify_payload(self.files)
        self.assertEqual(len(self.files), 105)

    def test_exact_report_excerpt_and_authority(self):
        for lang in ('ru', 'en'):
            self.assertEqual(candidate.sha('\n\n'.join(self.copy[lang]['paragraphs']).encode()), candidate.EXCERPT_SHA[lang])
            self.assertFalse(any(ch.isdigit() for p in self.copy[lang]['paragraphs'] for ch in p))
        self.assertEqual(self.copy['source']['sha256'], candidate.REPORT_SHA)
        self.assertFalse(any(self.copy['authority'].values()))
        self.assertFalse(self.stats['production'])
        self.assertFalse(self.stats['deploy'])

    def test_only_three_payload_files_and_new_manifest(self):
        changed = {n for n in self.base if self.base[n] != self.files[n]}
        self.assertEqual(changed, {'phuket-universe.html', 'en/phuket-universe.html', 'phuket-universe.css', '_release.json'})
        self.assertEqual(self.files['vercel.json'], self.base['vercel.json'])
        self.assertEqual(self.files['lab-command.js'], self.base['lab-command.js'])
        self.assertNotEqual(self.files['_release.json'], self.base['_release.json'])
        for name in self.base:
            self.assertEqual((candidate.ROOT/'deploy/live'/name).read_bytes(), self.base[name])

    def test_duplicates_missing_section_and_tampering_fail(self):
        raw = self.base['phuket-universe.html'].decode('utf-8')
        with self.assertRaisesRegex(ValueError, 'boundary'):
            candidate.add_terms(candidate.add_terms(raw, 'ru'), 'ru')
        with self.assertRaisesRegex(ValueError, 'boundary'):
            candidate.add_terms(raw.replace(candidate.MARKER, '<span'), 'ru')
        with self.assertRaisesRegex(ValueError, 'Unknown'):
            candidate.add_terms(raw, 'de')
        corrupt = dict(self.files)
        corrupt['phuket-universe.html'] += b'!'
        with self.assertRaisesRegex(ValueError, 'bytes'):
            candidate.verify_payload(corrupt)

    def test_svg_links_sections_and_csp_unchanged(self):
        geometry = {'svg', 'path', 'ellipse', 'circle', 'filter', 'radialgradient', 'stop'}
        for lang, route in candidate.ROUTES.items():
            name = route.lstrip('/') + '.html'
            old = Tags(self.base[name].decode('utf-8')).tags
            new = Tags(self.files[name].decode('utf-8')).tags
            self.assertEqual([x for x in old if x[0] in geometry], [x for x in new if x[0] in geometry])
            self.assertEqual([a.get('href') for t,a in old if t=='a'], [a.get('href') for t,a in new if t=='a'])
            self.assertEqual([a.get('id') for t,a in new if t=='section'], ['top','orbit','homes','agencies'])
            self.assertFalse(any('style' in a or t=='style' for t,a in new))
            self.assertEqual(sum(t=='h1' for t,a in new), 1)
            self.assertEqual(sum(t=='details' and a.get('data-agency-terms-version')=='pilot-r1' for t,a in new),1)


def typescript_parity(lib: str):
    module = Path(lib).resolve()
    candidate.need(module.is_file(), 'Pinned TypeScript library unavailable')
    script = r'''
const fs=require('node:fs'),path=require('node:path'),Module=require('node:module');
const ts=require(process.argv[2]);const root=process.argv[3];
const f=path.join(root,'components/phuketUniverseAgencyTerms.ts');
const code=ts.transpileModule(fs.readFileSync(f,'utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2017,module:ts.ModuleKind.CommonJS,esModuleInterop:true},reportDiagnostics:true});
if((code.diagnostics||[]).some(d=>d.category===ts.DiagnosticCategory.Error))throw Error('TypeScript syntax failure');
const m=new Module(f);m.filename=f;m.paths=Module._nodeModulePaths(path.dirname(f));m._compile(code.outputText,f);
const src=fs.readFileSync(path.join(root,'components/phuketUniverseMarkup.ts'),'utf8');
const markup=JSON.parse(src.split('export const phuketUniverseMarkup = ')[1].split(' as const;')[0]);
const out={};for(const locale of ['ru','en'])out[locale]=m.exports.withAgencyPilotTerms(markup[locale],locale);
for(const locale of ['ru','en']){let caught=false;try{m.exports.withAgencyPilotTerms(out[locale],locale)}catch{caught=true}if(!caught)throw Error('Duplicate accepted');}
process.stdout.write(JSON.stringify(out));
'''
    p = subprocess.run(['node','-',str(module),str(candidate.ROOT)],input=script,capture_output=True,text=True,encoding='utf-8',timeout=30)
    candidate.need(p.returncode==0, 'TypeScript execution failed: '+p.stderr[-1000:])
    actual = json.loads(p.stdout)
    ts = (candidate.ROOT/'components/phuketUniverseMarkup.ts').read_text(encoding='utf-8')
    baseline = json.loads(ts.split('export const phuketUniverseMarkup = ',1)[1].rsplit(' as const;',1)[0])
    for lang in ('ru','en'):
        candidate.need(actual[lang]==candidate.add_terms(baseline[lang],lang), 'TS/static renderer disagreement')
    component = (candidate.ROOT/'components/PhuketUniverse.tsx').read_text(encoding='utf-8')
    candidate.need('withAgencyPilotTerms(phuketUniverseMarkup[locale], locale)' in component and 'phuket-universe-agency-terms.css' in component,'Next component not wired')
    print('TYPESCRIPT_STATIC_COPY_PARITY_PASS locales=2 duplicate_guard=PASS',flush=True)


def browser_acceptance(screenshots: bool):
    import psutil
    from playwright.sync_api import sync_playwright
    candidate.need(psutil.virtual_memory().available>=2*1024**3,'HOST_RESOURCE_HOLD')
    exe=Path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')
    candidate.need(exe.is_file(),'Test browser unavailable')
    files,stats=candidate.render();copy=candidate.copy_data()
    cfg=json.loads(files['vercel.json'])
    headers={h['key']:h['value'] for rule in cfg['headers'] if rule['source']=='/(.*)' for h in rule['headers']}
    images=candidate.ROOT/'review'/candidate.RELEASE
    if screenshots:images.mkdir(parents=True,exist_ok=False)
    cases=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=str(exe),headless=True,timeout=20000,args=['--disable-background-networking','--disable-component-update','--no-first-run'])
        try:
            for locale,route in candidate.ROUTES.items():
                for enabled in (False,True):
                    for width in (390,1440):
                        ctx=browser.new_context(java_script_enabled=enabled,offline=True,service_workers='block',viewport={'width':width,'height':844})
                        page=ctx.new_page();page.set_default_timeout(6000)
                        rejected=[];events=[];errors=[]
                        page.on('pageerror',lambda e:errors.append(str(e)))
                        page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
                        def fulfill(rt):
                            request=rt.request;url=urlsplit(request.url)
                            if url.scheme!='https' or url.netloc!='aiskillab.work':
                                rejected.append(request.url);rt.abort();return
                            if url.path=='/api/event' and request.method=='POST':
                                events.append(json.loads(request.post_data or '{}'));rt.fulfill(status=200,body='{"ok":true}',headers={'Content-Type':'application/json'});return
                            if request.method!='GET' or url.query:
                                rejected.append(request.url);rt.abort();return
                            if url.path=='/_vercel/insights/script.js':
                                rt.fulfill(status=200,body='/* offline stub */',headers={'Content-Type':'application/javascript'});return
                            name=unquote(url.path).lstrip('/');name=name if name in files else name+'.html'
                            if name not in files:
                                rejected.append(request.url);rt.abort();return
                            mime={'.css':'text/css','.html':'text/html; charset=utf-8','.js':'application/javascript','.woff2':'font/woff2','.svg':'image/svg+xml','.webmanifest':'application/manifest+json'}.get(Path(name).suffix,'application/octet-stream')
                            rt.fulfill(status=200,body=files[name],headers={**headers,'Content-Type':mime})
                        ctx.route('**/*',fulfill)
                        response=page.goto('https://aiskillab.work'+route,wait_until='load',timeout=15000)
                        page.evaluate('document.fonts.ready')
                        candidate.need(response is not None and response.status==200,'Fixture route failed')
                        details=page.locator('#agencies details#agency-pilot-terms')
                        candidate.need(details.count()==1 and details.get_attribute('open') is None,'Terms not initially collapsed once')
                        details.locator('summary').click()
                        candidate.need(details.get_attribute('open') is not None,'Native no-JS disclosure failed')
                        candidate.need(details.locator('.pu-agency-terms-body p').all_text_contents()==copy[locale]['paragraphs'],'Displayed terms differ from report')
                        candidate.need(details.locator('.pu-agency-terms-body p').first.is_visible(),'Terms not readable')
                        dimension=page.evaluate('({width:document.documentElement.scrollWidth,viewport:innerWidth,height:document.documentElement.scrollHeight})')
                        candidate.need(dimension['width']<=width+1,'Horizontal overflow')
                        if enabled:
                            page.evaluate('''() => { for(const event of ['lead_submit_ok','lead_submit_error'])dispatchEvent(new CustomEvent('asl:lead-event',{detail:{event}})); }''')
                            page.wait_for_timeout(100)
                            candidate.need(events==[{'event':e,'page':route,'locale':locale} for e in ('lead_submit_ok','lead_submit_error')],'Existing event payload changed')
                        else:candidate.need(not events,'Unexpected no-JS event')
                        candidate.need(not errors and not rejected,'CSP or network error: '+repr((errors,rejected)))
                        if screenshots and width==390 and not enabled:
                            page.locator('#agencies').screenshot(path=str(images/(locale+'-agency-terms-390.png')))
                        details.locator('summary').click()
                        candidate.need(details.get_attribute('open') is None,'Native close failed')
                        cases.append({'locale':locale,'js':enabled,**dimension,'terms_paragraphs':3,'source_match':True,'native_details':True,'real_api_requests':0})
                        ctx.close()
        finally:browser.close()
    print('R4_BROWSER_ACCEPTANCE',json.dumps(cases),flush=True)
    return cases


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--typescript-lib')
    parser.add_argument('--browser',action='store_true')
    parser.add_argument('--screenshots',action='store_true')
    args=parser.parse_args()
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AgencyTermsTests))
    if not result.wasSuccessful():raise SystemExit(1)
    if args.typescript_lib:typescript_parity(args.typescript_lib)
    if args.browser:browser_acceptance(args.screenshots)
    print('R4_TERMS_TARGETED_PASS_NOT_RELEASE_INTEGRATED',flush=True)


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
