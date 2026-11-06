#!/usr/bin/env node
/**
 * 迁移后链接改写：
 *   1. 同目录 .md 链接按新目录结构重算相对路径
 *   2. ../example/... 改为新仓库的 GitHub 绝对链接
 *
 * 页内锚点（](#...)）与外部链接不动。
 */
import fs from 'node:fs';
import path from 'node:path';

const DOCS = 'docs';
const REPO = 'https://github.com/HiRidgewalker/soft-tech-notebook';

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, {withFileTypes: true})) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else if (entry.name.endsWith('.md')) out.push(full);
  }
  return out;
}

const files = walk(DOCS);

const byName = new Map();
for (const file of files) {
  const name = path.basename(file, '.md');
  if (byName.has(name)) {
    console.error(`重名笔记，无法唯一定位：${name}`);
    process.exit(1);
  }
  byName.set(name, file);
}

const stats = {internal: 0, example: 0, unresolved: 0, anchorOnly: 0};
const unresolved = [];

function toHref(fromDir, targetFile, anchor) {
  let rel = path.relative(fromDir, targetFile).split(path.sep).join('/');
  if (!rel.startsWith('.')) rel = `./${rel}`;
  rel = rel.replace(/ /g, '%20');
  return `${rel}${anchor}`;
}

for (const file of files) {
  const fromDir = path.dirname(file);
  const original = fs.readFileSync(file, 'utf8');

  let next = original.replace(/\]\(\.\/([^)#\s]+?\.md)(#[^)]*)?\)/g, (match, rawTarget, anchor = '') => {
    const name = decodeURIComponent(rawTarget).replace(/\.md$/, '');
    const dest = byName.get(name);
    if (!dest) {
      stats.unresolved++;
      unresolved.push(`${file}: ./${rawTarget}`);
      return match;
    }
    stats.internal++;
    return `](${toHref(fromDir, dest, anchor)})`;
  });

  next = next.replace(/\]\((\.\.\/example\/[^)\s]+)\)/g, (match, rel) => {
    const clean = rel.replace(/^\.\.\//, '').replace(/\/$/, '');
    const isDir = !path.extname(clean);
    const kind = isDir ? 'tree' : 'blob';
    stats.example++;
    return `](${REPO}/${kind}/main/${clean})`;
  });

  // 统计页内锚点，仅用于报告
  stats.anchorOnly += (original.match(/\]\(#[^)]+\)/g) || []).length;

  if (next !== original) {
    fs.writeFileSync(file, next, 'utf8');
  }
}

console.log(`扫描文件        ${files.length}`);
console.log(`内部链接改写    ${stats.internal}`);
console.log(`example 链接    ${stats.example}`);
console.log(`页内锚点保留    ${stats.anchorOnly}`);
console.log(`无法解析目标    ${stats.unresolved}`);

if (unresolved.length) {
  console.log('\n--- 无法解析的链接 ---');
  for (const u of unresolved) console.log(`  ${u}`);
  process.exitCode = 1;
}
