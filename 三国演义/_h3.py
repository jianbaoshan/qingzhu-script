p = r'd:\study\GitHub\shuohao-skills\三国演义\storyboard-batch-8.json'
t = open(p, encoding='utf-8-sig').read()
lines = t.split('\n')
# E38-09 h3 line index: find
for i,l in enumerate(lines):
    if l.startswith('          "h3Prompt"'):
        if '"id": "E38-06"' in '\n'.join(lines[max(0,i-3):i]) or i > 1600:
            pass
# We know h3 at line index 1704 (1-based 1705) is E38-09's.
h = lines[1704]
print('len h3 line', len(h))
print('HEAD:', repr(h[:80]))
print('TAIL:', repr(h[-120:]))
# count quotes
print('h3 quotes count', h.count('"'))
# show all positions of the string-opener and where it might close
# The h3 content itself contains escaped \n. Print the last 300 chars
print('LAST300:', repr(h[-300:]))