import json
p = r'd:\study\GitHub\shuohao-skills\三国演义\storyboard-batch-8.json'
t = open(p, encoding='utf-8-sig').read()
# do columnar analysis around the reported fail position 97796 in CURRENT (already-repaired) file
pos=97796
print(repr(t[pos-160:pos+160]))
print('---lines 1705-1712 raw---')
lines = t.split('\n')
for ln in range(1703,1714):
    if ln < len(lines):
        print(ln, repr(lines[ln][:120]))