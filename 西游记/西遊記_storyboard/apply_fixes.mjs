// 把分镜重贴后的三件事一次做完：
//   0) 从现有 h3Prompt 里把每镜的英文正文抽到 cut.en（此后英文正文有独立字段，重建不再靠解析）
//   1) 应用切级修订（拆/并，含新写的 frame/shot/en）
//   2) 按「每段 ≤15 秒」用 DP 重排段边界（尽量少动原边界），重编段号
//   3) 用 cut.en 重建每段 h3Prompt
// 用法：node apply_fixes.mjs <patchCuts.json>
import { readFileSync, writeFileSync } from 'node:fs';

const SB = 'storyboard.json';
const SCRIPT = '../西遊記_scriptwork/script.json';
const PATCH = process.argv[2];
const MAXSEG = 15;
const EPS = 1e-9;

const load = (p) => JSON.parse(readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const sb = load(SB);
const script = load(SCRIPT);
const patch = load(PATCH);

const r1 = (n) => Math.round(n * 10) / 10;
const cutStarts = (cuts) => { const s = []; let t = 0; for (const c of cuts) { s.push(r1(t)); t += c.seconds ?? 0; } return s; };
const h3CutTime = (t) => {
  const m = Math.floor(t / 60), s = Math.floor(t % 60), ms = Math.round((t - Math.floor(t)) * 1000);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}.${String(ms).padStart(3, '0')}`;
};
const I2VA = 'For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.';
const alignLine = (cuts) => {
  if (cuts.length <= 1) return I2VA;
  const st = cutStarts(cuts);
  const parts = cuts.map((c, i) => `Picture ${i + 1} (from Shot ${i + 1}) aligns with the ${st[i].toFixed(2)}-second mark of the target video`);
  return `How the reference pictures align with the target video — ${parts.join('; ')}.`;
};
const CAM = {
  'Static Shot': 'static shot', 'Push In': 'push in', 'Pull Out': 'pull out', 'Zoom In': 'zoom in',
  'Zoom Out': 'zoom out', 'Pan Left': 'pan left', 'Pan Right': 'pan right', 'Truck Left': 'truck left',
  'Truck Right': 'truck right', 'Tilt Up': 'tilt up', 'Tilt Down': 'tilt down', 'Pedestal Up': 'pedestal up',
  'Pedestal Down': 'pedestal down', 'Arc Shot': 'arc shot', 'Tracking Shot': 'tracking shot',
  'Shake Slightly': 'shake slightly', 'Shake Strongly': 'shake strongly', 'POV': 'POV',
  'Roll Clockwise': 'roll clockwise', 'Roll Counterclockwise': 'roll counterclockwise',
};
const cjkRe = /[\u3400-\u9fff\u3000-\u303f\uff00-\uffef]/;
const flow = (epNum) => script.episodes.find((e) => e.ep === epNum)?.scenes ?? [];
const pad2 = (n) => String(n).padStart(2, '0');

// ---------- 0. 回填 cut.en ----------
let backfilled = 0;
for (const ep of sb.episodes) {
  for (const seg of ep.segments) {
    const h3 = String(seg.h3Prompt ?? '');
    const a0 = h3.indexOf('integrated_multimodal_description:');
    const b0 = h3.indexOf('overall_soundscape:');
    const body = a0 >= 0 ? h3.slice(a0, b0 < 0 ? undefined : b0) : '';
    seg.cuts.forEach((c, i) => {
      if (c.en) return;
      const k = i + 1;
      const a = body.indexOf(`[Shot ${k}]`);
      const b = k < seg.cuts.length ? body.indexOf(`[Shot ${k + 1}]`) : -1;
      let sl = a >= 0 ? body.slice(a, b < 0 ? undefined : b) : '';
      sl = sl.replace(/<d>[\s\S]*?<\/d>/g, ' ');
      sl = sl.replace(/^\[Shot \d+\]\s*/, '');
      sl = sl.replace(/^Following <Picture \d+>,\s*/i, '');
      sl = sl.replace(/^At \d{2}:\d{2}\.\d{3},\s*/i, '');
      sl = sl.replace(/^the camera cuts to <Picture \d+>:\s*/i, '');
      c.en = sl.replace(/\s+/g, ' ').trim();
      backfilled += 1;
    });
    // 英文音景/配乐：h3Prompt 里的是英文，seg.soundscape 是中文——两者都要留，h3 用英文那份
    const os = h3.match(/overall_soundscape:\s*([\s\S]*?)(?=\n\n\s*non_diegetic_music:)/);
    const nd = h3.match(/non_diegetic_music:\s*([\s\S]*?)\s*$/);
    if (!seg.soundscapeEn) seg.soundscapeEn = os ? os[1].trim() : 'N/A';
    if (!seg.musicEn) seg.musicEn = nd ? nd[1].trim() : 'N/A';
  }
}
console.log(`回填 en：${backfilled} 切`);

// ---------- 1. 切级修订 ----------
const changedSegs = [];
for (const ep of sb.episodes) {
  for (const seg of ep.segments) {
    const spec = patch[seg.id];
    if (!spec) continue;
    const old = seg.cuts;
    const before = old.map((c) => `${c.beats[0]}-${c.beats[1]}`).join(',');
    seg.cuts = spec.map((s) => {
      const base = JSON.parse(JSON.stringify(old[s.reuse - 1]));
      for (const [k, v] of Object.entries(s)) if (k !== 'reuse') base[k] = v;
      return base;
    });
    const after = seg.cuts.map((c) => `${c.beats[0]}-${c.beats[1]}`).join(',');
    if (before !== after) changedSegs.push(`${seg.id} [${before}] -> [${after}]`);
  }
}
console.log(`切级修订：${changedSegs.length} 段`);
changedSegs.forEach((s) => console.log(`   ${s}`));

// ---------- 2. 段边界重排 ----------
const beforeCount = sb.episodes.reduce((n, e) => n + e.segments.length, 0);
const notes = [];
for (const ep of sb.episodes) {
  const groups = [];
  let cur = null;
  for (const seg of ep.segments) {
    if (!cur || cur.si !== seg.sceneIndex) { cur = { si: seg.sceneIndex, segs: [] }; groups.push(cur); }
    cur.segs.push(seg);
  }
  const newSegs = [];
  for (const g of groups) {
    const cuts = [];
    const oldBound = [];
    for (const seg of g.segs) { oldBound.push(cuts.length); cuts.push(...seg.cuts); }
    const n = cuts.length;
    const pref = [0];
    for (const c of cuts) pref.push(pref[pref.length - 1] + c.seconds);
    const sum = (i, j) => pref[j] - pref[i];
    const kOrig = g.segs.length;
    const near = (i) => oldBound.slice(1).reduce((m, b) => Math.min(m, Math.abs(i - b)), Infinity);

    let best = null;
    for (let k = kOrig; k <= kOrig + 4 && !best; k++) {
      if (k > n) break;
      const INF = Infinity;
      const dp = Array.from({ length: k + 1 }, () => new Array(n + 1).fill(INF));
      const par = Array.from({ length: k + 1 }, () => new Array(n + 1).fill(-1));
      dp[0][0] = 0;
      for (let gg = 1; gg <= k; gg++) {
        for (let i = gg; i <= n - (k - gg); i++) {
          for (let j = gg - 1; j < i; j++) {
            if (dp[gg - 1][j] === INF) continue;
            const s = sum(j, i);
            if (s > MAXSEG + EPS || s <= 0) continue;
            const c = dp[gg - 1][j] + (i === n ? 0 : near(i));
            if (c < dp[gg][i]) { dp[gg][i] = c; par[gg][i] = j; }
          }
        }
      }
      if (dp[k][n] !== INF) {
        const bnds = [];
        let i = n;
        for (let gg = k; gg >= 1; gg--) { const j = par[gg][i]; bnds.unshift([j, i]); i = j; }
        best = { k, bnds };
      }
    }
    if (!best) throw new Error(`E${ep.ep} 场${g.si} 无法在 ≤15 秒内分段`);
    if (best.k !== kOrig) notes.push(`E${pad2(ep.ep)} 场${g.si}：${kOrig} 段 -> ${best.k} 段`);
    best.bnds.forEach(([a, b], idx) => {
      const src = g.segs[Math.min(idx, g.segs.length - 1)];
      newSegs.push({
        sceneIndex: g.si, blocking: src.blocking, soundscape: src.soundscape,
        soundscapeEn: src.soundscapeEn, musicEn: src.musicEn,
        ...(src.music ? { music: src.music } : {}), cuts: cuts.slice(a, b),
      });
    });
  }
  newSegs.forEach((s, i) => { s.id = `E${pad2(ep.ep)}-${pad2(i + 1)}`; });
  ep.segments = newSegs.map((s) => {
    const o = { id: s.id, sceneIndex: s.sceneIndex, blocking: s.blocking, soundscape: s.soundscape };
    if (s.soundscapeEn) o.soundscapeEn = s.soundscapeEn;
    if (s.musicEn) o.musicEn = s.musicEn;
    if (s.music) o.music = s.music;
    o.cuts = s.cuts;
    return o;
  });
}

// ---------- 3. 重建 h3Prompt ----------
const cjkLeak = [];
for (const ep of sb.episodes) {
  const scenes = flow(ep.ep);
  for (const seg of ep.segments) {
    const cuts = seg.cuts;
    const scene = scenes[seg.sceneIndex - 1];
    const starts = cutStarts(cuts);
    const lines = cuts.map((c, i) => {
      const k = i + 1;
      const term = CAM[c.camera] ?? '';
      let core = String(c.en ?? '').trim();
      if (!core) throw new Error(`${seg.id}#${k} 缺 en`);
      if (term && !core.toLowerCase().includes(term.toLowerCase())) core = `${term}, ${core}`;
      let d = '';
      for (let n = c.beats[0]; n <= c.beats[1]; n++) {
        const bt = scene?.flow?.[n - 1];
        if (bt && typeof bt.line === 'string') d += ` <d>[Chinese] ${bt.line}</d>`;
      }
      const head = k === 1 ? `[Shot 1] Following <Picture 1>, ` : `[Shot ${k}] At ${h3CutTime(starts[i])}, `;
      return `${head}${core}${d}`;
    });
    // 字段顺序：先 cuts 再 h3Prompt
    const keep = seg.music;
    const rebuilt = { id: seg.id, sceneIndex: seg.sceneIndex, blocking: seg.blocking, soundscape: seg.soundscape };
    if (seg.soundscapeEn) rebuilt.soundscapeEn = seg.soundscapeEn;
    if (seg.musicEn) rebuilt.musicEn = seg.musicEn;
    if (keep) rebuilt.music = keep;
    rebuilt.cuts = cuts;
    rebuilt.h3Prompt = `${alignLine(cuts)}\n\nintegrated_multimodal_description:\n${lines.join('\n')}\n\noverall_soundscape: ${seg.soundscapeEn ?? 'N/A'}\n\nnon_diegetic_music: ${seg.musicEn ?? 'N/A'}`;
    Object.keys(seg).forEach((k) => delete seg[k]);
    Object.assign(seg, rebuilt);
    const rest = seg.h3Prompt.replace(/<d>[\s\S]*?<\/d>/g, ' ');
    if (cjkRe.test(rest)) cjkLeak.push(seg.id);
  }
}

writeFileSync(SB, JSON.stringify(sb, null, 2) + '\n', 'utf8');
const afterCount = sb.episodes.reduce((n, e) => n + e.segments.length, 0);
console.log(`段数：${beforeCount} -> ${afterCount}`);
console.log(notes.length ? `段数变化的集：\n   ${notes.join('\n   ')}` : '段数未变');
console.log(cjkLeak.length ? `⚠ 英文正文含中文：${cjkLeak.join(' ')}` : '✓ 英文正文无中文');
