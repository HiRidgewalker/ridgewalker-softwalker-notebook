#!/usr/bin/env node
/**
 * 从 Catalog.md 生成 docs/index.md（站点首页）。
 *
 * Catalog.md 是唯一索引源，index.md 是生成物，不要手工编辑。
 * 链接按笔记在 docs/ 下的实际子目录换算。
 */
import fs from 'node:fs';
import path from 'node:path';

const CATALOG = path.resolve('Catalog.md');
const DOCS = path.resolve('docs');
const OUT = path.join(DOCS, 'index.md');

function scanDocs(dir) {
  const map = new Map();
  for (const entry of fs.readdirSync(dir, {withFileTypes: true})) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      for (const [name, file] of scanDocs(full)) map.set(name, file);
    } else if (entry.name.endsWith('.md') && entry.name !== 'index.md') {
      map.set(path.basename(entry.name, '.md'), full);
    }
  }
  return map;
}

function scanBlog(dir) {
  const map = new Map();
  if (!fs.existsSync(dir)) return map;
  for (const entry of fs.readdirSync(dir)) {
    if (!entry.endsWith('.md')) continue;
    const name = path.basename(entry, '.md');
    map.set(name, `/blog/${name}`);
  }
  return map;
}

const docFiles = scanDocs(DOCS);
const blogFiles = scanBlog(path.resolve('blog'));

function toHref(name) {
  const full = docFiles.get(name);
  if (full) {
    const rel = path.relative(DOCS, full).split(path.sep).join('/');
    return `./${rel.replace(/ /g, '%20')}`;
  }
  const blogHref = blogFiles.get(name);
  if (blogHref) return blogHref.replace(/ /g, '%20');
  return null;
}

const raw = fs.readFileSync(CATALOG, 'utf8');
const lines = raw.split(/\r?\n/);

const sections = [];
let current = null;

for (const line of lines) {
  const h2 = line.match(/^##\s+(.+?)\s*$/);
  if (h2) {
    current = {title: h2[1].trim(), items: []};
    sections.push(current);
    continue;
  }
  const item = line.match(/^-\s+\[\[([^\]]+)\]\](.*)$/);
  if (item && current) {
    const name = item[1].trim();
    const target = name.split('#')[0].split('|')[0].trim();
    const rest = item[2].replace(/^\s*[—–-]\s*/, '').trim();
    current.items.push({target, label: name, desc: rest});
  }
}

const out = [];
out.push('---');
out.push('slug: /');
out.push('title: Software Tech Notebook');
out.push('sidebar_label: 首页');
out.push('sidebar_position: 0');
out.push('---');
out.push('');
out.push('# Software Tech Notebook');
out.push('');
out.push('> Software Tech Notebook —— 个人软件技术笔记。左侧边栏按技术域分类，右上角可全文搜索。');
out.push('>');
out.push('> 索引源为仓库根目录的 `Catalog.md`；本页由 `scripts/gen-index.mjs` 生成。');
out.push('');

let total = 0;
let missing = 0;
for (const sec of sections) {
  if (!sec.items.length) continue;
  out.push(`## ${sec.title}`);
  out.push('');
  for (const it of sec.items) {
    const href = toHref(it.target);
    if (!href) {
      console.warn(`  [跳过] 找不到笔记：${it.target}`);
      missing++;
      continue;
    }
    total++;
    const desc = it.desc ? ` — ${it.desc}` : '';
    out.push(`- [${it.label}](${href})${desc}`);
  }
  out.push('');
}

fs.writeFileSync(OUT, out.join('\n'), 'utf8');
console.log(
  `已生成 ${path.relative(process.cwd(), OUT)}：${sections.length} 个主题，${total} 篇笔记` +
    (blogFiles.size ? `（其中 ${blogFiles.size} 篇为博客文章）` : '') +
    (missing ? `（${missing} 条未找到）` : '')
);
