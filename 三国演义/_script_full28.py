import json
sp = r'd:\study\GitHub\shuohao-skills\三国演义\script.json'
s = json.load(open(sp, encoding='utf-8-sig'))
for ep in s['episodes']:
    if ep['ep'] in (38,39,40):
        print('########## EP', ep['ep'], 'targetSeconds', ep['targetSeconds'])
        print('hook:', ep['hook'])
        print('cliff:', ep['cliff'])
        for sc in ep['scenes']:
            print('----- sceneId', sc['sceneId'], 'lighting', sc.get('lighting'), 'characters', sc.get('characters'))
            for it in sc['flow']:
                if 'action' in it:
                    print('   A: ', it['action'])
                else:
                    print('   %s: %s  [%s]' % (it['speaker'], it['line'], it.get('delivery','')))