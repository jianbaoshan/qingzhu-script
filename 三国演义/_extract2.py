# -*- coding: utf-8 -*-
"""Extract all complete segments from the partial file by brace matching."""
import json, re
P = r'd:\study\GitHub\shuohao-skills\三国演义\storyboard-batch-8.json'
raw = open(P, encoding='utf-8-sig').read()

def find_object_start_after(txt, idx):
    # find first '{' at/after idx
    return txt.find('{', idx)

def extract_segment(txt, seg_id_marker_idx):
    # from the segment's 'id' key, back up to containing object start '{' and match braces
    # find the '{' that contains this id literally (nearest before, at depth)
    # Simpler: find '{\n          "id": ' immediately preceding
    a = txt.rfind('"segments": [', 0, seg_id_marker_idx)
    # find the exact object start: search backwards from marker for '\n        {'
    sub = txt[:seg_id_marker_idx]
    i = sub.rfind('{')
    # walk: we want the '{' that opens this object (after previous '},' or '[')
    start = i
    # ensure it's at object level: go back until we find '},\n        {' pattern
    m = list(re.finditer(r'\},\n?\s*\{\n?\s*"id"', txt))
    return start

# Instead: parse each segment by slicing between consecutive '"id": "E.."' boundaries
ids = list(re.finditer(r'"id": "E(\d+)-(\d+)"', raw))
segments = []  # (ep, seq, dict) for complete ones
for idx, m in enumerate(ids):
    start = raw.rfind('\n        {', 0, m.start())
    # find segment obj start: nearest '{' that precedes start+ several chars
    # find end: the segment object boundary — next segment's '\n        {' OR closing of array
    if idx+1 < len(ids):
        end = raw.rfind('\n        {', 0, ids[idx+1].start())
        if end < start:
            end = raw.find(',\n          "id"', m.start())
    else:
        # last segment: object ends where the segments array ends or file ends
        end = len(raw)
    segtext = raw[start:end]
    segtext = segtext.lstrip()
    if not segtext.startswith('{'):
        segtext = '{' + segtext
    # now find the matching closing brace for this object
    depth=0; close=None
    for k,ch in enumerate(segtext):
        if ch=='"' :
            pass
        if ch=='{': depth+=1
        elif ch=='}': 
            depth-=1
            if depth==0: close=k; break
    objtext = segtext[:close+1]
    try:
        obj=json.loads(objtext)
        segments.append((int(m.group(1)), int(m.group(2)), obj))
    except Exception as e:
        print('FAIL seg', m.group(1), m.group(2), str(e)[:60])

seen=[(e,s) for e,s,o in segments]
print('extracted', len(segments), seen)
from collections import defaultdict
byep=defaultdict(list)
for e,s,o in segments: byep[e].append((s,o))
for e in sorted(byep):
    print('ep',e,'segs', sorted(s for s,o in byep[e]))
# save as pickled
import pickle
pickle.dump(segments, open(r'd:\study\GitHub\shuohao-skills\三国演义\_extracted.pkl','wb'))