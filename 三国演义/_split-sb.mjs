// 把 storyboard.json 拆分成分镜批次文件（每批 batchSize 集），子代理填 segments 后各自输出
import { readFileSync, writeFileSync } from "fs";
import { fileURLToPath } from "url";
import path from "path";

const dir = path.dirname(fileURLToPath(import.meta.url));
const strip = s => s.replace(/^\uFEFF/, "");

const sb = JSON.parse(strip(readFileSync(path.join(dir, "storyboard.json"), "utf8")));
const batchSize = 5;
const eps = sb.episodes;
for (let i = 0; i < eps.length; i += batchSize) {
  const chunk = eps.slice(i, i + batchSize).map(ep => JSON.parse(JSON.stringify(ep)));
  const batch = { source: sb.source, promptLang: sb.promptLang, params: sb.params, episodes: chunk };
  const n = i / batchSize + 1;
  writeFileSync(path.join(dir, `storyboard-batch-${n}.json`), JSON.stringify(batch, null, 2), "utf8");
  console.log(`batch-${n}: eps ${chunk[0].ep}-${chunk[chunk.length - 1].ep} (${chunk.length}集)`);
}