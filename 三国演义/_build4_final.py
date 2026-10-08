# -*- coding: utf-8 -*-
"""batch-4（第16–20集）最终分镜生成：读恢复数据 + 模板，重构 h3Prompt，写回 storyboard-batch-4.json。"""
import json, re, sys

BASE = r"d:\study\GitHub\shuohao-skills\三国演义"
REC = BASE + r"\_recovered_batch4_data.json"       # 93 段创意数据（sec/_h3）
TPL = BASE + r"\storyboard-batch-4.json"           # 目标（含 seedScenes beats、params）

recovered = json.load(open(REC, encoding="utf-8"))
tpl = json.load(open(TPL, encoding="utf-8"))

# ---------- 直接从恢复数据 / 模板取数 ----------
byEp = {int(k): v for k, v in recovered.items()}
source = tpl["source"]
promptLang = tpl["promptLang"]
params = tpl["params"]

# beats per (ep, sceneIndex) —— 从 script.json flow 重建（每场内部 1-based 编号，动作/台词都计数）
# NOTE: 模板 storyboard-batch-4.json 的 seedScenes 会被本脚本覆盖写掉，不能作数据源
SCRIPT = BASE + r"\script.json"
script = json.load(open(SCRIPT, encoding="utf-8"))
beatsByScene = {}
for epobj in script["episodes"]:
    ep = epobj["ep"]
    for si, sc in enumerate(epobj["scenes"], start=1):
        fl = []
        for b in sc["flow"]:
            if "line" in b:
                fl.append({"kind": "line", "text": b["line"]})
            else:
                fl.append({"kind": "action", "text": b.get("action", "")})
        beatsByScene[(ep, si)] = fl

# ---------- camera 修复映射 ----------
CAMERA_FIX = {"Pan Down": "Tilt Down", "Push Out": "Pull Out"}

# ---------- 每 (ep, scene) 英文 soundscape / music ----------
EN_SCENE = {
    (16, 1): ("Thundering hooves and the clang of steel, battle cries and panting breath.", "Low war drums and tense strings, driving."),
    (16, 2): ("The hush of a great hall, soft clinks of cups, the rustle of robes.", "Solemn courtly strings, stately."),
    (16, 3): ("Night wind in the eaves, a guttering lamp flame, distant footsteps of patrols.", "Sparse plucked strings, suspenseful."),
    (17, 1): ("Cicadas buzzing in the summer courtyard, wine simmering over low fire, plum fruit dropping.", "Light playful plucked strings, leisurely."),
    (17, 2): ("A sudden clap of thunder, the rattle of rafters, dust sifting from the beams.", "A sharp thunder-stab, then tense quiet strings."),
    (17, 3): ("Night wind crossing the courtyard, plum branches rustling, a lamp flame swaying.", "Low ambient drone and occasional plucks, brooding."),
    (18, 1): ("Dead night, a guttering flame, furtive footsteps, the rustle of hidden silk.", "Sparse tense plucks, sinister."),
    (18, 2): ("Hushed whispers in a sealed chamber, the scratch of quill on paper, candles sputtering.", "Low strings, grave and conspiratorial."),
    (18, 3): ("The stillness of the hall, a jade ring turning, wind passing the courtyard shrubs.", "Cold woodwinds, calculating."),
    (19, 1): ("The murmur of a banquet, cups clinking, armor plates knocking.", "Cordial wind and strings, deflating as tension rises."),
    (19, 2): ("Near silence, robes and armor shifting, lamplight wavering.", "Spare strings, probing and watchful."),
    (19, 3): ("Night wind at the window, a blade's cold gleam, the crackle of lamp oil.", "A lone flute over low drone, longing."),
    (20, 1): ("Warhorses snorting, hooves drumming, banners cracking in the wind.", "Heavy war drums and horns, swelling."),
    (20, 2): ("A sudden gasp, the whistle of a blade, blood hitting the dust, men recoiling.", "A sharp sting, then stunned silence."),
    (20, 3): ("Night wind around the tent, campfire crackling, thin fog drifting.", "Low drone and sparse plucks, ominous."),
}

CAMERA_OPEN = {
    "Static Shot": "A static shot of",
    "Push In": "A slow push in toward",
    "Pull Out": "A slow pull out from",
    "Pan Left": "A steady pan left across",
    "Pan Right": "A steady pan right across",
    "Tracking Shot": "A tracking shot following",
    "Tilt Down": "A slow tilt down over",
    "Tilt Up": "A slow tilt up over",
    "Arc Shot": "An arc shot around",
    "Zoom In": "A zoom in toward",
    "Zoom Out": "A zoom out from",
}

# ---------- H3 对齐指令 / 切点时刻（与 validator 完全一致） ----------
def r1(n):
    return round(n * 10) / 10

def cut_starts(cuts):
    starts, t = [], 0
    for c in cuts:
        starts.append(r1(t))
        t += c.get("seconds", c.get("sec", 0))
    return starts

def h3_cut_time(t):
    m = int(t) // 60
    s = int(t) % 60
    ms = round((t - int(t)) * 1000)
    return "%02d:%02d.%03d" % (m, s, ms)

I2VA = "For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced."

def alignment_line(cuts):
    if not cuts or len(cuts) <= 1:
        return I2VA
    starts = cut_starts(cuts)
    parts = ["Picture %d (from Shot %d) aligns with the %.2f-second mark of the target video" % (i + 1, i + 1, starts[i])
             for i in range(len(cuts))]
    return "How the reference pictures align with the target video \u2014 %s." % "; ".join(parts)

def build_h3(cuts, scene_en):
    """按 h3-prompt.md 骨架重构整条英文 H3。"""
    soundscape_en, music_en = scene_en
    lines = [alignment_line(cuts), "", "integrated_multimodal_description:"]
    starts = cut_starts(cuts)
    for i, c in enumerate(cuts):
        k = i + 1
        cam = CAMERA_FIX.get(c.get("camera", ""), c.get("camera", "Static Shot"))
        open_ph = CAMERA_OPEN.get(cam, "A static shot of")
        if k == 1:
            head = "[Shot 1] "
        else:
            head = "[Shot %d] At %s, " % (k, h3_cut_time(starts[i]))
        # 描述 = 镜头开篇（含相机词带 <Picture k>）+ _h3 原文 + 台词
        desc = str(c.get("_h3", "")).strip()
        if not desc:
            desc = "the scene continues."
        line = head + open_ph + " <Picture %d>: %s" % (k, desc[0].upper() + desc[1:])
        lines.append(line)
    lines.append("")
    lines.append("overall_soundscape: %s" % soundscape_en)
    lines.append("")
    lines.append("non_diegetic_music: %s" % music_en)
    return "\n".join(lines)

# ---------- dialog 替换：把 {d_n} 原位换成 <d>[Chinese] ...</d> ----------
# 占位符形如 {d_0}（下划线+编号）；用 {d_?\d*} 兼容 {d0} 与 {d_0}
D_RE = re.compile(r"\{d_?\d*\}")

# ---------- shot 修正（禁角色名 + 相机枚举） ----------
SHOT_FIX = [
    ("随曹操起身走下台阶", "随他起身走下台阶"),
    ("想起对面军中还坐着那个玄德", "想起对面军中坐着的那位故人"),
]
def fix_shot(shot):
    shot = shot.replace(" {d_0}.", ".").replace(" {d_0}", "").replace("{d_0}", "")
    for a, b in SHOT_FIX:
        shot = shot.replace(a, b)
    for a, b in CAMERA_FIX.items():
        shot = shot.replace(a, b.lower())
    return shot

# ---------- 组装 ----------
# ---------- 台词注入（按段，把每个 [Shot] 行里台词放对位） ----------
def inject_dialogues_h3(h3, seg, beat_slice, cuts):
    """在整条 h3 中，对每个 cut 认领行注入台词 <d> 块。"""
    import re as _re
    lines = h3.split("\n")
    shot_txt_by_k = {}
    for k, c in enumerate(cuts, start=1):
        fi, to = c["beats"]
        sub = [b for b in beat_slice[fi - 1:to] if b.get("kind") == "line"]
        if sub:
            shot_txt_by_k[k] = ["<d>[Chinese] %s</d>" % t.get("text", "") for t in sub]
    k = 0
    result = []
    for ln in lines:
        m = _re.match(r"^\[Shot (\d+)\]", ln)
        if m:
            k = int(m.group(1))
        if k in shot_txt_by_k and ln.strip().startswith("[Shot %d]" % k):
            blocks = shot_txt_by_k[k]
            new = _re.sub(r"\{d_?\d*\}", lambda mo: blocks.pop(0) if blocks else "", ln)
            if blocks:
                new = new.rstrip() + " " + " ".join(blocks)
            ln = new
        result.append(ln)
    return "\n".join(result)

new_episodes = []
for ep in sorted(byEp.keys()):
    segs = byEp[ep]
    nseg = 0
    built = []
    for s in segs:
        nseg += 1
        sid = "E%02d-%02d" % (ep, nseg)
        sceneKey = (ep, s["sceneIndex"])
        beat_slice = beatsByScene.get(sceneKey, [])
        scene_en = EN_SCENE.get(sceneKey)
        # h3 从「原始恢复 cuts」（带 _h3/beats/seconds）构建，不掺最终落地字段
        h3 = build_h3(s["cuts"], scene_en)
        final_h3 = inject_dialogues_h3(h3, s, beat_slice, s["cuts"])
        cuts = []
        for c in s["cuts"]:
            cam = CAMERA_FIX.get(c.get("camera", ""), c.get("camera", "Static Shot"))
            cut = {
                "beats": c["beats"],
                "seconds": c["sec"],
                "size": c["size"],
                "camera": cam,
                "characters": c.get("characters", []),
            }
            if c.get("props"):
                cut["props"] = c["props"]
            cut["frame"] = c["frame"]
            cut["shot"] = fix_shot(c.get("shot", ""))
            for f in ("lens", "cameraPosition", "composition", "eyeline", "focus", "stability"):
                cut[f] = c.get(f, "")
            if c.get("note"):
                cut["note"] = c["note"]
            cuts.append(cut)
        seg = {
            "id": sid,
            "sceneIndex": s["sceneIndex"],
            "cuts": cuts,
            "blocking": s["blocking"],
            "soundscape": s["soundscape"],
        }
        music = s.get("music")
        if music and str(music).strip().lower() != "none" and str(music).strip():
            seg["music"] = music
        seg["h3Prompt"] = final_h3
        built.append(seg)
    new_episodes.append({"ep": ep, "segments": built})

out = {
    "source": source,
    "promptLang": promptLang,
    "params": params,
    "episodes": new_episodes,
}

outpath = BASE + r"\storyboard-batch-4.json"
with open(outpath, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("WROTE", outpath)
print("episodes:", [(e["ep"], len(e["segments"])) for e in new_episodes])
tot_cut = sum(len(e["segments"]) for e in new_episodes)
tot_sec = 0
for e in new_episodes:
    for s in e["segments"]:
        tot_sec += sum(c["seconds"] for c in s["cuts"])
print("total segments", tot_cut, "total seconds", round(tot_sec, 1))