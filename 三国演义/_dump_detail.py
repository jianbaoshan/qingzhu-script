# -*- coding: utf-8 -*-
import json
from collections import defaultdict
b = json.load(open(r'D:\study\GitHub\shuohao-skills\三国演义\_board_after39.json', encoding='utf-8'))
d = defaultdict(list)
for e in b['episodes']:
    d[e['ep']].append(e)
eps = [max(v, key=lambda x: len(x.get('segments', []))) for v in d.values()]
eps.sort(key=lambda x: x['ep'])
with open(r'd:\study\GitHub\shuohao-skills\三国演义\_seg_detail.txt', 'w', encoding='utf-8') as f:
    for e in eps:
        for seg in e['segments']:
            f.write("## {} S{}\n".format(seg['id'], seg['sceneIndex']))
            for i, c in enumerate(seg['cuts']):
                f.write("  cut{} beats={} sec={} size={} cam={} chars={} props={}\n".format(
                    i + 1, c['beats'], c['seconds'], c['size'], c['camera'], c['characters'], c.get('props', [])))
                f.write("      comp={} cpos={} eye={} foc={} stab={} lens={}\n".format(
                    c['composition'], c['cameraPosition'], c['eyeline'], c['focus'], c['stability'], c['lens']))
                f.write("      FRAME: {}\n".format(c['frame']))
                f.write("      SHOT: {}\n".format(c['shot']))
            f.write("\n")
print('done')