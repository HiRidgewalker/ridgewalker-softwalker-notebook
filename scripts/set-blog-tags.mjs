#!/usr/bin/env node
/**
 * 从 Catalog.md 的 Cross-cutting Topics 提取技术栈，写入 blog 文章 frontmatter。
 *
 * 规则：
 *   - 条目后括号内以 / 分隔的技术栈即为 tags
 *   - 每篇最多 5 个，超出直接报错，交给人取舍
 *   - 重复执行结果一致（覆盖已有 tags 行）
 */
import fs from 'node:fs';
import path from 'node:path';

const CATALOG = 'Catalog.md';
const BLOG = 'blog';
const MAX_TAGS = 5;

function parseCrossCuttingTags() {
  const entries = [];
  let current = null;

  for (const line of fs.readFileSync(CATALOG, 'utf8').split(/\r?\n/)) {
    const h2 = line.match(/^##\s+(.+?)\s*$/);
    if (h2) {
      current = h2[1].trim();
      continue;
    }
    if (current !== 'Cross-cutting Topics') continue;

    const item = line.match(/^-\s+\[\[([^\]]+)\]\].*?（([^）]+)）/);
    if (!item) continue;

    const name = item[1].trim();
    const tags = [...new Set(item[2].split('/').map((t) => t.trim()).filter(Boolean))];
    entries.push({name, tags});
  }

  return entries;
}

function writeTags(file, tags) {
  const original = fs.readFileSync(file, 'utf8');
  const match = original.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) throw new Error(`缺少 frontmatter：${file}`);

  const body = original.slice(match[0].length);
  const lines = match[1]
    .split(/\r?\n/)
    .filter((line) => !/^tags\s*:/.test(line));

  const tagsLine = `tags: ${JSON.stringify(tags)}`;
  const dateIndex = lines.findIndex((line) => /^date\s*:/.test(line));
  lines.splice(dateIndex >= 0 ? dateIndex + 1 : lines.length, 0, tagsLine);

  const next = `---\n${lines.join('\n')}\n---${body}`;
  if (next === original) return false;
  fs.writeFileSync(file, next, 'utf8');
  return true;
}

const entries = parseCrossCuttingTags();
if (!entries.length) {
  console.error('Catalog.md 中未找到 Cross-cutting Topics 条目');
  process.exit(1);
}

let updated = 0;
for (const {name, tags} of entries) {
  if (tags.length > MAX_TAGS) {
    console.error(`标签超过 ${MAX_TAGS} 个：${name}（${tags.join(' / ')}）`);
    process.exitCode = 1;
    continue;
  }

  const file = path.join(BLOG, `${name}.md`);
  if (!fs.existsSync(file)) {
    console.error(`找不到博客文章：${file}`);
    process.exitCode = 1;
    continue;
  }

  if (writeTags(file, tags)) updated++;
  console.log(`${name.padEnd(28)} ${tags.join(', ')}`);
}

console.log(`\n共 ${entries.length} 篇，更新 ${updated} 篇`);
