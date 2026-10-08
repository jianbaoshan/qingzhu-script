import re
p = r'd:\study\GitHub\shuohao-skills\三国演义\storyboard-batch-8.json'
t = open(p, encoding='utf-8-sig').read()
# find literal control chars that are not part of pretty-printing (inside strings)
# json.loads reported invalid control char at pos 97760. Locate raw newline/tab inside a quoted string.
# Simple heuristic: find all \n and \t occurrences and see if there is a value - print area around reported error
pos = 97760
for p0 in range(max(0,pos-200), min(len(t),pos+200)):
    c = t[p0]
    if ord(c) < 32 and c not in '\n\t':
        print('ctrl char', repr(c), 'at', p0)
for p0 in [97760]:
    seg = t[p0-120:p0+80]
    print('CTX seg at pos:', repr(seg))
# find raw newline inside string contexts by scanning
# Track in-string state, find \n while in_string=True
in_str = False
esc = False
for i,ch in enumerate(t):
    if esc:
        esc=False; continue
    if ch=='\\':
        esc=True; continue
    if in_str:
        if ch=='"':
            in_str=False
        elif ch=='\n' or ch=='\t' or (ord(ch)<32):
            print('RAW CTRL in string at',i, repr(ch), 'near:', repr(t[i-40:i]))
            # only show a few
    else:
        if ch=='"':
            in_str=True