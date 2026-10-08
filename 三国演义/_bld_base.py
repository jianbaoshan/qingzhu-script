# -*- coding: utf-8 -*-
"""batch-8 builder (step 1): helpers + existing segment extraction + new segment authoring + assembly."""
import json, re, pickle

P = r'd:\study\GitHub\shuohao-skills\三国演义\storyboard-batch-8.json'
SP = r'd:\study\GitHub\shuohao-skills\三国演义\script.json'

# ---------- load existing authored segments (eps 36,37,38-01..15) ----------
raw = open(P, encoding='utf-8-sig').read()
suffix='\n        }\n      ]\n    },\n    {"ep":39,"segments":[]},\n    {"ep":40,"segments":[]}\n  ]\n}\n'
board = json.loads(raw + suffix)
script = json.load(open(SP, encoding='utf-8-sig'))
SEP = {ep['ep'] for ep in board['episodes']}

# ---------- helpers (mirror novel-storyboard.mjs) ----------
def r1(x): return round(x*10)/10
def lineChars(l): return len(re.sub(r'\s+','',l))
def lineSec(l): return r1(lineChars(l)/4.5)

def cutStarts(cuts):
    starts=[]; t=0
    for c in cuts: starts.append(r1(t)); t+=c['seconds']
    return starts
def h3CutTime(t):
    m=int(t//60); s=int(t%60); ms=round((t-int(t))*1000)
    return f"{m:02d}:{s:02d}.{ms:03d}"
ALIGN_HEAD='How the reference pictures align with the target video — '
def h3AlignmentLine(cuts):
    if len(cuts)<=1:
        return 'For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.'
    starts=cutStarts(cuts)
    parts=[f"Picture {i+1} (from Shot {i+1}) aligns with the {starts[i]:.2f}-second mark of the target video" for i in range(len(cuts))]
    return ALIGN_HEAD + '; '.join(parts) + '.'

def build_h3(cuts, shot_desc_en, overall_sound, music_en):
    """cuts: list of cut dicts; shot_desc_en: list of English body strings (without [Shot k] prefix),
       each may contain (S1)/(S2) and <d>...</d> already. overall_sound/music_en: english."""
    line_align = h3AlignmentLine(cuts)
    parts=[line_align, '', 'integrated_multimodal_description:']
    for i,c in enumerate(cuts):
        k=i+1
        if k==1:
            parts.append(f"[Shot 1] {shot_desc_en[i]}")
        else:
            t=h3CutTime(cutStarts(cuts)[i])
            parts.append(f"[Shot {k}] At {t}, {shot_desc_en[i]}")
    parts += ['', 'overall_soundscape: '+overall_sound, '', 'non_diegetic_music: '+music_en]
    return '\n'.join(parts)

def make_cut(beats, seconds, size, camera, characters, props, frame, shot, cpos, comp, eyeline, focus, stability='stable', lens=None, hn=None):
    # hn = English shot description body for h3 (optional; if None generated basic)
    lens = lens or {'wide':'35mm 广角，中等景深','medium':'50mm 标准，中浅景深','close':'85mm 长焦，浅景深','extreme-wide':'24mm 广角，深景深','extreme-close':'100mm 长焦，极浅景深'}[size]
    return dict(beats=list(beats), seconds=seconds, size=size, camera=camera, characters=characters,
                props=props, frame=frame, shot=shot, lens=lens, cameraPosition=cpos,
                composition=comp, eyeline=eyeline, focus=focus, stability=stability)

# save helpers for later steps
import builtins
ctx = dict(raw=raw,suffix=suffix,board=board,script=script,SEP=SEP,
           r1=r1,lineSec=lineSec,cutStarts=cutStarts,h3CutTime=h3CutTime,
           h3AlignmentLine=h3AlignmentLine,build_h3=build_h3,make_cut=make_cut)
pickle.dump(ctx, open(r'd:\study\GitHub\shuohao-skills\三国演义\_ctx.pkl','wb'))
print('ctx saved. episodes:', [e['ep'] for e in board['episodes']], 'segCounts', [len(e['segments']) for e in board['episodes']])