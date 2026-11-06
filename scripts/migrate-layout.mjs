#!/usr/bin/env node
/**
 * 把 hub/ 下平铺的笔记按 Catalog 映射移动到 docs/<group>/。
 * 执行前做全量预检，任一冲突即中止，避免半途状态。
 */
import fs from 'node:fs';
import path from 'node:path';
import {buildFileMap, GROUPS} from './lib/catalog-map.mjs';

const SRC = 'hub';
const DEST = 'docs';

if (!fs.existsSync(SRC)) {
  console.error(`源目录 ${SRC}/ 不存在`);
  process.exit(1);
}

const map = buildFileMap(SRC, DEST);

for (const [name, dest] of map) {
  const src = path.join(SRC, `${name}.md`);
  if (!fs.existsSync(src)) {
    console.error(`源文件不存在：${src}`);
    process.exit(1);
  }
  if (fs.existsSync(dest)) {
    console.error(`目标已存在，拒绝覆盖：${dest}`);
    process.exit(1);
  }
}

for (const group of GROUPS) {
  fs.mkdirSync(path.join(DEST, group.dir), {recursive: true});
}

let moved = 0;
for (const [name, dest] of map) {
  fs.renameSync(path.join(SRC, `${name}.md`), dest);
  moved++;
}

const generatedIndex = path.join(SRC, 'index.md');
if (fs.existsSync(generatedIndex)) {
  fs.rmSync(generatedIndex);
}

const remaining = fs.readdirSync(SRC);
if (remaining.length) {
  console.error(`hub/ 仍有残留文件，保留目录：${remaining.join(', ')}`);
  process.exit(1);
}
fs.rmdirSync(SRC);

console.log(`已移动 ${moved} 篇笔记到 ${DEST}/，共 ${GROUPS.length} 个目录`);
