#!/usr/bin/env node
/**
 * 把文件名前缀转换为 frontmatter sidebar_position。
 *
 *   01-go-overview.md   -> sidebar_position: 1
 *   04-react-router.md  -> sidebar_position: 4
 *   01-docker-overview.md -> sidebar_position: 1
 *
 * 已有 sidebar_position 的文件跳过；无前缀文件不写入。
 */
import fs from 'node:fs';
import path from 'node:path';

const DOCS = 'docs';
const ROMAN = {I: 1, II: 2, III: 3, IV: 4, V: 5, VI: 6, VII: 7};

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, {withFileTypes: true})) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else if (entry.name.endsWith('.md')) out.push(full);
  }
  return out;
}

function positionOf(filename) {
  const base = path.basename(filename, '.md');
  const roman = base.match(/^([IV]+)_/);
  if (roman && ROMAN[roman[1]]) return ROMAN[roman[1]];
  const numeric = base.match(/^(\d+)_/);
  if (numeric) return Number.parseInt(numeric[1], 10);
  return null;
}

let written = 0;
let skipped = 0;
let unchanged = 0;

for (const file of walk(DOCS)) {
  const pos = positionOf(file);
  if (pos === null) {
    skipped++;
    continue;
  }

  const text = fs.readFileSync(file, 'utf8');
  const nl = text.includes('\r\n') ? '\r\n' : '\n';
  const head = `---${nl}`;
  const endMarker = `${nl}---${nl}`;

  if (text.startsWith(head)) {
    const end = text.indexOf(endMarker, head.length);
    if (end === -1) {
      console.warn(`frontmatter 未闭合，跳过：${file}`);
      continue;
    }
    const fm = text.slice(head.length, end);
    if (/^sidebar_position\s*:/m.test(fm)) {
      unchanged++;
      continue;
    }
    const next = `${head}${fm}${nl}sidebar_position: ${pos}${endMarker}${text.slice(end + endMarker.length)}`;
    fs.writeFileSync(file, next, 'utf8');
  } else {
    const next = `---${nl}sidebar_position: ${pos}${nl}---${nl}${nl}${text}`;
    fs.writeFileSync(file, next, 'utf8');
  }
  written++;
}

console.log(`写入 sidebar_position  ${written}`);
console.log(`已有，保持不变        ${unchanged}`);
console.log(`无前缀，跳过          ${skipped}`);
