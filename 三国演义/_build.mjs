// 构建器：把各集数据文件(segments 原始) 转成最终 storyboard，自动生成段号/H3/台词块
import fs from 'node:fs';
const IN = 'd:/study/GitHub/shuohao-skills/三国演义/storyboard-batch-3.json';
const SCRIPT_PATH = 'd:/study/GitHub/shuohao-skills/三国演义/script.json';
const raw = fs.readFileSync(IN, 'utf8').replace(/^\uFEFF/, '');
const board = JSON.parse(raw);
const script = JSON.parse(fs.readFileSync(SCRIPT_PATH, 'utf8').replace(/^\uFEFF/, ''));

const r1 = (n) => Math.round(n * 10) / 10;
function cutStarts(cuts){const s=[];let t=0;for(const c of cuts){s.push(r1(t));t+=c.seconds;}return s;}
function h3CutTime(t){const m=Math.floor(t/60),s=Math.floor(t%60),ms=Math.round((t-Math.floor(t))*1000);return `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}.${String(ms).padStart(3,'0')}`;}
const I2VA='For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.';
const AH='How the reference pictures align with the target video — ';
function alignLine(cuts){if(!cuts||cuts.length<=1)return I2VA;const st=cutStarts(cuts);const parts=cuts.map((c,i)=>`Picture ${i+1} (from Shot ${i+1}) aligns with the ${st[i].toFixed(2)}-second mark of the target video`);return `${AH}${parts.join('; ')}.`;}

// 扩展该场台词：返回 map: beatIndex->text
function sceneLines(ep, sceneIndex){
  const sc = script.episodes.find(e=>e.ep===ep)?.scenes?.[sceneIndex-1];
  if(!sc || !Array.isArray(sc.flow)) return [];
  return sc.flow.map(b => (b.line != null ? {kind:'line', text:b.line} : {kind:'action'}));
}

function buildEp(ep, rawSegs){
  return rawSegs.map((sg, i)=>{
    const lines = sceneLines(ep, sg.sceneIndex);
    // 每 cut 认领的 line 台词，按 cut 内顺序编号 {0},{1}...
    const cuts = sg.cuts.map(c=>{
      const claimedLines = [];
      for(let b=c.beats[0]-1;b<c.beats[1];b++){ if(lines[b].kind==='line') claimedLines.push(lines[b].text); }
      let ti=0;
      const eng = c.eng.replace(/\{t(\d+)\}/g, (m,n)=>`<d>[Chinese] ${claimedLines[+n]}</d>`);
      const {eng:_,...body}=c;
      return {...body, eng};
    });
    // 重算 eng 引用（写入 h3Prompt 用）
    const starts=cutStarts(cuts);
    const bodyLines = cuts.map((c,ci)=>{
      const head=`[Shot ${ci+1}]`+(ci===0?' ':` At ${h3CutTime(starts[ci])}, `);
      const term=String(c.camera).toLowerCase();
      let text=head+c.eng;
      if(!text.toLowerCase().includes(term)) text=head+term+'. '+c.eng;
      return text;
    }).join('\n');
    const h3=`${alignLine(cuts)}\n\nintegrated_multimodal_description:\n${bodyLines}\n\noverall_soundscape: ${sg.h3sound}\n\nnon_diegetic_music: ${sg.h3music}`;
    const segObj={ id:`E${String(ep).padStart(2,'0')}-${String(i+1).padStart(2,'0')}`, sceneIndex:sg.sceneIndex,
      cuts: cuts.map(({eng,...x})=>x), h3Prompt:h3, blocking:sg.blocking, soundscape:sg.soundscape };
    if(sg.music) segObj.music=sg.music;
    return segObj;
  });
}

import * as d11 from './_d11.mjs';
import * as d12 from './_d12.mjs';
import * as d13 from './_d13.mjs';
import * as d14 from './_d14.mjs';
import * as d15 from './_d15.mjs';

for (const e of board.episodes){
  const dat = {11:d11,12:d12,13:d13,14:d14,15:d15}[e.ep];
  e.segments = buildEp(e.ep, dat.default ?? dat.segments);
  delete e.seedScenes;
}
fs.writeFileSync(IN, JSON.stringify(board, null, 2), 'utf8');
console.log('built ok');