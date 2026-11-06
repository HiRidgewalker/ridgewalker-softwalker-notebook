/**
 * Catalog.md 主题 → docs 子目录的映射，供迁移、链接改写与首页生成共用。
 */
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';

export const GROUPS = [
  {dir: 'basics', label: '基础', position: 1, themes: ['Common Use', 'Temporary Storage']},
  {dir: 'languages', label: '编程语言', position: 2, themes: ['Python', 'Go', 'JavaScript', 'TypeScript', 'CSS']},
  {dir: 'frontend', label: '前端框架', position: 3, themes: ['React', 'Next.js']},
  {dir: 'backend', label: '后端框架', position: 4, themes: ['FastAPI', 'Django', 'Celery', 'Pydantic']},
  {dir: 'tooling', label: '开发工具', position: 5, themes: ['uv', 'Anaconda', 'Jupyter', 'Git']},
  {dir: 'database', label: '数据库', position: 6, themes: ['MySQL', 'PostgreSQL', 'SQLite', 'MongoDB', 'Redis']},
  {dir: 'vector-db', label: '向量数据库', position: 7, themes: ['Milvus', 'Qdrant', 'zvec']},
  {dir: 'message-queue', label: '消息队列', position: 8, themes: ['RabbitMQ', 'Kafka']},
  {dir: 'devops', label: 'DevOps', position: 9, themes: ['Docker', 'Kubernetes', 'Harbor', 'Jenkins']},
  {dir: 'linux', label: 'Linux', position: 10, themes: ['Linux', 'WSL', 'Process Management']},
  {
    dir: 'ai',
    label: 'AI 与大模型',
    position: 11,
    themes: ['Machine Learning', 'PyTorch', 'Large Language Models', 'LLM Evaluation', 'Prompt Engineering', 'RAG'],
  },
  {
    dir: 'agent',
    label: 'Agent 与 AI Coding',
    position: 12,
    themes: ['Agent', 'MCP', 'Skills', 'AI Coding Assistants', 'Model & Inference Platform'],
  },
  {dir: 'design', label: '设计', position: 13, themes: ['Figma', 'UI/UX Design']},
  {dir: 'network', label: '网络', position: 14, themes: ['Computer Networks']},
  {dir: 'cross-cutting', label: '跨技术主题', position: 15, themes: ['Cross-cutting Topics']},
];

export function parseCatalog(catalogPath = 'Catalog.md') {
  const sections = {};
  let current = null;
  for (const line of fs.readFileSync(catalogPath, 'utf8').split(/\r?\n/)) {
    const h2 = line.match(/^##\s+(.+?)\s*$/);
    if (h2) {
      current = h2[1].trim();
      sections[current] = [];
      continue;
    }
    const item = line.match(/^-\s+\[\[([^\]]+)\]\]/);
    if (item && current) {
      const name = item[1].split('#')[0].split('|')[0].trim();
      sections[current].push(name);
    }
  }
  return sections;
}

/**
 * @param {string} sourceDir 笔记当前所在目录（迁移前 hub，迁移后 docs）
 * @param {string} targetPrefix 目标路径前缀
 * @returns {Map<string, string>} 文件名（不含 .md）→ 目标相对路径
 */
export function buildFileMap(sourceDir = 'hub', targetPrefix = 'docs') {
  const sections = parseCatalog('Catalog.md');
  const map = new Map();

  for (const group of GROUPS) {
    for (const theme of group.themes) {
      for (const name of sections[theme] ?? []) {
        if (map.has(name)) {
          throw new Error(`笔记在 Catalog 中重复出现：${name}`);
        }
        map.set(name, path.join(targetPrefix, group.dir, `${name}.md`));
      }
    }
  }

  if (fs.existsSync(sourceDir)) {
    const actual = fs
      .readdirSync(sourceDir)
      .filter((f) => f.endsWith('.md') && f !== 'index.md')
      .map((f) => f.replace(/\.md$/, ''));
    const missing = actual.filter((n) => !map.has(n));
    const extra = [...map.keys()].filter((n) => !actual.includes(n));
    if (missing.length) throw new Error(`Catalog 未收录：${missing.join('、')}`);
    if (extra.length) throw new Error(`Catalog 有但文件不存在：${extra.join('、')}`);
  }

  return map;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const map = buildFileMap();
  for (const [name, dest] of [...map].sort((a, b) => a[1].localeCompare(b[1]))) {
    console.log(`${name}.md  ->  ${dest}`);
  }
  console.log(`\n共 ${map.size} 条映射，${GROUPS.length} 个目录`);
}
