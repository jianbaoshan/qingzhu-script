# -*- coding: utf-8 -*-
import json
P = r'd:\study\GitHub\shuohao-skills\三国演义\storyboard-batch-8.json'
raw = open(P, encoding='utf-8-sig').read()
print('len', len(raw))
print('tail:', repr(raw[-200:]))
# Append closures and try to parse entire structure
for suffix in ['\n        }\n      ]\n    },\n    {"ep":39,"segments":[]},\n    {"ep":40,"segments":[]}\n  ]\n}\n',
               '\n          ]\n        }\n      ]\n    }\n  ]\n}\n',
               ']}\n]\n}']:
    try:
        d=json.loads(raw+suffix)
        print('PARSED FULL with suffix', repr(suffix[:20])[::-1], 'eps', [e['ep'] for e in d['episodes']])
        print('  segCounts', [len(e['segments']) for e in d['episodes']])
        break
    except Exception as e:
        print('fail', repr(str(e)[:60]))