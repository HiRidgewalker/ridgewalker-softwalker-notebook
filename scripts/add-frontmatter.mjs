#!/usr/bin/env node
/**
 * 为缺少 title 的笔记补 frontmatter。
 *
 *   - 无 frontmatter：从第一个 H1 提取 title，插入
 *   - 有 frontmatter 但无 title：补 title
 *   - 已有 title：跳过
 *
 * 用法：
 *   node scripts/add-frontmatter.mjs --dry-run
 *   node scripts/add-frontmatter.mjs
 */
import fs from 'node:fs';
import path from 'node:path';

const HUB = path.resolve('hub');
const DRY_RUN = process.argv.includes('--dry-run');

function stripFencedCode(text) {
  return text.replace(/(`{3,}|~{3,})[\s\S]*?\1/g, '');
}

function extractH1(body) {
  const m = stripFencedCode(body).match(/^#\s+(.+?)\s*$/m);
  return m ? m[1].trim() : null;
}

const stats = {scanned: 0, added: 0, patched: 0, skipped: 0, fallback: 0};
const samples = [];

for (const file of fs.readdirSync(HUB).filter((f) => f.endsWith('.md'))) {
  stats.scanned++;
  const full = path.join(HUB, file);
  const original = fs.readFileSync(full, 'utf8');

  const hasFm = original.startsWith('---\n') || original.startsWith('---\r\n');

  if (hasFm) {
    const close = original.indexOf('\n---', 3);
    if (close === -1) {
      stats.skipped++;
      continue;
    }
    const fm = original.slice(4, close);
    if (/^title\s*:/m.test(fm)) {
      stats.skipped++;
      continue;
    }
    const body = original.slice(close + 4);
    const title = extractH1(body);
    if (!title) {
      stats.skipped++;
      continue;
    }
    const next = `---\ntitle: ${JSON.stringify(title)}\n${fm}\n---${body}`;
    stats.patched++;
    if (samples.length < 5) samples.push(`${file}: 补 title -> ${title}`);
    if (!DRY_RUN) fs.writeFileSync(full, next, 'utf8');
  } else {
    let title = extractH1(original);
    if (!title) {
      title = file.replace(/\.md$/, '');
      stats.fallback++;
    }
    const next = `---\ntitle: ${JSON.stringify(title)}\n---\n\n${original}`;
    stats.added++;
    if (samples.length < 5) samples.push(`${file}: 新增 -> ${title}`);
    if (!DRY_RUN) fs.writeFileSync(full, next, 'utf8');
  }
}

console.log(`\n${'='.repeat(48)}`);
console.log(`frontmatter 补齐${DRY_RUN ? '（DRY RUN）' : ''}`);
console.log('='.repeat(48));
console.log(`扫描          ${stats.scanned}`);
console.log(`新增          ${stats.added}`);
console.log(`补 title      ${stats.patched}`);
console.log(`跳过(已有)    ${stats.skipped}`);
console.log(`兜底用文件名  ${stats.fallback}`);
if (samples.length) {
  console.log('\n样例：');
  for (const s of samples) console.log(`  ${s}`);
}
