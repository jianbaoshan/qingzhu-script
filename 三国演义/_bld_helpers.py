# -*- coding: utf-8 -*-
"""batch-8 shared helpers."""
import json, re

P = r'd:\study\GitHub\shuohao-skills\三国演义\storyboard-batch-8.json'
SP = r'd:\study\GitHub\shuohao-skills\三国演义\script.json'

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

def make_cut(beats, seconds, size, camera, characters, props, frame, shot, cpos, comp, eyeline, focus, stability='stable', lens=None):
    lens = lens or {'wide':'35mm 广角，中等景深','medium':'50mm 标准，中浅景深','close':'85mm 长焦，浅景深','extreme-wide':'24mm 广角，深景深','extreme-close':'100mm 长焦，极浅景深'}[size]
    return dict(beats=list(beats), seconds=seconds, size=size, camera=camera, characters=characters,
                props=props, frame=frame, shot=shot, lens=lens, cameraPosition=cpos,
                composition=comp, eyeline=eyeline, focus=focus, stability=stability)

def seg_from_specs(segid, scene_index, specs, epno, overall_sound, music_en, script):
    cuts=[]; descs=[]
    for sp in specs:
        cut=make_cut(sp['beats'],sp['sec'],sp['size'],sp['camera'],sp['chars'],
                     sp.get('props',[]),sp['frame'],sp['shot'],sp['cpos'],
                     sp['comp'],sp['eye'],sp['foc'],stability=sp.get('stability','stable'))
        hbody=sp['h3']
        sc = script['episodes'][epno-1]['scenes'][scene_index-1]
        dlg=[]
        for bi in range(sp['beats'][0]-1, sp['beats'][1]):
            b=sc['flow'][bi]
            if 'line' in b: dlg.append(b)
        desc=hbody
        if dlg:
            extra=' '.join(f'<d>[Chinese] {b["line"]}</d>' for b in dlg)
            desc=desc+'  '+extra
        descs.append(desc); cuts.append(cut)
    total=round(sum(c['seconds'] for c in cuts),1)
    assert total<=15, f"{segid} {total}s>15"
    h3=build_h3(cuts, descs, overall_sound, music_en)
    return dict(id=segid, sceneIndex=scene_index, cuts=cuts, h3Prompt=h3)