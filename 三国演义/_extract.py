# -*- coding: utf-8 -*-
"""Extract already-authored segments for eps 36,37,38 from the partial file."""
import json, re

P = r'd:\study\GitHub\shuohao-skills\三国演义\storyboard-batch-8.json'
raw = open(P, encoding='utf-8-sig').read()

# split by segment ids
idpat = re.compile(r'"id": "E(\d+)-(\d+)"')
positions = [(m.start(), int(m.group(1)), int(m.group(2))) for m in idpat.finditer(raw)]
print('segments found:', [(e,s) for _,e,s in positions], 'count', len(positions))

# We want to extract each segment as a JSON object. Instead of text-splitting, use a
# bracket matcher: find the last segment's opening '{' and matching '}' to confirm validity.
# Easier: reconstruct the file as valid by node? Instead, parse segments using json by
# temporarily replacing h3Prompt... already done. The file is valid through E38-15 as full
# segments, just the ending (after E38-15) is unclosed. Everything before E38-15 h3 close is fine.
# Find index of the LAST complete segment object boundary relative to 'ep": 38'.
# We'll locate 'ep": 38' and parse from there with tolerant closure.
start38 = raw.index('"ep": 38,')
# try closing with guesses
seg_blob = raw[start38:]
test = lambda s: extract38(seg_blob + s)
def extract38(b):
    d=json.loads('{"episodes":['+b+']}')
    return [e for e in d['episodes'] if e['ep']==38]
import json as _j
for suffix in ['"segments":[]}]}', '",{"segments":[]}]}', ']}}', ']}}}}', '"segments":[]}}', '"segments":[]]}}']:
    try:
        d=_j.loads('{"episodes":['+seg_blob+suffix)
        segs=[e for e in d['episodes'] if e['ep']==38][0]['segments']
        print('EP38 parsed with suffix', repr(suffix), 'segs', len(segs), 'ids', [s['id'] for s in segs])
        break
    except Exception as e:
        print('suffix fail', repr(suffix), str(e)[:50])