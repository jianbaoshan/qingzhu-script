# -*- coding: utf-8 -*-
"""合并各集 fragment(ep31-35.json) 为最终 storyboard-batch-7.json，并做基础校验。"""
import json, io, sys, re, os

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
OUT = os.path.join(ROOT, "storyboard-batch-7.json")

EP_RANGE = range(31, 36)  # 31..35

params = {
    "maxSegmentSeconds": 15,
    "minCutSeconds": 2,
    "maxCutSeconds": 8,
    "maxOnScreen": 3,
    "tolerance": 0.15,
}

total_segments = 0
total_cuts = 0
total_seconds = 0.0
all_ok = True

episodes = []
for ep in EP_RANGE:
    frag_path = os.path.join(BASE, "ep%d.json" % ep)
    with io.open(frag_path, "r", encoding="utf-8-sig") as f:
        segs = json.load(f)
    if not isinstance(segs, list):
        raise SystemExit("fragment %s 不是数组" % frag_path)

    # 每段内部校验；beats 按场(sceneIndex)连续，跨段累计、换场时重置
    seg_seconds = 0.0
    prev_scene = None
    prev_beats_hi = 0
    for si, seg in enumerate(segs, 1):
        assert "id" in seg and seg["id"].startswith("E%d-" % ep), "段缺少/错误 id: %s" % seg.get("id")
        assert "sceneIndex" in seg
        scene = seg["sceneIndex"]
        assert "h3Prompt" in seg and isinstance(seg["h3Prompt"], str) and seg["h3Prompt"].strip(), \
            "%s 缺 h3Prompt" % seg["id"]
        assert "blocking" in seg and "soundscape" in seg
        assert "cuts" in seg and isinstance(seg["cuts"], list) and len(seg["cuts"]) >= 1, \
            "%s 无 cuts" % seg["id"]

        if scene != prev_scene:
            prev_beats_hi = 0
            prev_scene = scene

        cut_total = 0.0
        for c in seg["cuts"]:
            s = c["seconds"]
            assert isinstance(s, (int, float)) and 2 <= s <= 8, "%s 镜头秒数越界: %s" % (seg["id"], s)
            cut_total += s
            # 六构图 + beats + characters + frame/shot
            for k in ("beats","seconds","size","camera","characters","frame","shot",
                      "lens","cameraPosition","composition","eyeline","focus","stability"):
                assert k in c, "%s cut 缺字段 %s" % (seg["id"], k)
            b0, b1 = c["beats"]
            assert b0 <= b1 and b0 == prev_beats_hi + 1, \
                "%s beats 不连续: %s (上一镜到尾 %s, scene %s)" % (seg["id"], c["beats"], prev_beats_hi, scene)
            prev_beats_hi = b1
        assert cut_total <= params["maxSegmentSeconds"] + 1e-9, \
            "%s 段时长 %s > 15" % (seg["id"], cut_total)
        seg_seconds += cut_total
        total_segments += 1
        total_cuts += len(seg["cuts"])

        if seg.get("music") is not None:
            pass

    total_seconds += seg_seconds
    episodes.append({"ep": ep, "segments": segs})

# 组装最终对象（不含 seedScenes）
out = {
    "source": "三国演义",
    "promptLang": "en",
    "params": params,
    "episodes": episodes,
}

with io.open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("已写入:", OUT)
print("覆盖集数:", len(episodes))
print("路段数:", total_segments)
print("分镜数:", total_cuts)
print("总时长(sec): %.1f" % total_seconds)
print("目标: 每集 180s, 5 集总目标约 %.1f s (±15%%)" % (180*len(episodes)))
for ep in episodes:
    ep_sec = sum(c["seconds"] for s in ep["segments"] for c in s["cuts"])
    lo, hi = 180*0.85, 180*1.15
    flag = "OK" if lo <= ep_sec <= hi else "!!"
    print("  EP%d: %.1fs  segments=%d (范围 %.0f-%.0f) %s" % (ep["ep"], ep_sec, len(ep["segments"]), lo, hi, flag))