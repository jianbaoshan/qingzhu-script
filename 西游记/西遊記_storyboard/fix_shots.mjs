// 应用 shot 重写（去掉角色名、去掉复述台词），并修个别秒数；顺手复核全库不再有角色名。
// 用法：node fix_shots.mjs <patchShots.json> <bannedNamesJson>
import { readFileSync, writeFileSync } from 'node:fs';

const SB = 'storyboard.json';
const CAST = '../characters.json';
const PATCHP = process.argv[2];

const load = (p) => JSON.parse(readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const sb = load(SB);
const cast = load(CAST);
const patch = load(PATCHP);

const banned = new Set();
for (const ch of cast.characters ?? []) {
  if (typeof ch?.name === 'string') banned.add(ch.name);
  for (const a of ch?.aliases ?? []) if (typeof a === 'string') banned.add(a);
}

let shotFix = 0, secFix = 0;
const missing = [];
for (const ep of sb.episodes) {
  for (const seg of ep.segments) {
    seg.cuts.forEach((c, i) => {
      const key = `${seg.id}#${i + 1}`;
      const ns = patch.shots[key];
      if (ns) {
        if (c.shot === ns) missing.push(`${key} 未变化`);
        c.shot = ns;
        shotFix += 1;
      }
      const sec = patch.__seconds?.[key];
      if (sec !== undefined) { c.seconds = sec; secFix += 1; }
    });
  }
}

// 复核：全库 shot 不再含角色名
const hits = [];
for (const ep of sb.episodes) {
  for (const seg of ep.segments) {
    seg.cuts.forEach((c, i) => {
      for (const n of banned) if (String(c.shot ?? '').includes(n)) hits.push(`${seg.id}#${i + 1} -> ${n}`);
    });
  }
}

writeFileSync(SB, JSON.stringify(sb, null, 2) + '\n', 'utf8');
console.log(`shot 重写 ${shotFix} 处，秒数修正 ${secFix} 处`);
if (missing.length) console.log(`⚠ 名单里有但没匹配上的键：${missing.join(' ')}`);
console.log(hits.length ? `✗ 仍有角色名：\n   ${hits.join('\n   ')}` : '✓ shot 全库已无角色名');
