# -*- coding: utf-8 -*-
import json, os, re, unicodedata
ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPT = json.load(open(os.path.join(ROOT, 'script.json'), encoding='utf-8'))
CPS = 4.5
for ep in [8, 9, 10]:
    for e in SCRIPT['episodes']:
        if e['ep'] != ep:
            continue
        print('='*70)
        print(f'EP{ep} target={e.get("targetSeconds")}')
        for si, sc in enumerate(e['scenes'], 1):
            props = sc.get('props') or []
            chars = sc.get('characters') or []
            scid = sc.get('id') or sc.get('scene') or sc.get('title') or ''
            print(f'\n-- scene {si}: {scid}  props={props} chars={chars}')
            for bi, b in enumerate(sc['flow'], 1):
                if 'line' in b:
                    n = len(re.sub(r'\s','',b['line']))
                    print(f'  beat{bi} [{round(n/CPS,1)}s] LINE: {b["line"]}')
                else:
                    act = b.get('action','') if isinstance(b.get('action'), str) else ''
                    print(f'  beat{bi} [2.5s] ACTION: {act}')