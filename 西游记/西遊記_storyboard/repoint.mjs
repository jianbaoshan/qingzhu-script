// 把既有分镜的节拍认领从「旧剧本 flow 下标」重贴到「新剧本 flow 下标」。
// 原理：改写只增写/拆分动作拍，台词 646 句一字未动且顺序不变 —— 用台词当锚点，
// 把每场 flow 切成若干「台词间隙」，旧间隙里 k_old 个动作拍按比例摊到新间隙的 k_new 个动作拍上。
// 映射是新区间的一个划分，因此「恰好一次、按顺序、连续」自动成立。
//
// 用法：node repoint.mjs <旧script.json路径>
import { readFileSync, writeFileSync } from 'node:fs';

const SB = 'storyboard.json';
const NEW = '../西遊記_scriptwork/script.json';
const OLDP = process.argv[2];

const load = (p) => JSON.parse(readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const sb = load(SB);
const nw = load(NEW);
const od = load(OLDP);

const CPS = nw.params?.charsPerSecond ?? 4.5;
const ASE = nw.params?.actionSeconds ?? 2.5;
const r1 = (n) => Math.round(n * 10) / 10;
const lineChars = (s) => String(s).replace(/\s+/g, '').length;

// 新剧本每拍秒数
const nByIdx = new Map(); // `${ep}|${sceneIndex}` -> [secs]
for (const e of nw.episodes) {
  e.scenes.forEach((sc, i) => {
    nByIdx.set(`${e.ep}|${i + 1}`, (sc.flow ?? []).map((b) => (typeof b?.line === 'string' ? r1(lineChars(b.line) / CPS) : ASE)));
  });
}
const oByIdx = new Map();
for (const e of od.episodes) {
  e.scenes.forEach((sc, i) => oByIdx.set(`${e.ep}|${i + 1}`, sc.flow ?? []));
}
const nFlow = new Map();
for (const e of nw.episodes) {
  e.scenes.forEach((sc, i) => nFlow.set(`${e.ep}|${i + 1}`, sc.flow ?? []));
}

function buildMap(of, nf) {
  const oL = [], nL = [];
  of.forEach((b, i) => { if (typeof b?.line === 'string') oL.push(i); });
  nf.forEach((b, i) => { if (typeof b?.line === 'string') nL.push(i); });
  const ol = oL.map((i) => of[i].line);
  const nl = nL.map((i) => nf[i].line);
  if (JSON.stringify(ol) !== JSON.stringify(nl)) {
    throw new Error(`台词序列不一致 old=${ol.length} new=${nl.length}`);
  }
  const first = {}, last = {};
  for (let g = 0; g <= oL.length; g++) {
    const oLo = g ? oL[g - 1] + 1 : 0;
    const oHi = g < oL.length ? oL[g] : of.length;
    const nLo = g ? nL[g - 1] + 1 : 0;
    const nHi = g < nL.length ? nL[g] : nf.length;
    const oActs = [], nActs = [];
    for (let i = oLo; i < oHi; i++) oActs.push(i);
    for (let i = nLo; i < nHi; i++) nActs.push(i);
    const ko = oActs.length, kn = nActs.length;
    if (ko === 0) continue;
    if (kn === 0) {
      const v = Math.max(0, nLo - 1);
      for (const oi of oActs) { first[oi] = v; last[oi] = v; }
      continue;
    }
    oActs.forEach((oi, j) => {
      const a = Math.floor((j * kn) / ko);
      let b = Math.floor(((j + 1) * kn) / ko) - 1;
      if (b < a) b = a;
      first[oi] = nActs[a];
      last[oi] = nActs[b];
    });
  }
  oL.forEach((oi, g) => { first[oi] = nL[g]; last[oi] = nL[g]; });
  return { first, last };
}

let cuts = 0, changed = 0;
const moved = [];
for (const ep of sb.episodes) {
  for (const seg of ep.segments) {
    const key = `${ep.ep}|${seg.sceneIndex}`;
    const of = oByIdx.get(key), nf = nFlow.get(key), secs = nByIdx.get(key);
    if (!of || !nf) throw new Error(`找不到 ${key}`);
    const { first, last } = buildMap(of, nf);
    for (const c of seg.cuts) {
      cuts += 1;
      const [f0, t0] = c.beats;
      const a = first[f0 - 1], b = last[t0 - 1];
      if (a === undefined || b === undefined) throw new Error(`${seg.id} 拍 ${f0}-${t0} 映射失败`);
      const ns = r1(secs.slice(a, b + 1).reduce((x, y) => x + y, 0));
      if (a + 1 !== f0 || b + 1 !== t0 || ns !== c.seconds) {
        moved.push({ id: `${seg.id}#${seg.cuts.indexOf(c) + 1}`, old: [f0, t0], nw: [a + 1, b + 1], o: c.seconds, n: ns });
        changed += 1;
      }
      c.beats = [a + 1, b + 1];
      c.seconds = ns;
    }
  }
}

writeFileSync(SB, JSON.stringify(sb, null, 2) + '\n', 'utf8');
console.log(`重贴完成：${cuts} 切，其中 ${changed} 切的位置或时长发生变化`);
const bad = moved.filter((m) => m.n > 8 || m.n < 2);
console.log(`重贴后越界 [2,8] 秒的切：${bad.length}`);
for (const m of bad) console.log(`   ${m.id} 旧拍${m.old} -> 新拍${m.nw}  ${m.o}s -> ${m.n}s`);
