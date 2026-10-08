import json, re
p = r'd:\study\GitHub\shuohao-skills\三国演义\storyboard-batch-8.json'
t = open(p, encoding='utf-8-sig').read()
# The JSON is not yet complete (ends mid-ep38). Zero out the tail to parse what's valid.
# Remove everything from the last complete segment boundary. We know E38-15 h3 ends at the tail.
# Strategy: find positions of each '"id": "E38-1x"' and json-parse by brute: cut file to last known-good.
# Simpler: extract raw and try parse, else progressively truncate.
# Just report on beat claims + seconds per segment via regex-free approach using a repair.
# We'll build: momentarily append closure to make it parseable if structure is right.
# Find the last complete segment JSON object boundaries using brace matching from start.
# Use a streaming approach: track through find of '"id": "' segments.
ids = re.findall(r'"id": "E(\d\d-\d\d)"', t)
print('all seg ids:', ids)
# For E38 print beats + seconds + camera per cut (extract from text)
# Parse E38 region only using jsonc trick: take substring from '"ep": 38' to end, complete it
start = t.index('"ep": 38,')
tail = t[start:]
# append closure guesses
for suffix in ['"segments":[]}],{"ep":39,"segments":[]}],{"ep":40,"segments":[]}],{"ep":41}]}}', ']}\n', ',\n}\n', ']\n']:
    try:
        d=json.loads('{"episodes":['+tail+suffix)
        eps=[e for e in d['episodes'] if e.get('segments')]
        print('OK with suffix', suffix[:20], 'parsed eps', [e['ep'] for e in eps])
        break
    except Exception as e:
        # print('try', suffix[:15], repr(str(e))[:40])
        pass