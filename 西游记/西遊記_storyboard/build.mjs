// 生成器：从分镜规格推导 h3Prompt（对齐指令、切点时刻、台词 <d> 块、运镜词）。
// 用法：node build.mjs  输出 segments_ep2.json / segments_ep3.json（无 BOM）。
import { readFileSync, writeFileSync } from 'node:fs';

const SCRIPT_PATH = '../西遊記_scriptwork/script.json';
const script = JSON.parse(readFileSync(new URL(SCRIPT_PATH, import.meta.url), 'utf8'));

const p = script.params || {};
const cps = p.charsPerSecond || 4.5;
const ase = p.actionSeconds || 2.5;
const r1 = (n) => Math.round(n * 10) / 10;
const chars = (l) => l.replace(/\s+/g, '').length;
const beatSec = (b) => (typeof b?.line === 'string' ? r1(chars(b.line) / cps) : ase);

// H3 token（en）
const I2VA =
  'For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.';
const ALIGN_HEAD = 'How the reference pictures align with the target video — ';
const ALIGN_ITEM = (k, t) =>
  `Picture ${k} (from Shot ${k}) aligns with the ${t.toFixed(2)}-second mark of the target video`;
const FIELDS = ['integrated_multimodal_description:', 'overall_soundscape:', 'non_diegetic_music:'];
const cutStarts = (cuts) => {
  const s = [];
  let t = 0;
  for (const c of cuts ?? []) { s.push(r1(t)); t += c?.seconds ?? 0; }
  return s;
};
const h3CutTime = (t) => {
  const m = Math.floor(t / 60);
  const s = Math.floor(t % 60);
  const ms = Math.round((t - Math.floor(t)) * 1000);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}.${String(ms).padStart(3, '0')}`;
};
const alignmentLine = (cuts) => {
  if (!cuts || cuts.length <= 1) return I2VA;
  const starts = cutStarts(cuts);
  const parts = cuts.map((c, i) => ALIGN_ITEM(i + 1, starts[i]));
  return `${ALIGN_HEAD}${parts.join('; ')}.`;
};

function epFlow(epNum) {
  return script.episodes.find((e) => e.ep === epNum)?.scenes ?? [];
}

function buildSegment(spec, epNum) {
  const scene = epFlow(epNum)[spec.sceneIndex - 1];
  const cuts = (spec.cuts ?? []).map((c, i) => {
    const [from, to] = c.beats;
    let dlg = '';
    for (let n = from; n <= to; n++) {
      const b = scene?.flow?.[n - 1];
      if (b && typeof b?.line === 'string') dlg += ` <d>[Chinese] ${b.line}</d>`;
    }
    return { ...c, dlg };
  });
  const starts = cutStarts(cuts);
  const body = cuts
    .map((c, i) => {
      const k = i + 1;
      const prefix = k === 1 ? '[Shot 1] Following <Picture 1>, ' : `[Shot ${k}] At ${h3CutTime(starts[i])}, `;
      return `${prefix}${c.body.trim()}${c.dlg}`;
    })
    .join('\n');
  const h3Prompt = `${alignmentLine(cuts)}\n\n${FIELDS[0]}\n${body}\n\n${FIELDS[1]} ${spec.soundscapeEn}\n\n${FIELDS[2]} ${spec.musicEn || 'N/A'}`;
  return {
    id: spec.id,
    sceneIndex: spec.sceneIndex,
    blocking: spec.blocking,
    soundscape: spec.soundscape,
    ...(spec.music ? { music: spec.music } : {}),
    cuts: cuts.map(({ dlg, ...c }) => ({ ...c })),
    h3Prompt,
  };
}

export function buildEpisode(epNum, specs) {
  return specs.map((s) => buildSegment(s, epNum));
}

// CLI：把 specs_ep2 / specs_ep3 从文件读出并写出
const readSpecs = (f) => JSON.parse(readFileSync(new URL(f, import.meta.url), 'utf8'));

const specs2 = readSpecs('specs_ep2.json');
const out2 = buildEpisode(2, specs2);
writeFileSync(new URL('segments_ep2.json', import.meta.url), JSON.stringify(out2, null, 2));

const specs3 = readSpecs('specs_ep3.json');
const out3 = buildEpisode(3, specs3);
writeFileSync(new URL('segments_ep3.json', import.meta.url), JSON.stringify(out3, null, 2));

console.log(`ep2: ${out2.length} segs, ${out2.reduce((n, s) => n + s.cuts.reduce((m, c) => m + c.seconds, 0), 0).toFixed(1)}s`);
console.log(`ep3: ${out3.length} segs, ${out3.reduce((n, s) => n + s.cuts.reduce((m, c) => m + c.seconds, 0), 0).toFixed(1)}s`);