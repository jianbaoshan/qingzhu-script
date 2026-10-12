// 从分镜结构重建每段的 h3Prompt：
//   首行对齐指令（由 cuts 秒数推导）+ integrated_multimodal_description（逐镜：[Shot k] At 时刻, 英文正文 <d>台词</d>）
//   + overall_soundscape + non_diegetic_music
// 英文正文核心从现有 h3Prompt 里抽出来复用（剥掉前缀、<d> 块），保证不丢已写好的英文。
// 用法：node regen_h3.mjs
import { readFileSync, writeFileSync } from 'node:fs';

const SB = 'storyboard.json';
const SCRIPT = '../西遊記_scriptwork/script.json';
const load = (p) => JSON.parse(readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const sb = load(SB);
const script = load(SCRIPT);

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

const flow = (epNum) => script.episodes.find((e) => e.ep === epNum)?.scenes ?? [];

const cjkRe = /[\u3400-\u9fff\u3000-\u303f\uff00-\uffef]/;

let segs = 0, cjkLeak = [];
for (const ep of sb.episodes) {
  const scenes = flow(ep.ep);
  for (const seg of ep.segments) {
    segs += 1;
    const cuts = seg.cuts;
    const scene = scenes[seg.sceneIndex - 1];
    const old = String(seg.h3Prompt ?? '');
    const m = old.match(/integrated_multimodal_description:[\s\S]*?(?=\n\n\s*overall_soundscape:)/);
    const body = m ? m[0] : '';
    const cores = [];
    for (let k = 1; k <= cuts.length; k++) {
      const a = body.indexOf(`[Shot ${k}]`);
      const b = k < cuts.length ? body.indexOf(`[Shot ${k + 1}]`) : -1;
      let sl = a >= 0 ? body.slice(a, b < 0 ? undefined : b) : '';
      sl = sl.replace(/<d>[\s\S]*?<\/d>/g, ' ');
      sl = sl.replace(/^\[Shot \d+\]\s*/, '');
      sl = sl.replace(/^Following <Picture \d+>,\s*/i, '');
      sl = sl.replace(/^At \d{2}:\d{2}\.\d{3},\s*/i, '');
      sl = sl.replace(/^the camera cuts to <Picture \d+>:\s*/i, '');
      cores.push(sl.replace(/\s+/g, ' ').trim());
    }
    const starts = cutStarts(cuts);
    const lines = cuts.map((c, i) => {
      const k = i + 1;
      const term = CAM[c.camera] ?? '';
      let core = cores[i] || '';
      if (term && !core.toLowerCase().includes(term.toLowerCase())) core = `${term}, ${core}`.replace(/,\s*$/, '');
      let d = '';
      for (let n = c.beats[0]; n <= c.beats[1]; n++) {
        const bt = scene?.flow?.[n - 1];
        if (bt && typeof bt.line === 'string') d += ` <d>[Chinese] ${bt.line}</d>`;
      }
      const head = k === 1 ? `[Shot 1] Following <Picture 1>, ` : `[Shot ${k}] At ${h3CutTime(starts[i])}, `;
      return `${head}${core}${d}`.replace(/\s+$/, '');
    });
    // 音景与配乐沿用
    const os = old.match(/overall_soundscape:\s*([\s\S]*?)(?=\n\n\s*non_diegetic_music:)/);
    const nd = old.match(/non_diegetic_music:\s*([\s\S]*?)\s*$/);
    const soundscape = os ? os[1].trim() : 'N/A';
    const music = nd ? nd[1].trim() : 'N/A';
    seg.h3Prompt = `${alignLine(cuts)}\n\nintegrated_multimodal_description:\n${lines.join('\n')}\n\noverall_soundscape: ${soundscape}\n\nnon_diegetic_music: ${music}`;
    // 自查：英文正文里混进中文
    const rest = seg.h3Prompt.replace(/<d>[\s\S]*?<\/d>/g, ' ').replace(/"[^"\n]*"/g, ' ');
    if (cjkRe.test(rest)) cjkLeak.push(seg.id);
  }
}

writeFileSync(SB, JSON.stringify(sb, null, 2) + '\n', 'utf8');
console.log(`重建 ${segs} 段的 h3Prompt`);
console.log(cjkLeak.length ? `⚠ 英文正文仍有中文的段（${cjkLeak.length}）：${cjkLeak.slice(0, 20).join(' ')}` : '✓ 全段英文正文不含中文');
