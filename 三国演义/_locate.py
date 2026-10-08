p = r'd:\study\GitHub\shuohao-skills\三国演义\storyboard-batch-8.json'
t = open(p, encoding='utf-8-sig').read()
lines = t.split('\n')
# find E38-09 segment start and E38-09 h3Prompt, then E38-10 segment start
import re
for i,l in enumerate(lines):
    if '"id": "E38-09"' in l:
        print('E38-09 seg at line', i+1)
    if '"id": "E38-10"' in l:
        print('E38-10 seg at line', i+1)
    if 'h3Prompt' in l:
        print('h3Prompt at line', i+1, 'len', len(l))
# print E38-09 h3Prompt full lines
print('===== lines around E38-09 h3 (search) =====')
start = None
for i,l in enumerate(lines):
    if 'Faint embers' in l or 'faint' in l.lower() and 'h3' in l.lower():
        pass
# just print lines 1695 to 1710 already inspected