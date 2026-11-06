# 基本能力

@hiduck/general-rule/直面需求编写笔记
@hiduck/general-rule/快速上手优先
@hiduck/general-rule/常用特性优先
@hiduck/general-rule/跳跃知识点简要解释
@hiduck/general-rule/mermaid可视化表达规范
@hiduck/general-rule/docusaurus项目结构规范

## 仓库定位

本仓库是 Software Tech Notebook，个人软件技术笔记。源文件为纯 markdown，不绑定任何笔记软件；通过 Docusaurus 生成静态站点（`docs/` 为知识正文，`blog/` 为跨技术文章）。`docs/` 下现有 48 个主题目录、97 篇笔记。

## 如何辅助记录技术

当用户想记录一个技术栈、学习一个技术组件或编写一篇技术文章时，直接基于该技术组件编写完整的学习文档笔记，不逐步追问大纲和素材。笔记以实用为主：快速上手优先、常用特性优先、原理简要说明并附在线详解链接、必要时用 Mermaid 图示辅助理解。

- 写作姿态：[直面需求编写笔记.md](hiduck/general-rule/直面需求编写笔记.md)
- 内容取舍：[快速上手优先.md](hiduck/general-rule/快速上手优先.md) · [常用特性优先.md](hiduck/general-rule/常用特性优先.md) · [跳跃知识点简要解释.md](hiduck/general-rule/跳跃知识点简要解释.md)
- 表达方式：[mermaid可视化表达规范.md](hiduck/general-rule/mermaid可视化表达规范.md)
- 项目结构：[docusaurus项目结构规范.md](hiduck/general-rule/docusaurus项目结构规范.md)

## 语言偏好

- 后续所有描述性内容、非技术名词，全部使用中文描述

## 命名规范（全局强制）

- **笔记文件名**：英文小写 kebab-case（`[a-z0-9.-]`），如 `01-go-overview.md`、`markdown-latex-syntax.md`；系列文章用 `01-`、`02-` 数字前缀排序
- **主题目录名**：英文小写 slug（`Go` → `go`、`Next.js` → `nextjs`、`AI Coding Assistants` → `ai-coding-assistants`）
- **blog 文件名**：当前仍是中文；新建 blog 文章时同样使用英文小写 kebab-case
- **正标题**：frontmatter `title` 与文内 H1 保持中文，如 `title: "Go 笔记（总览）"`；文件名与标题分工是「文件名给机器与 URL，标题给人」
- 站点展示规则：目录树、首页、侧边栏条目一律显示文件名（去 `.md`），侧边栏标签由 `docusaurus.config.ts` 的 `sidebarItemsGenerator` 自动取文件名，与源文件名始终同步；显式 `sidebar_label` 的文档（如首页）优先

## SOP：新增技术笔记

前提：用户说「记一篇 X 笔记 / 学习 X / 写 X 的文章」时按此流程执行，无需追问细节。

1. **定位主题目录**：找到 `docs/` 下对应主题目录（如 Go 笔记 → `docs/go/`）
   - 已有主题：直接放入
   - 无对应主题：新建 `docs/<slug>/` + `_category_.json`，`position` 取现有最大值 +1（当前最大 48），`label` 用技术名原文（如 `Rust`），`collapsed: true`
2. **创建笔记文件**：`docs/<slug>/<英文kebab-case>.md`；系列文章加 `01-`、`02-` 前缀
3. **frontmatter**（最少必要）：
   - `title: "中文名"` —— 页面 H1 与分页标题
   - `description: "一句话说明"` —— 可选，会显示在首页条目后
   - `sidebar_position: N` —— 同目录多篇时控制顺序；单篇或希望按文件名排时可省略
4. **写正文**：遵循「如何辅助记录技术」的写作规则；配图放 `docs/<slug>/img/` 用相对路径引用（`![](./img/arch.png)`），全站共用图放 `static/img/` 用 `/img/...` 引用；需要可运行 demo 时按「代码演示外置 example 模式」处理
5. **笔记间引用**：标准 markdown 相对链接，同主题 `[标题](./note-name.md)`，跨主题 `[标题](../wsl/wsl.md)`
6. **无需登记索引**：首页 `docs/intro.md` 与侧边栏由目录结构自动生成，新增文件即自动收录；`npm start` / `npm run build` 前会自动重跑生成脚本

单笔记主题注意：目录内只有一篇与目录同名的笔记时（如 `docs/wsl/wsl.md`），必须在 `_category_.json` 写 `"link": null`，否则 Docusaurus 把它当分类索引，侧边栏退化成一个链接。

## SOP：新增 Tech Blog 文章

适用：跨技术选型对比、方案总览、多栈整合类内容（单技术内容一律走上面的笔记 SOP）。

1. **创建文件**：`blog/<英文kebab-case>.md`
2. **frontmatter 必须带**：
   ```yaml
   ---
   title: "中文标题"
   date: YYYY-MM-DD
   tags: ["技术名1", "技术名2"]   # 技术栈标签，最多 5 个
   ---
   ```
   `tags` 用技术名原文（如 `"Docker"`、`"FastAPI"`、`"AI Coding Assistants"`），与 docs 主题名一致可复用现有配色；标签显示在文章标题下方，按标签名稳定取色（`src/theme/Tag`），点击进入 `/blog/tags/<slug>` 聚合页
3. **正文写作**同笔记规则（配图放 `blog/img/` 相对引用）；站点导航栏已有 Tech Blog 入口，无需额外登记

## 代码演示外置 example 模式

- 可运行代码示例从笔记中提炼到 `example/` 目录下作为可执行 demo
- 笔记通过 GitHub 仓库链接引用 demo：`https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/...`（目录用 `tree`，分支固定 `main`）
- 各子项目的目录结构与约定见 [example/README.md](example/README.md)

## 笔记渲染约定

- Mermaid：用 ```` ```mermaid ```` 代码块，主题已配置，浏览器端渲染
- 数学公式：KaTeX 渲染，行内写 `$E=mc^2$`，块级写 `$$ ... $$`，支持 `\begin{align}`、`\begin{equation}` 等环境
- 非公式的美元符号必须转义为 `\$`，公式内也不要出现未转义的 `$`（KaTeX 会报错）
- 配置位置：`docusaurus.config.ts` 中 docs/blog 的 `remarkPlugins` / `rehypePlugins`；KaTeX 样式由 `src/clientModules/katex.ts` 本地引入

## 站点机制（了解即可，日常无需操作）

- 站点首页 = `docs/intro.md`（`slug: /`），由 `scripts/gen-index.mjs` 扫描 `docs/` 生成：主题顺序取 `_category_.json` 的 `position`，笔记顺序取 frontmatter `sidebar_position`（缺省按文件名），说明取 frontmatter `description`。生成物，**不要手工编辑**
- 侧边栏完全由目录结构 + `_category_.json` 自动生成，不手工维护
- `npm start` / `npm run build` 的 pre 钩子自动执行 `npm run gen:index` 重新生成首页，日常不需要手动跑
- 浏览：`npm start`（开发服务器 http://localhost:3000）或 `npm run build && npm run serve`（静态产物）；部署配置在 `wrangler.jsonc`（Cloudflare Workers 静态资产）
- 仓库根目录不再有 `Catalog.md`；任何旧的索引维护流程已作废，目录结构即唯一索引源
