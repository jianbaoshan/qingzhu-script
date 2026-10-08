# -*- coding: utf-8 -*-
"""修复 batch-7 的 4 类质量门违规，改写各 _build/ep*.json fragment。

修复内容：
  1. camera-phrase / h3-structure：按分镜结构 + 保留原有英文正文，重建 h3Prompt，
     使每个 [Shot k] 切片都含该分镜的小写英文运镜词、对齐指令逐字对上。
  2. dialogue-fit：核对剧本 line 秒数，自动补足 cut.seconds 并在段内 ≤15 内再平衡。
  3. prompt-no-names：擦除 shot 里的禁角色名「卧龙」（卧龙岗→山岗，卧龙→那位隐士）。
"""
import json, io, os, math, re

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
SCRIPT = os.path.join(ROOT, "script.json")

CHARS_PER_SECOND = 4.5
ACTION_SECONDS = 2.5
MAX_SEG = 15.0
MIN_CUT = 2
MAX_CUT = 8

I2VA_LINE = 'For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.'
FIELD = ['integrated_multimodal_description:', 'overall_soundscape:', 'non_diegetic_music:']

def r1(n):
    return round(n * 10) / 10

def line_seconds(line):
    return r1(len(re.sub(r'\s+', '', str(line))) / CHARS_PER_SECOND)

def load_script():
    with io.open(SCRIPT, 'r', encoding='utf-8-sig') as f:
        script = json.load(f)
    eps = {}
    for ep in script.get('episodes', []):
        scenes = []
        for sc in (ep.get('scenes') or []):
            beats = []
            for j, b in enumerate((sc.get('flow') or [])):
                is_line = isinstance(b.get('line'), str)
                beats.append({
                    'n': j + 1,
                    'kind': 'line' if is_line else 'action',
                    'seconds': line_seconds(b['line']) if is_line else ACTION_SECONDS,
                    'text': b.get('line') if is_line else b.get('action'),
                })
            scenes.append(beats)
        eps[ep['ep']] = scenes
    return eps

def cut_dlg(beats, cut):
    fr, to = cut['beats']
    return r1(sum(b['seconds'] for b in beats[fr - 1: to] if b['kind'] == 'line'))

def min_sec(beats, cut):
    return max(MIN_CUT, math.ceil(cut_dlg(beats, cut) * 10 - 1e-9) / 10)

def cut_starts(cuts):
    starts, t = [], 0.0
    for c in cuts:
        starts.append(r1(t))
        t += c['seconds']
    return starts

def h3_cut_time(t):
    t = float(t)
    m = int(math.floor(t / 60))
    s = int(math.floor(t % 60))
    ms = int(round((t - math.floor(t)) * 1000))
    return '%02d:%02d.%03d' % (m, s, ms)

def alignment_line(cuts):
    if len(cuts) <= 1:
        return I2VA_LINE
    starts = cut_starts(cuts)
    parts = ['Picture %d (from Shot %d) aligns with the %s-second mark of the target video'
             % (i + 1, i + 1, ('%.2f' % starts[i])) for i in range(len(cuts))]
    return 'How the reference pictures align with the target video — ' + '; '.join(parts) + '.'

def extract_bodies(old_prompt, n):
    """从旧 h3Prompt 的描述正文里，按 [Shot k] 切片取出每镜的英文正文（含 <d>）。"""
    body_region = old_prompt
    i0 = body_region.find(FIELD[0])
    i1 = body_region.find(FIELD[1])
    if i0 < 0:
        return [None] * n
    body_region = body_region[i0 + len(FIELD[0]): i1 if i1 >= 0 else None]
    bodies = []
    for k in range(1, n + 1):
        mk = '[Shot %d]' % k
        a = body_region.find(mk)
        b = body_region.find('[Shot %d]' % (k + 1))
        if a < 0:
            bodies.append(None)
            continue
        sl = body_region[a: b if b >= 0 else None]
        p = sl.find('<Picture %d>' % k)
        colon = sl.find(':', p if p >= 0 else 0)
        txt = sl[colon + 1:].strip() if colon >= 0 else sl.strip()
        bodies.append(txt)
    return bodies

def extract_field(old_prompt, label):
    i = old_prompt.find(label)
    if i < 0:
        return ''
    rest = old_prompt[i + len(label):]
    # 遇到下一个字段名停下
    j = len(rest)
    for other in FIELD:
        k = rest.find(other)
        if k >= 0 and k < j:
            j = k
    return rest[:j].strip()

def build_h3(cuts, old_prompt):
    n = len(cuts)
    want = alignment_line(cuts)
    bodies = [None] * n
    if old_prompt:
        bodies = extract_bodies(old_prompt, n)
    sound = extract_field(old_prompt or '', FIELD[1])
    music = extract_field(old_prompt or '', FIELD[2])
    starts = cut_starts(cuts)
    lines = [want, '', FIELD[0]]
    for i, cut in enumerate(cuts):
        term = str(cut.get('camera') or 'Static Shot').lower()
        body = bodies[i] or ''
        k = i + 1
        if k == 1:
            lines.append('[Shot 1] A %s anchored on <Picture 1>: %s' % (term, body))
        else:
            lines.append('[Shot %d] At %s, the camera cuts to <Picture %d> in a %s: %s'
                         % (k, h3_cut_time(starts[i]), k, term, body))
    lines += ['', 'overall_soundscape: %s' % sound, '', 'non_diegetic_music: %s' % music]
    return '\n'.join(lines).rstrip('\n')

def scrub_shot(shot):
    s = shot
    s = s.replace('卧龙岗', '山岗')
    s = s.replace('那卧龙', '那位隐士')
    s = s.replace('卧龙', '那位隐士')
    return s

def fix_dialogue(seg, beats):
    # 1) 补足台词装不下的
    for cut in seg['cuts']:
        need = min_sec(beats, cut)
        if need > MAX_CUT:
            print('  !! %s 台词 %.1fs 超过 8s 上限，需拆切' % (seg['id'], need))
        cut['seconds'] = min(MAX_CUT, max(cut.get('seconds', MIN_CUT), need))
    # 2) 段内再平衡到 ≤15
    total = r1(sum(c['seconds'] for c in seg['cuts']))
    over = total - MAX_SEG
    if over > 1e-9:
        cands = []
        for cut in seg['cuts']:
            m = min_sec(beats, cut)
            slack = cut['seconds'] - m
            cands.append((cut, slack))
        cands.sort(key=lambda x: -x[1])
        idx = 0
        while over > 1e-9 and idx < len(cands):
            cut, slack = cands[idx]
            take = min(over, slack)
            if take > 1e-9:
                cut['seconds'] = r1(cut['seconds'] - take)
                over -= take
            idx += 1
        if over > 1e-9:
            print('  !! %s 段仍超 15s：%.1f（需人工重排）' % (seg['id'], r1(sum(c['seconds'] for c in seg['cuts']))))

def main():
    eps = load_script()
    EP_RANGE = range(31, 36)
    for epnum in EP_RANGE:
        path = os.path.join(BASE, 'ep%d.json' % epnum)
        with io.open(path, 'r', encoding='utf-8-sig') as f:
            segs = json.load(f)
        scenes = eps.get(epnum, [])
        changed_prompt = changed_sec = changed_shot = 0
        for seg in segs:
            sid = seg['id']
            si = seg.get('sceneIndex', 1) - 1
            beats = scenes[si] if si < len(scenes) else []
            # dialogue-fit
            old_secs = [c['seconds'] for c in seg['cuts']]
            fix_dialogue(seg, beats)
            if [c['seconds'] for c in seg['cuts']] != old_secs:
                changed_sec += 1
            # 擦名
            for cut in seg['cuts']:
                nw = scrub_shot(cut.get('shot', ''))
                if nw != cut.get('shot'):
                    cut['shot'] = nw
                    changed_shot += 1
            # 重建 h3Prompt
            old_p = seg.get('h3Prompt')
            nw_p = build_h3(seg['cuts'], old_p)
            if nw_p != old_p:
                seg['h3Prompt'] = nw_p
                changed_prompt += 1
        with io.open(path, 'w', encoding='utf-8') as f:
            json.dump(segs, f, ensure_ascii=False, indent=2)
        print('EP%d: 重写 h3Prompt %d 段 / 调秒 %d 段 / 擦名 %d 镜' %
              (epnum, changed_prompt, changed_sec, changed_shot))

if __name__ == '__main__':
    main()