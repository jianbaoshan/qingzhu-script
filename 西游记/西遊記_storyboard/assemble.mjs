// 组装最终 storyboard.json：ep1-3(现有 storyboard.json 里已生成的 segments) + ep4/5/6(build.mjs 生成)。
// 输出无 BOM 的 storyboard.nobom.json；随后由外壳写回 storyboard.json + BOM。
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { buildEpisode } from './build.mjs';

const SE = fileURLToPath(new URL('.', import.meta.url));
// 读现有 storyboard.json 中已生成的 1-3 集 segments（保持不动）
const cur = JSON.parse(readFileSync(SE + 'storyboard.json', 'utf8'));
const eps13 = cur.episodes.filter((e) => e.ep <= 3).map((e) => ({ ep: e.ep, segments: e.segments }));

// 用 specs 构建 4-12 集
const specs4 = JSON.parse(readFileSync(SE + 'specs_ep4.json', 'utf8'));
const specs5 = JSON.parse(readFileSync(SE + 'specs_ep5.json', 'utf8'));
const specs6 = JSON.parse(readFileSync(SE + 'specs_ep6.json', 'utf8'));
const specs7 = JSON.parse(readFileSync(SE + 'specs_ep7.json', 'utf8'));
const specs8 = JSON.parse(readFileSync(SE + 'specs_ep8.json', 'utf8'));
const specs9 = JSON.parse(readFileSync(SE + 'specs_ep9.json', 'utf8'));
const specs10 = JSON.parse(readFileSync(SE + 'specs_ep10.json', 'utf8'));
const specs11 = JSON.parse(readFileSync(SE + 'specs_ep11.json', 'utf8'));
const specs12 = JSON.parse(readFileSync(SE + 'specs_ep12.json', 'utf8'));
const ep4 = buildEpisode(4, specs4);
const ep5 = buildEpisode(5, specs5);
const ep6 = buildEpisode(6, specs6);
const ep7 = buildEpisode(7, specs7);
const ep8 = buildEpisode(8, specs8);
const ep9 = buildEpisode(9, specs9);
const ep10 = buildEpisode(10, specs10);
const ep11 = buildEpisode(11, specs11);
const ep12 = buildEpisode(12, specs12);

const doc = {
  source: '西游记（维基文库·百回）',
  // ep7-9 存在 >6s 的单行台词（称量按 字/4.5 秒，且 coverage 门不允许拆节拍），故 maxCutSeconds 抬到 8。
  params: { ...(cur.params ?? { maxSegmentSeconds: 15, minCutSeconds: 2, maxCutSeconds: 6, maxOnScreen: 3, tolerance: 0.15 }), maxCutSeconds: 8 },
  episodes: [
    ...eps13,
    { ep: 4, segments: ep4 },
    { ep: 5, segments: ep5 },
    { ep: 6, segments: ep6 },
    { ep: 7, segments: ep7 },
    { ep: 8, segments: ep8 },
    { ep: 9, segments: ep9 },
    { ep: 10, segments: ep10 },
    { ep: 11, segments: ep11 },
    { ep: 12, segments: ep12 },
  ],
};

// 去掉可能残留的 seedScenes / scenes（episodes 只留 segments）
for (const ep of doc.episodes) {
  for (const k of Object.keys(ep)) if (k !== 'ep' && k !== 'segments') delete ep[k];
}

const json = JSON.stringify(doc, null, 2);
writeFileSync(SE + 'storyboard.nobom.json', json, 'utf8');
for (const ep of doc.episodes) {
  const s = ep.segments.reduce((n, sg) => n + sg.cuts.reduce((m, c) => m + c.seconds, 0), 0);
  console.log(`ep${ep.ep}: ${ep.segments.length} segs, ${s.toFixed(1)}s`);
}
console.log('wrote storyboard.nobom.json');