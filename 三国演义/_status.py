import io, re, json
p = r'd:\study\GitHub\shuohao-skills\三国演义\storyboard-batch-8.json'
t = open(p, encoding='utf-8-sig').read()
print('len', len(t))
print('BOM?', t.startswith('\ufeff'))
# try parse
try:
    d = json.loads(t)
    print('PARSED OK. eps', len(d.get('episodes', [])))
    for ep in d.get('episodes', []):
        print(' ep', ep['ep'], 'segments', len(ep.get('segments', [])))
except Exception as e:
    print('PARSE FAIL:', e)
    pos = getattr(e, 'pos', None)
    print('pos', pos)
    if pos:
        print(repr(t[pos-60:pos+60]))
# count segment ids & blocking presence
ids = re.findall(r'"id": "(E\d\d-\d\d)"', t)
print('seg ids found', len(ids))
print('blocking count', len(re.findall(r'"blocking":', t)))
print('soundscape count', len(re.findall(r'"soundscape":', t)))
print('music count', len(re.findall(r'"music":', t)))
print('seedScenes present', 'seedScenes' in t)
print('last seg', ids[-6:] if ids else None)