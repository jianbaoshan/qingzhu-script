// h3Prompt 归一化：对 storyboard.json 的每个 segment，用 cuts + 剧本 flow 从零重建 h3Prompt，
// 保证 alignmentLine / 切点时刻 / 台词 <d> 块 / camera 词全部逐字对账。保留每镜原有的英文叙述正文。
import { readFileSync, writeFileSync } from 'node:fs';

const SB = '西遊記_storyboard/storyboard.json';
const doc = JSON.parse(readFileSync(SB, 'utf8'));
const script = JSON.parse(readFileSync(new URL('../西遊記_scriptwork/script.json', import.meta.url), 'utf8'));

function flow(epNum) {
  return script.episodes.find((e) => e.ep === epNum)?.scenes ?? [];
}

const r1 = (n) => Math.round(n * 10) / 10;
const cutStarts = (cuts) => { const s = []; let t = 0; for (const c of cuts) { s.push(r1(t)); t += c.seconds; } return s; };
const h3CutTime = (t) => {
  const m = Math.floor(t / 60), s = Math.floor(t % 60), ms = Math.round((t - Math.floor(t)) * 1000);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}.${String(ms).padStart(3, '0')}`;
};
const alignmentLine = (cuts) => {
  if (cuts.length <= 1) return 'For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.';
  const starts = cutStarts(cuts);
  const parts = cuts.map((c, i) => `Picture ${i + 1} (from Shot ${i + 1}) aligns with the ${starts[i].toFixed(2)}-second mark of the target video`);
  return `How the reference pictures align with the target video — ${parts.join('; ')}.`;
};

// camera 词（en）：与 CAMERA_MOVES 保持一致
const CAM = {
  'Static Shot': 'static shot', 'Push In': 'push in', 'Pull Out': 'pull out', 'Zoom In': 'zoom in',
  'Zoom Out': 'zoom out', 'Pan Left': 'pan left', 'Pan Right': 'pan right', 'Truck Left': 'truck left',
  'Truck Right': 'truck right', 'Tilt Up': 'tilt up', 'Tilt Down': 'tilt down', 'Pedestal Up': 'pedestal up',
  'Pedestal Down': 'pedestal down', 'Arc Shot': 'arc shot', 'Tracking Shot': 'tracking shot',
  'Shake Slightly': 'shake slightly', 'Shake Strongly': 'shake strongly', 'POV': 'POV',
  'Roll Clockwise': 'roll clockwise', 'Roll Counterclockwise': 'roll counterclockwise',
};

for (const ep of doc.episodes) {
  const scenes = flow(ep.ep);
  for (const seg of ep.segments) {
    const cuts = seg.cuts;
    const scene = scenes[seg.sceneIndex - 1];
    const starts = cutStarts(cuts);
    // 收集每镜已有的英文正文：解析原 h3Prompt 的 integrated_multimodal_description 段
    let desc = String(seg.h3Prompt ?? '');
    const m = desc.match(/integrated_multimodal_description:\n([\s\S]*?)(?=\n\noverall_soundscape:)/);
    const body = m ? m[1] : '';
    const slices = [];
    for (let k = 1; k <= cuts.length; k++) {
      const a = body.indexOf(`[Shot ${k}]`);
      const b = k < cuts.length ? body.indexOf(`[Shot ${k + 1}]`) : -1;
      let sl = a >= 0 ? body.slice(a, b < 0 ? undefined : b) : '';
      // 去掉 d 块与句首前缀，留纯英文叙述核心
      sl = sl.replace(/<d>[\s\S]*?<\/d>/g, '');
      sl = sl.replace(/^\[Shot \d+\]\s*/, '');
      sl = sl.replace(/^(Following <Picture \d+>,|At \d{2}:\d{2}\.\d{3},\s*the camera cuts to <Picture \d+>:\s*)/, '');
      slices.push(sl.trim());
    }
    // 重建说明正文
    const lines = cuts.map((c, i) => {
      const k = i + 1;
      const term = CAM[c.camera] ?? '';
      let core = slices[i] || '';
      // 运镜词必须落在自己那一行
      if (term && !core.toLowerCase().includes(term)) core = `${term}, ${core}`.trim();
      // 台词 <d>
      let d = '';
      for (let n = c.beats[0]; n <= c.beats[1]; n++) {
        const b = scene?.flow?.[n - 1];
        if (b && typeof b?.line === 'string') d += ` <d>[Chinese] ${b.line}</d>`;
      }
      if (k === 1) {
        return `[Shot 1] Following <Picture 1>, ${core}${d}`;
      }
      return `[Shot ${k}] At ${h3CutTime(starts[i])}, the camera cuts to <Picture ${k}>: ${core}${d}`;
    });
    // 音景与配乐：从原 h3Prompt 取（保证英文、无括号）
    const os = desc.match(/overall_soundscape:\s*([\s\S]*?)(?=\n\nnon_diegetic_music:)/);
    const nd = desc.match(/non_diegetic_music:\s*([\s\S]*?)(?=\n\n|$)/);
    const soundscape = os ? os[1].trim() : 'N/A';
    const music = nd ? nd[1].trim() : 'N/A';
    seg.h3Prompt = `${alignmentLine(cuts)}\n\nintegrated_multimodal_description:\n${lines.join('\n')}\n\noverall_soundscape: ${soundscape}\n\nnon_diegetic_music: ${music}`;
  }
}

writeFileSync(SB, JSON.stringify(doc, null, 2) + '\n', 'utf8');
console.log('normalized h3Prompts ->', SB);
console.log(`ep1 ${doc.episodes[0].segments.length} / ep2 ${doc.episodes[1].segments.length} / ep3 ${doc.episodes[2].segments.length}`);