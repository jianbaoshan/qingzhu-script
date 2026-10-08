import json
sp = r'd:\study\GitHub\shuohao-skills\三国演义\script.json'
s = json.load(open(sp, encoding='utf-8-sig'))
eps = s['episodes']
for ep in eps:
    if ep['ep'] in (36,37,38,39,40):
        print('=== EP', ep['ep'], 'targetSeconds', ep.get('targetSeconds'), 'title', ep.get('title'))
        for sc in ep.get('scenes', []):
            print('   scene', sc.get('sceneIndex'), sc.get('location'), '|', sc.get('time'))
            for beat in sc.get('beats', []):
                ln = beat.get('line') or beat.get('dialogue') or ''
                who = beat.get('character') or beat.get('speaker') or ''
                print('     b%-3d %-6s %s' % (beat.get('episodeBeat') or beat.get('beatNumber') or beat.get('index'), who, ln[:40]))
        # also print any segments-level hookBeat info
        print('   hookBeat', ep.get('hookBeat'))