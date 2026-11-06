/**
 * 以 Catalog.md 为唯一目录源：
 *   ## 主题标题 -> docs/<slug>/
 *   主题下的 [[笔记]] -> 该目录下的文章
 */
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

export function slugify(title) {
  return title
    .toLowerCase()
    .replace(/&/g, ' ')
    .replace(/\//g, '-')
    .replace(/\./g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

export function parseCatalog(catalogPath = 'Catalog.md') {
  const themes = [];
  let current = null;

  for (const line of fs.readFileSync(catalogPath, 'utf8').split(/\r?\n/)) {
    const h2 = line.match(/^##\s+(.+?)\s*$/);
    if (h2) {
      current = {title: h2[1].trim(), slug: slugify(h2[1].trim()), notes: []};
      themes.push(current);
      continue;
    }
    const item = line.match(/^-\s+\[\[([^\]]+)\]\]/);
    if (item && current) {
      const name = item[1].split('#')[0].split('|')[0].trim();
      current.notes.push(name);
    }
  }

  const seenSlug = new Map();
  for (const t of themes) {
    if (seenSlug.has(t.slug)) {
      throw new Error(`主题 slug 冲突：${t.title} 与 ${seenSlug.get(t.slug)} 都映射到 ${t.slug}`);
    }
    seenSlug.set(t.slug, t.title);
  }

  return themes;
}

export const BLOG_THEME = 'Cross-cutting Topics';

/**
 * @returns {{themes: Array, fileMap: Map<string, string>}}
 *   fileMap: 笔记名 -> docs/<slug>/<name>.md
 */
export function buildThemeMap(sourceDir = 'docs', targetDir = 'docs') {
  const themes = parseCatalog();
  const fileMap = new Map();

  for (const theme of themes) {
    if (theme.title === BLOG_THEME) continue;
    for (const name of theme.notes) {
      if (fileMap.has(name)) {
        throw new Error(`笔记重复出现在多个主题：${name}`);
      }
      fileMap.set(name, path.join(targetDir, theme.slug, `${name}.md`));
    }
  }

  if (fs.existsSync(sourceDir)) {
    const actual = [];
    const walk = (dir) => {
      for (const entry of fs.readdirSync(dir, {withFileTypes: true})) {
        const full = path.join(dir, entry.name);
        if (entry.isDirectory()) walk(full);
        else if (entry.name.endsWith('.md') && entry.name !== 'index.md') {
          actual.push(path.basename(entry.name, '.md'));
        }
      }
    };
    walk(sourceDir);
    const missing = actual.filter((n) => !fileMap.has(n));
    if (missing.length) throw new Error(`docs 中未匹配到主题的笔记：${missing.join('、')}`);
  }

  return {themes, fileMap};
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const {themes, fileMap} = buildThemeMap();
  const docsThemes = themes.filter((t) => t.title !== BLOG_THEME);
  for (const t of docsThemes) {
    console.log(`${t.title.padEnd(28)} ${t.slug.padEnd(26)} ${t.notes.length} 篇`);
  }
  console.log(`\n主题 ${docsThemes.length} 个，笔记 ${fileMap.size} 篇`);
}
