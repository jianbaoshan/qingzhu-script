import fs from 'node:fs';
const s = JSON.parse(fs.readFileSync('d:/study/GitHub/shuohao-skills/三国演义/script.json','utf8').replace(/^\uFEFF/,''));
for (const ep of s.episodes) {
  if (![11,12,13,14,15].includes(ep.ep)) continue;
  console.log(`\n===== ep${ep.ep} targetSeconds=${ep.targetSeconds} =====`);
  ep.scenes.forEach((sc, idx) => {
    console.log(` scene${idx+1} sceneId=${sc.sceneId} chars=${JSON.stringify(sc.characters)} props=${JSON.stringify(sc.props)}`);
    (sc.flow || []).forEach((b, i) => {
      const kind = b.speaker ? 'line' : 'action';
      const secs = b.seconds != null ? b.seconds : (b.durationSeconds != null ? b.durationSeconds : '?');
      console.log(`   b${i+1} ${kind} ${secs}s${b.speaker?(' ['+b.speaker+']'):''} ${b.line || b.action || b.text}`);
    });
  });
}