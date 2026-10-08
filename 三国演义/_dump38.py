# -*- coding: utf-8 -*-
import json
P = r'd:\study\GitHub\shuohao-skills\三国演义\storyboard-batch-8.json'
raw=open(P,encoding='utf-8-sig').read()
suffix='\n        }\n      ]\n    },\n    {"ep":39,"segments":[]},\n    {"ep":40,"segments":[]}\n  ]\n}\n'
d=json.loads(raw+suffix)
ep38=[e for e in d['episodes'] if e['ep']==38][0]
print('=== ep38 segments & beat claims & seconds ===')
for s in ep38['segments']:
    claims=[c['beats'] for c in s['cuts']]
    tot=round(sum(c['seconds'] for c in s['cuts']),1)
    print(f"{s['id']} scene{s.get('sceneIndex')} beats={claims} tot={tot}s cuts={len(s['cuts'])}")
tot38=round(sum(sum(c['seconds'] for c in s['cuts']) for s in ep38['segments']),1)
print('ep38 total', tot38)
# one full segment example (E38-16 style) -> E38-13
ex=[s for s in ep38['segments'] if s['id']=='E38-13'][0]
print(json.dumps(ex, ensure_ascii=False, indent=1)[:2600])