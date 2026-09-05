#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
required=[('components/workshop/WorkshopBusiness.tsx', ['Ship · Revise · Stop.', 'human review', 'failure modes', 'data boundaries', 'fallback', 'Stop']), ('components/workshop/WorkshopBusiness.tsx', ['Ship · Revise · Stop.', 'human review', 'failure modes', 'data boundaries', 'fallback', 'Stop']), ('deploy/live/business.html', ['Ship · Revise · Stop.', 'human review', 'failure modes', 'data boundaries', 'fallback', 'STOP']), ('deploy/live/en/business.html', ['Ship · Revise · Stop.', 'human review', 'failure modes', 'data boundaries', 'fallback', 'STOP'])]
checks=0
for rel,needles in required:
    text=(ROOT/rel).read_text(encoding='utf-8')
    for n in needles:
        if n not in text:
            print(f'BUSINESS_DECISION_GATE_FAIL {rel}: missing {n}'); sys.exit(1)
        checks+=1
print(f'BUSINESS_DECISION_GATE_PASS checks={checks} surfaces=4')
