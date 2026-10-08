import json
p = r'd:\study\GitHub\shuohao-skills\三国演义\storyboard-batch-8.json'
t = open(p, encoding='utf-8-sig').read()

# Repair: inside JSON strings, replace raw control chars that should be escaped.
# Proper approach: do a real JSON repair by tracking string state and escaping \n, \t, and other ctrl chars.
out = []
in_str = False
esc = False
i = 0
N = len(t)
while i < N:
    ch = t[i]
    if esc:
        out.append(ch); esc=False; i+=1; continue
    if ch == '\\':
        out.append(ch); esc=True; i+=1; continue
    if in_str:
        if ch == '"':
            out.append(ch); in_str=False
        elif ch == '\n':
            out.append('\\n')
        elif ch == '\t':
            out.append('\\t')
        elif ord(ch) < 32:
            out.append('\\u%04x' % ord(ch))
        else:
            out.append(ch)
        i+=1; continue
    else:
        if ch == '"':
            in_str=True
        out.append(ch); i+=1; continue

t2 = ''.join(out)
try:
    d = json.loads(t2)
    print('REPAIRED PARSE OK. eps', len(d.get('episodes', [])))
    for ep in d['episodes']:
        print(' ep', ep['ep'], 'segs', len(ep['segments']))
    open(p, 'w', encoding='utf-8-sig').write(t2)
    print('WROTE back repaired file')
except Exception as e:
    print('STILL FAIL:', e, 'pos', getattr(e,'pos',None))