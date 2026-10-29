#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
import site_r31_post_r7c_profile as post_r31
import sys
ROOT=Path(__file__).resolve().parents[1];LIVE=ROOT/'deploy/live';errors=[];checks=0
class P(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.current=None;self.anchors=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':
   a=dict(attrs);self.current={'href':(a.get('href') or '').strip(),'class':a.get('class',''),'text':[]}
 def handle_data(self,data):
  if self.current is not None:self.current['text'].append(data)
 def handle_endtag(self,tag):
  if tag=='a' and self.current is not None:
   self.current['text']=' '.join(''.join(self.current['text']).split());self.anchors.append(self.current);self.current=None
def anchors(path):p=P();p.feed(path.read_text(encoding='utf-8'));return p.anchors
import site_a1_a2_r2_successor as site_a2
SITE_A2=site_a2.active()
POST_R31=post_r31.active() or SITE_A2
if POST_R31:
 (site_a2.verify() if SITE_A2 else post_r31.check_release())
for path in sorted(LIVE.rglob('*.html')):
 rel=path.relative_to(ROOT).as_posix()
 for a in anchors(path):
  label=a['text'].casefold();href=a['href'];checks+=1
  # Exact form fallback points to the on-page channel directory, not a direct channel.
  if POST_R31 and rel in {'deploy/live/start.html','deploy/live/en/start.html'}:
   locale='en' if rel=='deploy/live/en/start.html' else 'ru'
   if href=='#contact-channels' and label==post_r31.candidate.NOTE[locale][1].casefold():
    continue
  if 'telegram' in label and not href.startswith('https://t.me/'):errors.append(f'{rel}: Telegram label mismatch {href}')
  if ('почта' in label or label.startswith('email')) and not href.startswith('mailto:'):errors.append(f'{rel}: email label mismatch {href}')
  if 'whatsapp' in label and not href.startswith('https://wa.me/'):errors.append(f'{rel}: WhatsApp label mismatch {href}')
  if label.startswith('line') and not href.startswith('https://line.me/'):errors.append(f'{rel}: LINE label mismatch {href}')
  if href in {'/start','/en/start'} and any(x in label for x in ['telegram','whatsapp','line','почта','email']):errors.append(f'{rel}: internal Start masquerades as direct channel')
for rel in ['deploy/live/start.html','deploy/live/en/start.html']:
 aa=anchors(ROOT/rel);send=[a for a in aa if 'briefSendLink' in a['class']];checks+=1
 if len(send)!=5:errors.append(f'{rel}: briefSendLink count={len(send)}')
 if any(not a['href'].startswith('https://t.me/BiTFormer?text=') for a in send):errors.append(f'{rel}: brief send default channel drift')
print(f'cta_semantics_checks={checks}')
if errors:
 for e in errors:print('FAIL:',e)
 sys.exit(1)
print('CTA_SEMANTICS_PASS')
