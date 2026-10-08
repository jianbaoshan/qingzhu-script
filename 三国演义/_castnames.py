import json
def load(p):
    return json.load(open(p, encoding='utf-8-sig'))
cast = load(r'd:\study\GitHub\shuohao-skills\三国演义\cast.json')
print('CAST characters:')
for c in cast.get('characters', []):
    print(' ', c.get('id'), reproduce:=c.get('name'), '| aliases', c.get('aliases'))
print()
try:
    outline = load(r'd:\study\GitHub\shuohao-skills\三国演义\outline.json')
    print('OUTLINE chars:', [c.get('name') for c in outline.get('characters', [])])
except Exception as e:
    print('outline err', e)