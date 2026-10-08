import json
sp = r'd:\study\GitHub\shuohao-skills\三国演义\script.json'
s = json.load(open(sp, encoding='utf-8-sig'))
for ep in s['episodes']:
    if ep['ep'] in (36,37,38):
        print('### EP', ep['ep'])
        for i, sc in enumerate(ep['scenes']):
            print(' scene', i+1, sc['sceneId'], sc.get('lighting'))
            for j, it in enumerate(sc['flow']):
                if 'line' in it:
                    sec = round(len(it['line'].replace(' ',''))/4.5,1)
                    print('   b%02d L C%s %.1fs %s' % (j+1, it['speaker'], sec, it['line']))
                else:
                    print('   b%02d A %.1fs %s' % (j+1, 2.5, it['action']))