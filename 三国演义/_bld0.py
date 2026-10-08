# -*- coding: utf-8 -*-
"""batch-8 builder: parse existing + author missing + harden + validate."""
import json, re, io, sys

P = r'd:\study\GitHub\shuohao-skills\三国演义\storyboard-batch-8.json'
SP = r'd:\study\GitHub\shuohao-skills\三国演义\script.json'

# ---- read current file (now valid through E38-15) ----
raw = open(P, encoding='utf-8-sig').read()
board = json.loads(raw)

script = json.load(open(SP, encoding='utf-8-sig'))

# ---- helpers mirroring novel-storyboard.mjs ----
def r1(x): return round(x*10)/10
def cutStarts(cuts):
    starts=[]; t=0
    for c in cuts:
        starts.append(r1(t)); t+=c['seconds']
    return starts
def h3CutTime(t):
    m=int(t//60); s=int(t%60); ms=round((t-int(t))*1000)
    return f"{m:02d}:{s:02d}.{ms:03d}"
ALIGN_HEAD='How the reference pictures align with the target video — '
def alignItem(k,t): return f"Picture {k} (from Shot {k}) aligns with the {t:.2f}-second mark of the target video"
def h3AlignmentLine(cuts):
    if len(cuts)<=1: return 'For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.'
    starts=cutStarts(cuts)
    parts=[alignItem(i+1, starts[i]) for i in range(len(cuts))]
    return ALIGN_HEAD + '; '.join(parts) + '.'

def segSeconds(seg): return r1(sum(c['seconds'] for c in seg['cuts']))

CAM='''Static Shot,Push In,Pull Out,Zoom In,Zoom Out,Pan Left,Pan Right,Truck Left,Truck Right,Tilt Up,Tilt Down,Pedestal Up,Pedestal Down,Arc Shot,Tracking Shot,Shake Slightly,Shake Strongly,POV,Roll Clockwise,Roll Counterclockwise'''.split(',')

def lineChars(x): return len(re.sub(r'\s+','',x))
def lineSec(l): return r1(lineChars(l)/4.5)

def parse_beats(ep):
    """returns list of scenes; each scene has beats list of {n,kind,speaker,text,seconds}"""
    out=[]
    for sc in ep['scenes']:
        beats=[]
        for j,it in enumerate(sc['flow']):
            if 'line' in it:
                beats.append(dict(n=j+1,kind='line',speaker=it['speaker'],
                                  text=it['line'], seconds=lineSec(it['line'])))
            else:
                beats.append(dict(n=j+1,kind='action',text=it['action'],seconds=2.5))
        out.append(dict(sceneId=sc['sceneId'], light=sc.get('lighting',''),
                        characters=sc.get('characters',[]), props=sc.get('props',[]),
                        beats=beats))
    return out

def scene_by_index(ep_script, idx):
    beats=parse_beats(ep_script)
    return beats[idx-1]

# Load episode script maps
SEP={ep['ep']:ep for ep in script['episodes']}

print('board episodes present:', [e['ep'] for e in board['episodes']], 'segs', [len(e['segments']) for e in board['episodes']])

# Show ep38 beat coverage currently claimed by existing segments
import collections
for ep in board['episodes']:
    if ep['ep']!=38: continue
    claims=collections.defaultdict(list)
    for seg in ep['segments']:
        for c in seg.get('cuts',[]):
            claims[seg['sceneIndex']].append((tuple(c['beats']), seg['id']))
    for si in sorted(claims):
        print('scene',si,'claims',sorted(claims[si], key=lambda x:x[0][0]))
    print('scenes in script:', len(SEP[38]['scenes']))