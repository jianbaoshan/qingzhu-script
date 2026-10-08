import json
p = r'd:\study\GitHub\shuohao-skills\三国演义\storyboard-batch-8.json'
t = open(p, encoding='utf-8-sig').read()
try:
    d = json.loads(t)
    print('PARSED OK. eps', len(d.get('episodes', [])))
    for ep in d['episodes']:
        print(' ep', ep['ep'], 'segs', len(ep['segments']))
except Exception as e:
    pos = getattr(e, 'pos', None)
    print('FAIL:', e)
    print('pos', pos)
    if pos is not None:
        print('CTX:', repr(t[pos-80:pos+80]))
        # line/col
        before = t[:pos]
        line = before.count('\n')+1
        col = pos - before.rfind('\n')
        print('line',line,'col',col)