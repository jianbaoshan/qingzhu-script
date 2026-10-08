import json
sp = r'd:\study\GitHub\shuohao-skills\三国演义\script.json'
s = json.load(open(sp, encoding='utf-8-sig'))
print('top keys', list(s.keys()))
ep = s['episodes'][0]
print('ep keys', list(ep.keys()))
print(json.dumps(ep, ensure_ascii=False, indent=1)[:3000])