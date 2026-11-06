# Docusaurus 项目结构规范

## 规则

在本仓库新增笔记、blog 文章、图片、视频或其他资源时，一律按本仓库已落地的 Docusaurus 项目结构放置文件：内容按 `docs/`（单技术笔记）与 `blog/`（跨技术文章）分流，媒体资源跟随所属文档就近放置，全站共用资源放 `static/`，可运行 demo 放 `example/`。不新建未经本规范定义的顶层目录。

## 原因

- Docusaurus 对 `docs/`、`blog/`、`static/`、`src/` 有约定语义，按约定放置才能被侧边栏、首页索引、标签聚合等机制自动收录
- 目录结构即唯一索引源：文件放对位置，首页与侧边栏自动生成，无需维护任何索引文件
- 媒体资源就近放置可享受构建期校验（路径错误直接构建失败），避免死链

## 如何应用

### 1. 顶层目录职责

| 目录 | 职责 |
| --- | --- |
| `docs/<slug>/` | 单技术笔记，一主题一目录（`docs/go/`、`docs/docker/`） |
| `blog/` | Tech Blog 文章（跨技术选型、方案总览、多栈整合） |
| `static/` | 全站共用静态资源，以站点根绝对路径引用（`/img/...`） |
| `src/` | 站点自定义代码（swizzle 组件、CSS、clientModules），普通笔记不涉及 |
| `example/` | 可运行代码 demo，笔记通过 GitHub 链接引用，不参与站点构建 |
| `scripts/` | 构建/生成脚本，其中 `gen-index.mjs` 生成首页 `docs/intro.md` |
| `hiduck/` | 写作规则、计划与 PRD |

不要新建 `docs/src`、`docs/assets` 之类的顶层混杂目录；临时内容放主题目录内，站点不感知的草稿不要放进 `docs/`。

### 2. 命名规范

- **笔记与 blog 文件名**：英文小写 kebab-case（`[a-z0-9.-]`），如 `01-go-overview.md`、`markdown-latex-syntax.md`；系列文章用 `01-`、`02-` 数字前缀
- **主题目录名**：英文小写 slug（`Go` → `go`、`Next.js` → `nextjs`、`AI Coding Assistants` → `ai-coding-assistants`）
- **正标题**：frontmatter `title` 与文内 H1 用中文；「文件名给机器与 URL，标题给人」
- 站点展示：目录树、首页、侧边栏条目一律显示文件名（去 `.md`），由 `docusaurus.config.ts` 的 `sidebarItemsGenerator` 自动同步；显式 `sidebar_label` 的文档（如首页）优先

### 3. 媒体资源（图片 / 视频）

优先级从高到低：

1. **文档配套图**：放所属文档附近——笔记用 `docs/<slug>/img/`，引用写相对路径 `![](./img/arch.png)`；blog 用 `blog/img/`
   - 相对引用经 webpack 处理：文件缺失直接构建失败（可查错）、自动加内容 hash
2. **全站共用资源**（favicon、logo、首页 banner 等）：放 `static/img/`，引用写站点根绝对路径 `/img/...`
   - `static/` 原样复制、不校验引用，路径写错不会报错，页面直接 404
3. **大视频 / 超大文件**：不进仓库，笔记里放外链

禁止：为单篇笔记把图片集中丢进 `static/`；在 markdown 里引用仓库外或未提交的本地路径。

### 4. 自动收录机制（无需手工登记）

- 站点首页 = `docs/intro.md`（`slug: /`），由 `scripts/gen-index.mjs` 扫描 `docs/` 生成，**生成物，不要手工编辑**；`npm start` / `npm run build` 的 pre 钩子自动重跑
- 侧边栏完全由目录结构 + `_category_.json` 自动生成，不手工维护
- 主题显示名与顺序：`docs/<slug>/_category_.json` 的 `label` 与 `position`（新主题取现有最大 position +1，当前最大 48）
- 笔记顺序：frontmatter `sidebar_position`；缺省按文件名排序
- 仓库根目录没有 `Catalog.md`，任何旧的索引维护流程已作废

### 5. 结构陷阱

- 目录内只有一篇与目录同名的笔记时（如 `docs/wsl/wsl.md`），必须在 `_category_.json` 写 `"link": null`，否则 Docusaurus 把它当分类索引，侧边栏退化成一个链接
- 笔记间引用用标准 markdown 相对链接：同主题 `[标题](./note-name.md)`，跨主题 `[标题](../wsl/wsl.md)`
- 笔记正文避免 `{}` 裸花括号触发 MDX 解析；本站 `markdown.format: 'md'` 已全局关闭 MDX，但复制网上的 JSX 示例时仍需留意
- 非公式的美元符号写 `\$`，否则会与 KaTeX 行内公式配对（见渲染约定）
