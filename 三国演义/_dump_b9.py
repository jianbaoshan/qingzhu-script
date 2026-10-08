# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
raw = open('storyboard-batch-9.json', encoding='utf-8-sig').read()
E = json.loads(raw.replace('\ufeff', ''))
for ep in [41,42,43,44,45]:
    for e in E['episodes']:
        if e['ep'] != ep: continue
        print('='*70)
        print(f"EP{ep} target={e.get('targetSeconds')}")
        for sc in e['seedScenes']:
            print(f" -- scene idx{sc['sceneIndex']} {sc['sceneId']} lighting={sc.get('lighting')} chars={sc['characters']} props={sc['props']}")
            for b in sc['beats']:
                kind = b['kind']
                tag = f"{b['n']} {kind} {b['seconds']} "
                if kind=='line': tag += f"{b.get('speaker','?')} "
                print(f"    beat {tag}{b['text']}")