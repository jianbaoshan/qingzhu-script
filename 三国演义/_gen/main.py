# -*- coding: utf-8 -*-
"""batch-10 generator: assemble ep46-50 segments, build h3Prompt, validate, write back."""
import importlib.util
import io
import json
import math
import re
import sys

DIR = r"d:\study\GitHub\shuohao-skills\三国演义"
BATCH = DIR + r"\storyboard-batch-10.json"
GEN = DIR + r"\_gen"

SHOT_SIZES = {
    'extreme-wide': '大远景', 'wide': '全景', 'medium': '中景',
    'close': '特写', 'extreme-close': '大特写',
}
CAMERA_MOVES = ['Static Shot', 'Push In', 'Pull Out', 'Zoom In', 'Zoom Out',
                'Pan Left', 'Pan Right', 'Truck Left', 'Truck Right',
                'Tilt Up', 'Tilt Down', 'Pedestal Up', 'Pedestal Down',
                'Arc Shot', 'Tracking Shot', 'Shake Slightly', 'Shake Strongly',
                'POV', 'Roll Clockwise', 'Roll Counterclockwise']
STABILITY = ['stable', 'slight-shake', 'handheld']
COMPOSITION_FIELDS = ['lens', 'cameraPosition', 'composition', 'eyeline', 'focus', 'stability']

# ensure exact camera term appears inside each [Shot k] body
CAMERA_APPEND = {
    'Static Shot': ' the camera holds a static shot',
    'Push In': ' the camera performs a push in',
    'Pull Out': ' the camera performs a pull out',
    'Zoom In': ' the camera performs a zoom in',
    'Zoom Out': ' the camera performs a zoom out',
    'Pan Left': ' the camera performs a pan left',
    'Pan Right': ' the camera performs a pan right',
    'Truck Left': ' the camera performs a truck left',
    'Truck Right': ' the camera performs a truck right',
    'Tilt Up': ' the camera performs a tilt up',
    'Tilt Down': ' the camera performs a tilt down',
    'Pedestal Up': ' the camera performs a pedestal up',
    'Pedestal Down': ' the camera performs a pedestal down',
    'Arc Shot': ' the camera performs an arc shot',
    'Tracking Shot': ' the camera makes a tracking shot',
    'Shake Slightly': ' a shake slightly rocks the frame',
    'Shake Strongly': ' a shake strongly jolts the frame',
    'POV': ' shown from a direct pov',
    'Roll Clockwise': ' the camera performs a roll clockwise',
    'Roll Counterclockwise': ' the camera performs a roll counterclockwise',
}

H3_I2VA = ('For the target video, at 0.00 seconds into the target video, '
           '<Picture 1> (from [Shot 1]) is fully referenced.')


def r1(n):
    return round(n * 10) / 10


def cut_starts(cuts):
    starts, t = [], 0.0
    for c in cuts:
        starts.append(r1(t))
        t += c['seconds']
    return starts


def h3_cut_time(t):
    m = int(t // 60)
    s = int(t % 60)
    ms = round((t - math.floor(t)) * 1000)
    return "%02d:%02d.%03d" % (m, s, ms)


def h3_alignment_line(cuts):
    if len(cuts) <= 1:
        return H3_I2VA
    starts = cut_starts(cuts)
    parts = ["Picture %d (from Shot %d) aligns with the %.2f-second mark of the target video"
             % (i + 1, i + 1, starts[i]) for i in range(len(cuts))]
    return "How the reference pictures align with the target video — " + "; ".join(parts) + "."


def build_cut_output(cut):
    return {
        'beats': list(cut['beats']),
        'seconds': cut['seconds'],
        'size': cut['size'],
        'camera': cut['camera'],
        'characters': list(cut['chars']),
        'frame': cut['frame'],
        'shot': cut['shot'],
        'lens': cut['lens'],
        'cameraPosition': cut['cameraPosition'],
        'composition': cut['composition'],
        'eyeline': cut['eyeline'],
        'focus': cut['focus'],
        'stability': cut['stability'],
    }


def build_h3_prompt(seg):
    cuts = seg['cuts']
    line = h3_alignment_line(cuts)
    starts = cut_starts(cuts)
    bodies = []
    for i, c in enumerate(cuts):
        if i == 0:
            prefix = "[Shot 1]"
        else:
            prefix = "[Shot %d] At %s," % (i + 1, h3_cut_time(starts[i]))
        bodies.append(prefix + " " + c['h3'].strip() + CAMERA_APPEND[c['camera']])
    return (line + "\n\n"
            + "integrated_multimodal_description:\n" + "\n".join(bodies) + "\n"
            + "overall_soundscape: " + seg['h3_sound'].strip() + "\n"
            + "non_diegetic_music: " + seg['h3_music'].strip())


def load_data(ep):
    spec = importlib.util.spec_from_file_location("data%d" % ep, GEN + r"\data%d.py" % ep)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.SEG


def scene_beats(episode):
    """{sceneIndex: [beat dicts]} from seedScenes."""
    out = {}
    for sc in episode['seedScenes']:
        out[sc['sceneIndex']] = {
            'characters': sc.get('characters', []),
            'props': sc.get('props', []),
            'beats': sc.get('beats', []),
        }
    return out


# ---- validation helpers ----
errors = []
def err(msg):
    errors.append(msg)


def validate(ep_logical_ep, ep_segments, scenes):
    for seg in ep_segments:
        sid = seg['id']
        total = r1(sum(c['seconds'] for c in seg['cuts']))
        if not (total > 0) or total > 15:
            err("%s segment-cap: %.1f 秒" % (sid, total))
        scene = scenes.get(seg['sceneIndex'])
        if scene is None or not seg['cuts']:
            err("%s 场次 %s 无脚本" % (sid, seg['sceneIndex']))
            continue
        cast = set(scene['characters'])
        prop_set = set(scene['props'])
        # h3 structure self-check
        h3 = seg['h3Prompt']
        f0, f1, f2 = (h3.find(x) for x in
                      ['integrated_multimodal_description:', 'overall_soundscape:', 'non_diegetic_music:'])
        if not (f0 >= 0 and f1 >= 0 and f2 >= 0 and f0 < f1 < f2):
            err("%s 三个 h3 字段缺失或顺序不对" % sid)
        starts = cut_starts(seg['cuts'])
        for i, c in enumerate(seg['cuts']):
            ci = "%s#%d" % (sid, i + 1)
            if not (2 <= c['seconds'] <= 8):
                err("%s cutLen: %.1f" % (ci, c['seconds']))
            if len(c['characters']) > 3 and not (seg.get('note') or c.get('note')):
                err("%s 同框 %d 人无拆解" % (ci, len(c['characters'])))
            for ch in c['characters']:
                if ch not in cast:
                    err("%s refs: %s 不在剧本该场人物" % (ci, ch))
            for pr in c.get('props', []):
                if pr not in prop_set:
                    err("%s props: %s 不在剧本" % (ci, pr))
            if c['size'] not in SHOT_SIZES:
                err("%s 景别 %s 不在枚举" % (ci, c['size']))
            elif SHOT_SIZES[c['size']] not in c['frame']:
                err("%s frame 缺景别词 %s" % (ci, SHOT_SIZES[c['size']]))
            if not re.search(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]', c['frame']):
                err("%s frame 非中文" % ci)
            if c['camera'] not in CAMERA_MOVES:
                err("%s 运镜 %s 不在词表" % (ci, c['camera']))
            if not c['frame'].strip():
                err("%s frame 空" % ci)
            for fld in COMPOSITION_FIELDS:
                if not str(c.get(fld, '')).strip():
                    err("%s 缺 %s" % (ci, fld))
            if c.get('stability') not in STABILITY:
                err("%s stability %s 不在枚" % (ci, c.get('stability')))
            # shot text checks
            shot = c.get('shot', '')
            if not shot.strip():
                err("%s 缺 shot" % ci)
            elif not re.search(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]', shot):
                err("%s shot 非中文" % ci)
            # dialogue fit + <d>
            dlg = 0.0
            for b in scene['beats'][c['beats'][0] - 1: c['beats'][1]]:
                if b.get('kind') == 'line':
                    dlg += b['seconds']
            if dlg > c['seconds']:
                err("%s 台词 %.1f 装不进 %.1f" % (ci, dlg, c['seconds']))
            # camera term in slice
            body_start = h3.find('integrated_multimodal_description:')
            body_end = h3.find('overall_soundscape:')
            body = h3[body_start if body_start >= 0 else 0: body_end if body_end >= 0 else None]
            a = body.find('[Shot %d]' % (i + 1))
            b = body.find('[Shot %d]' % (i + 2))
            sl = body[a: b if b >= 0 else None].lower()
            if c['camera'].lower() not in sl:
                err("%s [Shot %d] 缺运镜词 %s" % (ci, i + 1, c['camera'].lower()))
    # beat coverage per scene
    for sc_idx, sc in scenes.items():
        claims = []
        for seg in ep_segments:
            if seg['sceneIndex'] != sc_idx:
                continue
            for c in seg['cuts']:
                claims.append([c['beats'][0], c['beats'][1]])
        n = len(sc['beats'])
        cursor = 1
        for (f_, to_) in claims:
            if f_ < 1 or to_ > n or f_ > to_:
                err("E%02d 场%d 区间 [%d,%d] 不合法（共 %d 拍）" % (ep_logical_ep, sc_idx, f_, to_, n))
            if f_ != cursor:
                err("E%02d 场%d 第 %d 拍%s" % (ep_logical_ep, sc_idx, cursor,
                    "没人认领" if f_ > cursor else "重复认领"))
            cursor = max(cursor, to_ + 1)
        if claims and cursor <= n:
            err("E%02d 场%d 第 %d-%d 拍没人认领" % (ep_logical_ep, sc_idx, cursor, n))
        if not claims and n:
            err("E%02d 场%d 整场无分镜" % (ep_logical_ep, sc_idx))


def main():
    raw = io.open(BATCH, 'r', encoding='utf-8-sig').read()
    board = json.loads(raw)
    params = board['params']
    tolerance = params.get('tolerance', 0.15)

    result_episodes = []
    for ep in board['episodes']:
        logical = ep['ep']
        scenes = scene_beats(ep)
        segs = load_data(logical)
        out_segs = []
        for i, seg in enumerate(segs):
            seg_out = {
                'id': "E%02d-%02d" % (logical, i + 1),
                'sceneIndex': seg['sceneIndex'],
                'cuts': [build_cut_output(c) for c in seg['cuts']],
                'h3Prompt': build_h3_prompt(seg),
                'blocking': seg['blocking'],
                'soundscape': seg['soundscape'],
                'music': seg['music'],
            }
            out_segs.append(seg_out)
        validate(logical, out_segs, scenes)
        total = r1(sum(r1(sum(c['seconds'] for c in s['cuts'])) for s in out_segs))
        target = 180.0
        lo, hi = target * (1 - tolerance), target * (1 + tolerance)
        if total < lo or total > hi:
            err("E%02d 总时长 %s 秒不在 [%.0f, %.0f]" % (logical, total, lo, hi))
        else:
            print("E%02d OK: %d segs, %d cuts, %.1fs / 目标 180" %
                  (logical, len(out_segs), sum(len(s['cuts']) for s in out_segs), total))
        result_episodes.append({'ep': logical, 'segments': out_segs})

    if errors:
        print("\n==== 校验失败 %d 条 ====" % len(errors))
        for e in errors:
            print(" -", e)
        sys.exit(1)

    new_board = {
        'source': board.get('source'),
        'promptLang': board.get('promptLang', 'en'),
        'params': params,
        'episodes': result_episodes,
    }
    out_json = json.dumps(new_board, ensure_ascii=False, indent=2)
    io.open(BATCH, 'w', encoding='utf-8', newline='\n').write(out_json)
    print("\n写回完成：episodes =", len(result_episodes),
          " 段 =", sum(len(e['segments']) for e in result_episodes),
          " 切 =", sum(len(s['cuts']) for e in result_episodes for s in e['segments']))


if __name__ == '__main__':
    main()