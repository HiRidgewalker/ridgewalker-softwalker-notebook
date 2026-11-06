# Software Tech Notebook

Software Tech Notebook —— 个人软件技术笔记。源文件是纯 markdown，不绑定任何笔记软件；通过 Docusaurus 生成静态站点在浏览器中阅读。

## 快速开始

```bash
npm install
npm start          # 开发服务器 http://localhost:3000
npm run build      # 构建静态站点到 build/
npm run serve      # 预览构建产物
```

## 目录结构

| 路径 | 说明 |
| --- | --- |
| `docs/<slug>/` | 技术笔记，48 个主题即 `docs/` 下的一级目录 |
| `docs/<slug>/_category_.json` | 主题显示名、顺序、折叠状态 |
| `docs/intro.md` | 站点首页，由 `scripts/gen-index.mjs` 扫描 `docs/` 生成 |
| `blog/` | Tech Blog 文章（跨技术选型、方案总览等），日期统一为 2026-11-06 |
| `example/` | 可运行代码 demo（仓库静态资源，笔记通过 GitHub 链接引用） |
| `hiduck/` | 写作规则、计划与 PRD |
| `scripts/` | 构建与生成脚本 |
| `src/` | Docusaurus 自定义样式 |
| `static/` | 站点静态资源（favicon 等） |
| `build/` | 构建产物，已 gitignore |

## 内容维护

目录结构即站点目录：`docs/<slug>/` 一级目录为主题，目录下的 `.md` 文件为文章。

```
docs/                        站点
────────────────────────  ──────────────────────────────
docs/go/                 →    Go（侧边栏分组，_category_.json）
  01-go-overview.md      →      01-go-overview
  02-go-basic-syntax.md  →      02-go-basic-syntax
```

1. 在 `docs/<主题 slug>/` 新增或修改笔记（无对应主题时新建目录与 `_category_.json`）
2. 运行 `npm start` / `npm run build`，自动扫描 `docs/` 生成首页 `docs/intro.md`

主题目录名 = 章节标题转 slug：`Go` → `go`、`Next.js` → `nextjs`、`AI Coding Assistants` → `ai-coding-assistants`。

笔记文件名统一为英文小写 kebab-case（`01-go-overview.md`、`markdown-latex-syntax.md`），系列文章用 `01-`、`02-` 前缀排序；目录树、首页与侧边栏都显示英文文件名。

Tech Blog 文章（跨技术选型、方案总览、跨栈整合）放在 `blog/`；其余单技术笔记放在 `docs/`。Tech Blog 的技术栈标签（最多 5 个）直接维护在文章 frontmatter 的 `tags`。标签显示在文章标题下方，按技术名稳定取色，点击可进入 `/blog/tags/<slug>` 聚合页，样式与取色逻辑在 `src/theme/Tag/`。

侧边栏由目录结构自动生成：

- 目录层级：主题（48 个）→ 文章
- 主题显示名与顺序：`docs/<slug>/_category_.json`
- 文章条目标签：取源文件名（不含 `.md`），由 `docusaurus.config.ts` 的 `sidebarItemsGenerator` 自动同步；显式 `sidebar_label` 的文档（如首页）优先
- 文章顺序：frontmatter `sidebar_position`；未设置时按文件名排序
- 主题目录始终以分组展示；目录内只有一篇与目录同名的笔记时（如 `docs/wsl/wsl.md`），需在该目录 `_category_.json` 写 `"link": null`，否则 Docusaurus 会把它当作分类索引，侧边栏退化为一级链接

笔记间引用使用标准 markdown 链接：

- 同主题：`[标题](./note-name.md)`
- 跨主题：`[标题](../wsl/wsl.md)`

## 渲染能力

| 能力 | 写法 | 说明 |
| --- | --- | --- |
| Mermaid | ```` ```mermaid ```` 代码块 | 浏览器端渲染，支持 flowchart / sequenceDiagram 等 |
| 行内公式 | `$E=mc^2$` | KaTeX 渲染 |
| 块级公式 | `$$ ... $$` | 支持 `\begin{align}`、`\begin{equation}` 等环境 |

正文中表示价格的美元符号要转义为 `\$`（如 `\$0.025`），否则会与行内公式配对。

## Agent 使用

- 索引入口：`docs/` 目录结构（主题 = 一级目录，笔记 = 目录内 `.md`）
- 首页 `docs/intro.md` 是扫描生成的只读索引，可作快速导航
- 全部为标准 markdown，可直接全文读取或 grep
- 代码示例在 `example/`，每个子项目有独立 README
