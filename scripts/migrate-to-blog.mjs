#!/usr/bin/env node
/**
 * 把 docs/cross-cutting/ 下的跨技术笔记迁移为博客文章。
 *
 * - 文件移动到 blog/，保留原文件名
 * - frontmatter 写入 date: 2026-11-06
 * - 指向 docs 其他目录的链接补上 docs/ 前缀
 *
 * 用法：node scripts/migrate-to-blog.mjs [--dry-run]
 */
import fs from 'node:fs';
import path from 'node:path';

const SRC = path.join('docs', 'cross-cutting');
const DEST = 'blog';
const DATE = '2026-11-06';
const DRY = process.argv.includes('--dry-run');

const files = fs.readdirSync(SRC).filter((f) => f.endsWith('.md'));

for (const file of files) {
  if (fs.existsSync(path.join(DEST, file))) {
    console.error(`目标已存在，拒绝覆盖：${path.join(DEST, file)}`);
    process.exit(1);
  }
}

fs.mkdirSync(DEST, {recursive: true});

let moved = 0;
let links = 0;
const samples = [];

for (const file of files) {
  const src = path.join(SRC, file);
  const dest = path.join(DEST, file);
  let text = fs.readFileSync(src, 'utf8');

  // 1. 跨目录链接补 docs/ 前缀：](../database/X.md) -> ../docs/database/X.md
  text = text.replace(/\]\(\.\.\/(?!example\/|docs\/)([^)]+\.md)(#[^)]*)?\)/g, (match, rel, anchor = '') => {
    links++;
    if (samples.length < 5) samples.push(`${file}: ../${rel} -> ../docs/${rel}`);
    return `](../docs/${rel}${anchor})`;
  });

  // 2. frontmatter 补 date
  const nl = text.includes('\r\n') ? '\r\n' : '\n';
  const head = `---${nl}`;
  const endMarker = `${nl}---${nl}`;

  if (text.startsWith(head)) {
    const end = text.indexOf(endMarker, head.length);
    if (end === -1) {
      console.error(`frontmatter 未闭合：${src}`);
      process.exit(1);
    }
    const fm = text.slice(head.length, end);
    if (!/^date\s*:/m.test(fm)) {
      text = `${head}${fm}${nl}date: ${DATE}${endMarker}${text.slice(end + endMarker.length)}`;
    }
  } else {
    const title = file.replace(/\.md$/, '');
    text = `---${nl}title: ${JSON.stringify(title)}${nl}date: ${DATE}${nl}---${nl}${nl}${text}`;
  }

  if (!DRY) {
    fs.writeFileSync(dest, text, 'utf8');
    fs.rmSync(src);
  }
  moved++;
}

if (!DRY) {
  const remaining = fs.readdirSync(SRC);
  if (remaining.length === 1 && remaining[0] === '_category_.json') {
    fs.rmSync(path.join(SRC, '_category_.json'));
  }
  const left = fs.readdirSync(SRC);
  if (left.length) {
    console.error(`docs/cross-cutting 仍有残留：${left.join(', ')}`);
    process.exit(1);
  }
  fs.rmdirSync(SRC);
}

console.log(`${DRY ? '[dry-run] ' : ''}迁移 ${moved} 篇到 ${DEST}/，改写链接 ${links} 处`);
if (samples.length) {
  console.log('\n样例：');
  for (const s of samples) console.log(`  ${s}`);
}
