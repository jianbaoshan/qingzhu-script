# -*- coding: utf-8 -*-
import json, re
s = json.load(open(r'D:\study\GitHub\shuohao-skills\三国演义\script.json', encoding='utf-8-sig'))
def lc(l): return len(re.sub(r'\s+', '', l))
def lit(b): return round(lc(b['line'])/4.5, 1) if 'line' in b else 0

for ep in s['episodes']:
    if ep['ep'] in (39, 40):
        for sc in ep['scenes']:
            print('=== EP%s S%s chars=%s props=%s light=%s nflow=%d' % (
                ep['ep'], sc.get('sceneId'), sc.get('characters'), sc.get('props'), sc.get('lighting'), len(sc['flow'])))
            for i, b in enumerate(sc['flow'], 1):
                extra = lit(b)
                if 'line' in b:
                    print('  b%02d [%s] %s  ~%.1fs | %s' % (i, b['spk'] if 'spk' in b else '??', '', extra, b['line']))
                else:
                    print('  b%02d [action] :: %s' % (i, b.get('text', b.get('action', b.get('desc', '')))))
        print()