#!/usr/bin/env node
/** 为 docs 下每个技术域目录生成 _category_.json。 */
import fs from 'node:fs';
import path from 'node:path';
import {GROUPS} from './lib/catalog-map.mjs';

let created = 0;
for (const group of GROUPS) {
  const dir = path.join('docs', group.dir);
  if (!fs.existsSync(dir)) {
    console.warn(`目录不存在，跳过：${dir}`);
    continue;
  }
  const meta = {
    label: group.label,
    position: group.position,
    collapsed: true,
  };
  fs.writeFileSync(path.join(dir, '_category_.json'), `${JSON.stringify(meta, null, 2)}\n`, 'utf8');
  created++;
}

console.log(`已生成 ${created} 个 _category_.json`);
