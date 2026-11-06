#!/usr/bin/env node
/**
 * 清理历史遗留的 frontmatter 字段，只保留站点实际使用的键。
 *
 * 保留：title / date / sidebar_position / slug / sidebar_label / description
 * 删除：type / topic / status / source / sources
 *
 * 用法：
 *   node scripts/clean-frontmatter.mjs --dry-run
 *   node scripts/clean-frontmatter.mjs
 */
import fs from 'node:fs';
import path from 'node:path';

const KEEP = new Set(['title', 'date', 'sidebar_position', 'slug', 'sidebar_label', 'description']);
const REMOVE = new Set(['type', 'topic', 'status', 'source', 'sources']);
const DRY = process.argv.includes('--dry-run');

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, {withFileTypes: true})) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else if (entry.name.endsWith('.md')) out.push(full);
  }
  return out;
}

function cleanFrontmatter(fm) {
  const lines = fm.split('\n');
  const out = [];
  let skipping = false;

  for (const line of lines) {
    const keyMatch = line.match(/^([A-Za-z_][\w-]*)\s*:/);
    if (keyMatch) {
      const key = keyMatch[1];
      if (KEEP.has(key)) {
        skipping = false;
        out.push(line);
      } else if (REMOVE.has(key)) {
        skipping = true;
      } else {
        // 未知字段：保留，避免误删
        skipping = false;
        out.push(line);
      }
      continue;
    }

    if (skipping) {
      if (line.startsWith(' ') || line.startsWith('\t') || line.startsWith('- ') || line.trim() === '') {
        continue;
      }
      skipping = false;
    }
    out.push(line);
  }

  return out.join('\n');
}

const files = [...walk('docs'), ...walk('blog')];
let changed = 0;
let removed = 0;
const samples = [];

for (const file of files) {
  const text = fs.readFileSync(file, 'utf8');
  const m = text.match(/^(---\r?\n)([\s\S]*?)(\r?\n---\r?\n)/);
  if (!m) continue;

  const cleaned = cleanFrontmatter(m[2]);
  if (cleaned === m[2]) continue;

  const before = m[2].split('\n').length;
  const after = cleaned.split('\n').length;
  removed += before - after;
  changed++;

  if (samples.length < 5) {
    samples.push(`--- ${file}\n${m[2]}\n  ↓\n${cleaned}`);
  }

  if (!DRY) {
    fs.writeFileSync(file, m[1] + cleaned + m[3] + text.slice(m[0].length), 'utf8');
  }
}

console.log(`${DRY ? '[dry-run] ' : ''}清理 ${changed} 个文件，删除 ${removed} 行`);
if (samples.length) {
  console.log('\n--- 样例 ---');
  console.log(samples.slice(0, 2).join('\n\n'));
}
