import * as d11 from './_d11.mjs';
import * as d12 from './_d12.mjs';
import * as d13 from './_d13.mjs';
import * as d14 from './_d14.mjs';
import * as d15 from './_d15.mjs';
import fs from 'node:fs';
const raw = fs.readFileSync('d:/study/GitHub/shuohao-skills/三国演义/storyboard-batch-3.json','utf8').replace(/^\uFEFF/,'');
const board = JSON.parse(raw);
const maps = {11:Object.values(d11)[0],12:Object.values(d12)[0],13:Object.values(d13)[0],14:Object.values(d14)[0],15:Object.values(d15)[0]};
const r1=n=>Math.round(n*10)/10;
let allOk=true;
for (const ep of board.episodes){
  const segs = maps[ep.ep];
  // beat tiling per scene
  const cover = {};
  for (const s of segs){
    if(!s.sceneIndex||!Array.isArray(s.cuts)){console.log(`MISSING seg fields ep${ep.ep}`);allOk=false;continue;}
    const tot = s.cuts.reduce((a,c)=>a+c.seconds,0);
    if(tot>15+1e-6||tot<=0){console.log(`SEG len out of range ep${ep.ep} si${s.sceneIndex}: ${tot}`);allOk=false;}
    if(tot>0 && tot<9){console.log(`NOTE seg short ep${ep.ep} si${s.sceneIndex}: ${tot}`);}
    for(const c of s.cuts){
      const b=c.beats; const key=s.sceneIndex+':'+b[0]+'-'+b[1];
      if(b[0]>b[1]){console.log(`BAD beats ep${ep.ep} ${key}`);allOk=false;}
      for(let i=b[0];i<=b[1];i++){ if(cover[s.sceneIndex]&&cover[s.sceneIndex].includes(i)){console.log(`DUP beat ep${ep.ep} si${s.sceneIndex} beat${i}`);allOk=false;} (cover[s.sceneIndex]=cover[s.sceneIndex]||[]).push(i);}
      if(c.seconds<2||c.seconds>8){console.log(`CUT sec out ep${ep.ep} ${key}: ${c.seconds}`);allOk=false;}
    }
  }
  // check contiguity per scene
  let epTot=0; let scTot={};
  for(const s of segs){const t=s.cuts.reduce((a,c)=>a+c.seconds,0);epTot+=t;scTot[s.sceneIndex]=(scTot[s.sceneIndex]||0)+t;}
  for(const si in cover){const arr=[...cover[si]].sort((a,b)=>a-b);for(let i=0;i<arr.length;i++){if(arr[i]!==i+1){console.log(`NON-CONT/ep-gap ep${ep.ep} si${si}: ${arr.join(',')}`);allOk=false;break;}}}
  console.log(`ep${ep.ep}: segs=${segs.length} totalSecs=${epTot} scenes=${JSON.stringify(scTot)}`);
}
console.log(allOk?'CHECK ALL OK':'CHECK FAILED');