import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { validateStoryboard, gateReport } from
  '../../.trae/skills/novel-storyboard/scripts/novel-storyboard.mjs';
const DIR = 'd:/study/GitHub/shuohao-skills/三国演义';
const board = JSON.parse(readFileSync(join(DIR, 'storyboard-batch-10.json'), 'utf8'));
const ctx = {
  script: JSON.parse(readFileSync(join(DIR, 'script.json'), 'utf8')),
  outline: JSON.parse(readFileSync(join(DIR, 'outline.json'), 'utf8')),
  cast: JSON.parse(readFileSync(join(DIR, 'cast.json'), 'utf8')),
  art: JSON.parse(readFileSync(join(DIR, 'art.json'), 'utf8')),
};
const gates = gateReport(board, ctx);
console.log('=== 18 道质量门 ===');
for (const g of gates) {
  console.log(`[${g.ok ? 'PASS' : 'FAIL'}] ${g.id}: ${g.label}`);
  if (!g.ok) {
    const list = Array.isArray(g.detail) ? g.detail : (g.detail ?? '');
    console.log('      ', typeof list === 'string' ? list : list.slice(0, 8).join(' | '));
  }
}
const problems = validateStoryboard(board, ctx);
console.log('\nvalidateStoryboard problems:', problems.length);
for (const p of problems.slice(0, 30)) console.log('  -', p);