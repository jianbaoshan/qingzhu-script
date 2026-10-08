# -*- coding: utf-8 -*-
"""batch-2 (EP6-10) assembly: read sb_batch2_data_epN.py -> fill storyboard-batch-2.json
segments (id/sceneIndex/cuts/h3Prompt/blocking/soundscape/music), drop seedScenes, write back.
h3Prompt generation mirrors _build.mjs.  cut tuples:
(seconds, beats, size, camera, chars, props, frame, shot, lens, camPos, comp, eye, focus, stab, en)
en absent on action cuts -> 14-tuple.
"""
import importlib.util, json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(ROOT, 'storyboard-batch-2.json')
EPS = [6, 7, 8, 9, 10]
FIELDS = ['seconds','beats','size','camera','characters',
          'frame','shot','lens','cameraPosition','composition',
          'eyeline','focus','stability']

def r1(n): return round(n * 10.0) / 10.0

def cut_starts(cuts):
    s, t = [], 0.0
    for c in cuts:
        s.append(r1(t)); t += c['seconds']
    return s

def h3_cut_time(t):
    m = int(t) // 60; s = int(t) % 60
    ms = round((t - int(t)) * 1000)
    return '%02d:%02d.%03d' % (m, s, ms)

I2VA = ('For the target video, at 0.00 seconds into the target video, '
        '<Picture 1> (from [Shot 1]) is fully referenced.')
AH = 'How the reference pictures align with the target video \u2014 '

def align_line(cuts):
    if not cuts or len(cuts) <= 1:
        return I2VA
    st = cut_starts(cuts)
    parts = ['Picture %d (from Shot %d) aligns with the %.2f-second mark of the target video' % (i + 1, i + 1, st[i])
             for i in range(len(cuts))]
    return AH + '; '.join(parts) + '.'

def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, name + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

CAMERA_PHRASE = {'Static Shot':'static shot','Push In':'push in','Pull Out':'pull out',
 'Pan Left':'pan left','Pan Right':'pan right','Truck Left':'truck left','Truck Right':'truck right',
 'Tilt Up':'tilt up','Tilt Down':'tilt down','Arc Shot':'arc around','Tracking Shot':'tracking shot',
 'Zoom In':'zoom in','Zoom Out':'zoom out','Pedestal Up':'pedestal up','Pedestal Down':'pedestal down',
 'Shake Slightly':'handheld shake','Shake Strongly':'strong shake','POV':'point-of-view shot',
 'Roll Clockwise':'roll','Roll Counterclockwise':'roll'}

def build_ep(ep, raw_segs):
    out = []
    seg_idx = 0
    for sg in raw_segs:
        seg_idx += 1
        overall = sg.get('overall', '')
        used_overall = False
        cuts = []
        for t in raw_segs and sg['cuts']:
            sec, beats, size, camera, chars, props, frame = t[0], t[1], t[2], t[3], t[4], t[5], t[6]
            shot = t[7]; lens = t[8]; campos = t[9]; comp = t[10]; eye = t[11]
            focus = t[12]; stab = t[13]
            en = t[14] if len(t) > 14 else ''
            if en:
                body = en
            else:
                # action cut without english body: first uses scene overall,
                # later ones a natural camera-phrase continuation.
                if not used_overall:
                    body = overall; used_overall = True
                else:
                    body = 'the action proceeds with a %s.' % CAMERA_PHRASE.get(camera, 'static shot')
            cuts.append(dict(seconds=sec, beats=beats, size=size, camera=camera,
                             characters=chars, frame=frame, shot=shot, lens=lens,
                             cameraPosition=campos, composition=comp, eyeline=eye,
                             focus=focus, stability=stab, _body=body,
                             _props=props, _en=en))
        starts = cut_starts(cuts)
        body_lines = []
        for ci, c in enumerate(cuts):
            k = ci + 1
            head = '[Shot %d] ' % k if k == 1 else '[Shot %d] At %s, ' % (k, h3_cut_time(starts[ci]))
            term = str(c['camera']).lower()
            text = head + c['_body']
            if term not in text.lower():
                text = head + term + '. ' + c['_body']
            body_lines.append(text)
        h3 = ('%s\n\nintegrated_multimodal_description:\n%s\n\noverall_soundscape: %s'
              '\n\nnon_diegetic_music: %s\n' % (align_line(cuts), '\n'.join(body_lines),
              sg.get('overall', ''), sg.get('music_en', '')))
        store_cuts = []
        for c in cuts:
            cut = {fld: c[fld] for fld in FIELDS}
            if c['_props']:
                cut['props'] = c['_props']
            store_cuts.append(cut)
        seg = {'id': 'E%02d-%02d' % (ep, seg_idx), 'sceneIndex': sg['sceneIndex'],
               'cuts': store_cuts, 'blocking': sg.get('blocking', ''),
               'soundscape': sg.get('soundscape', '')}
        music = sg.get('music')
        if music and str(music).strip().lower() not in ('', 'none'):
            seg['music'] = music
        seg['h3Prompt'] = h3
        out.append(seg)
    return out

board = json.load(open(TPL, encoding='utf-8-sig'))
episodes = [{'ep': ep, 'segments': build_ep(ep, getattr(load('sb_batch2_data_ep%d' % ep), 'EP%d' % ep))} for ep in EPS]
board['episodes'] = episodes

with open(TPL, 'w', encoding='utf-8-sig') as f:
    json.dump(board, f, ensure_ascii=False, indent=2)

# ---- self-check summary ----
tot_seg = tot_cut = 0; tot_sec = 0.0
for e in episodes:
    nseg = len(e['segments']); ncut = 0; sec = 0.0
    for s in e['segments']:
        ncut += len(s['cuts'])
        sec += sum(c['seconds'] for c in s['cuts'])
    tot_seg += nseg; tot_cut += ncut; tot_sec += sec
    print('EP%02d segments=%d cuts=%d %.1fs' % (e['ep'], nseg, ncut, round(sec, 1)))
print('TOTAL segments=%d cuts=%d %.1fs' % (tot_seg, tot_cut, round(tot_sec, 1)))
print('seedScenes removed:', all('seedScenes' not in e for e in episodes))
print('WROTE', TPL)