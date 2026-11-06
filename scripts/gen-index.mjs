#!/usr/bin/env node
/**
 * 扫描 docs/ 目录生成 docs/intro.md（站点首页）。
 *
 * 目录结构是唯一索引源：
 *   docs/<slug>/_category_.json -> 主题显示名与顺序
 *   docs/<slug>/*.md            -> 主题下的文章，frontmatter sidebar_position 或文件名排序
 * intro.md 是生成物，不要手工编辑。
 */
import fs from 'node:fs';
import path from 'node:path';

const DOCS = path.resolve('docs');
const OUT = path.join(DOCS, 'intro.md');

function readFrontmatter(text) {
  const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return {};
  const fm = {};
  for (const line of match[1].split(/\r?\n/)) {
    const m = line.match(/^([\w-]+)\s*:\s*(.*)$/);
    if (m) fm[m[1]] = m[2].trim().replace(/^["']|["']$/g, '');
  }
  return fm;
}

function listThemes() {
  const themes = [];
  for (const entry of fs.readdirSync(DOCS, {withFileTypes: true})) {
    if (!entry.isDirectory()) continue;
    const dir = path.join(DOCS, entry.name);
    const metaFile = path.join(dir, '_category_.json');
    const meta = fs.existsSync(metaFile)
      ? JSON.parse(fs.readFileSync(metaFile, 'utf8'))
      : {};
    const notes = fs
      .readdirSync(dir)
      .filter((f) => f.endsWith('.md'))
      .map((file) => {
        const fm = readFrontmatter(fs.readFileSync(path.join(dir, file), 'utf8'));
        const position = Number.parseInt(fm.sidebar_position, 10);
        return {
          name: path.basename(file, '.md'),
          href: `./${entry.name}/${file}`,
          position: Number.isNaN(position) ? null : position,
          description: fm.description ?? '',
        };
      })
      .sort(
        (a, b) =>
          (a.position ?? Infinity) - (b.position ?? Infinity) ||
          a.name.localeCompare(b.name),
      );
    themes.push({
      slug: entry.name,
      label: meta.label ?? entry.name,
      position: meta.position ?? Infinity,
      notes,
    });
  }
  return themes.sort(
    (a, b) => a.position - b.position || a.label.localeCompare(b.label),
  );
}

const themes = listThemes();
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
out.push('> 索引源为 `docs/` 目录结构与 `_category_.json`；本页由 `scripts/gen-index.mjs` 生成。');
out.push('');

let total = 0;
for (const theme of themes) {
  if (!theme.notes.length) continue;
  out.push(`## ${theme.label}`);
  out.push('');
  for (const note of theme.notes) {
    total++;
    const desc = note.description ? ` — ${note.description}` : '';
    out.push(`- [${note.name}](${note.href})${desc}`);
  }
  out.push('');
}

fs.writeFileSync(OUT, out.join('\n'), 'utf8');
console.log(
  `已生成 ${path.relative(process.cwd(), OUT)}：${themes.filter((t) => t.notes.length).length} 个主题，${total} 篇笔记`,
);
