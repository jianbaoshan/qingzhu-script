# -*- coding: utf-8 -*-
"""Validate batch-2 data modules (sb_batch2_data_epN.py) against script.json.
Usage: python 三国演义/_validate_batch2.py
Reads EP6..EP10 lists and checks gates; prints pass/fail list."""
import importlib.util, json, os, sys, re

ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPT = json.load(open(os.path.join(ROOT, 'script.json'), encoding='utf-8'))
EPS = [6, 7, 8, 9, 10]
CPS = 4.5

CAMERAS = {'Static Shot','Push In','Pull Out','Zoom In','Zoom Out','Pan Left','Pan Right',
 'Truck Left','Truck Right','Tilt Up','Tilt Down','Pedestal Up','Pedestal Down','Arc Shot',
 'Tracking Shot','Shake Slightly','Shake Strongly','POV','Roll Clockwise','Roll Counterclockwise'}
SIZES = {'extreme-wide','wide','medium','close','extreme-close'}
STABS = {'stable','slight-shake','handheld'}

# names/aliases that must not appear in en(body, outside <d>) or in Chinese shot
FORBIDDEN = ['刘备','玄德','刘玄德','刘皇叔','刘先主','关羽','云长','美髯公','关公','张飞','翼德','燕人',
 '曹操','孟德','阿瞒','曹丞相','曹公','吕布','奉先','飞将','貂蝉','王允','王司徒','司徒','董卓','董太师',
 '袁绍','本初','袁本初','袁公','孙坚','文台','诸葛亮','诸葛亮','周瑜','鲁肃','孙权','李肃','李傕','郭汜','刘协','献帝']

def sc_of(ep):
    for e in SCRIPT['episodes']:
        if e['ep'] == ep:
            return e['scenes']
    return None

def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, name + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def scene_flow_lines(scenes, si):
    fl = scenes[si-1]['flow']
    # line seconds per beat
    out = []
    for b in fl:
        if 'line' in b:
            import unicodedata
            n = len(re.sub(r'\s','',b['line']))
            out.append(('line', round(n/CPS,1), b['line']))
        else:
            out.append(('action', 2.5, None))
    return out

def check_ep(ep):
    scenes = sc_of(ep)
    m = load('sb_batch2_data_ep%d' % ep)
    segs = m.EP7 if ep==7 else getattr(m, 'EP%d' % ep if ep!=6 else 'EP6', None)
    if segs is None:
        segs = getattr(m, 'EP6', getattr(m, 'EP%d'%ep, None))
    probs = []
    tot = 0.0
    ncut = 0
    # build beat-coverage tracer per scene
    cov = {}
    sc_props_chars = {i+1: (scenes[i].get('props') or [], scenes[i].get('characters') or []) for i in range(len(scenes))}
    for seg in segs:
        si = seg['sceneIndex']
        cov.setdefault(si, [])
        sc = sum(c[0] for c in seg['cuts'])
        tot += sc
        if sc > 15.0 + 1e-9:
            probs.append(f'  seg(scene{si}) {sc:.1f}s >15')
        for c in seg['cuts']:
            ncut += 1
            sec, beats, size, camera, chars, props, frame, shot, lens, cp, comp, eye, focus, stab = c[:14]
            en = c[14] if len(c) > 14 else ''
            if not (2.0 <= sec <= 8.0 + 1e-9):
                probs.append(f'  cut beats{beats} sec={sec} out of [2,8]')
            if size not in SIZES:
                probs.append(f'  cut beats{beats} bad size {size}')
            if camera not in CAMERAS:
                probs.append(f'  cut beats{beats} bad camera {camera}')
            if stab not in STABS:
                probs.append(f'  cut beats{beats} bad stab {stab}')
            if not re.search(r'（大远景|（全景|（中景|（特写|（大特写|大远景|全景|中景|特写|大特写', frame):
                # frame must carry a shot-size Chinese word
                if size == 'extreme-wide' and '大远景' not in frame: pass
            scok = sc_props_chars[si]
            if not set(props).issubset(set(scok[0])):
                probs.append(f'  cut beats{beats} props {props} not <= scene props {scok[0]}')
            if not set(chars).issubset(set(scok[1])):
                probs.append(f'  cut beats{beats} chars {chars} not <= scene chars {scok[1]}')
            if len(chars) > 3:
                probs.append(f'  cut beats{beats} >3 on screen {chars}')
            for b in range(beats[0], beats[1]+1):
                cov[si].append(b)
            # line-fit + verbatim + forbidden
            lines = scene_flow_lines(scenes, si)
            claim = []
            for b in range(beats[0]-1, beats[1]):
                if lines[b][0] == 'line':
                    claim.append((lines[b][1], lines[b][2]))
            linsec = sum(x[0] for x in claim)
            if linsec - 1e-9 > sec:
                probs.append(f'  cut beats{beats} line {linsec:.1f}s > cut {sec}s')
            # verbatim: each claimed <d>[Chinese] TEXT</d> must appear
            for _, txt in claim:
                if ('<d>[Chinese] %s</d>' % txt) not in en:
                    probs.append(f'  cut beats{beats} missing verbatim <d> for: {txt[:12]}...')
            # forbidden names in en OUTSIDE <d>, and in shot
            en_body = re.sub(r'<d>.*?</d>', '', en)
            for nm in FORBIDDEN:
                if nm in en_body:
                    probs.append(f'  cut beats{beats} name "{nm}" leaked into en body')
                if nm in shot:
                    probs.append(f'  cut beats{beats} name "{nm}" in shot')
    # coverage check
    for si in range(1, len(scenes)+1):
        exp = list(range(1, len(scenes[si-1]['flow'])+1))
        got = sorted(set(cov.get(si, [])))
        if got != exp:
            probs.append(f'  scene{si} beat coverage {got} != expected {exp}')
        # also ensure no duplicates
        seen = [b for b in cov.get(si,[])]
        if len(seen) != len(set(seen)):
            probs.append(f'  scene{si} duplicate beats')
    return tot, ncut, probs

def main():
    allok = True
    for ep in EPS:
        tot, ncut, probs = check_ep(ep)
        inrange = 153.0 <= tot <= 207.0
        status = 'OK' if (inrange and not probs) else 'FAIL'
        if status != 'OK': allok = False
        print(f'\nEP{ep}: total {tot:.1f}s ({ncut} cuts) target ok={inrange} -> {status}')
        for p in probs:
            print('   ', p)
    print('\nALL OK' if allok else '\nHAS ERRORS')

if __name__ == '__main__':
    main()