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
| `docs/<slug>/` | 技术笔记，`Catalog.md` 的 48 个主题即 `docs/` 下的一级目录 |
| `docs/<slug>/_category_.json` | 主题显示名、顺序、折叠状态 |
| `blog/` | Tech Blog 文章（跨技术选型、方案总览等），日期统一为 2026-11-06 |
| `Catalog.md` | 跨技术逻辑索引，首页与 agent 导航的索引入口 |
| `example/` | 可运行代码 demo（仓库静态资源，笔记通过 GitHub 链接引用） |
| `hiduck/` | 写作规则、计划与 PRD |
| `scripts/` | 构建与生成脚本 |
| `src/` | Docusaurus 自定义样式 |
| `static/` | 站点静态资源（favicon 等） |
| `build/` | 构建产物，已 gitignore |

## 内容维护

目录结构严格对应 `Catalog.md`：`##` 主题即 `docs/` 下的一级目录，主题下的 `[[笔记]]` 为文章；`# Catalog` 只是文档标题，不生成目录。

```
Catalog.md                 站点目录
─────────────────────────  ──────────────────────────────
## Go                 →    Go          docs/go/
- [[I_Go笔记]]        →      I_Go笔记
```

1. 在 `Catalog.md` 新增或调整 `##` 主题
2. 在 `docs/<主题 slug>/` 新增或修改笔记
3. 在 `Catalog.md` 对应主题下加入 `[[笔记名]]`
4. 运行 `npm start` / `npm run build`，自动生成 `docs/index.md`

主题目录名 = 章节标题转 slug：`Go` → `go`、`Next.js` → `nextjs`、`AI Coding Assistants` → `ai-coding-assistants`。

Tech Blog 文章（跨技术选型、方案总览、跨栈整合）放在 `blog/`；其余单技术笔记放在 `docs/`。

Tech Blog 的技术栈标签来自 `Catalog.md` 条目后的括号标注，最多 5 个，写入 frontmatter 的 `tags`：

```bash
npm run gen:tags    # 从 Catalog.md 同步 blog/*.md 的 tags
```

标签显示在文章标题下方，按技术名稳定取色，点击可进入 `/blog/tags/<slug>` 聚合页。样式与取色逻辑在 `src/theme/Tag/`。

侧边栏由目录结构自动生成：

- 目录层级：主题（48 个）→ 文章
- 主题显示名与顺序：`docs/<slug>/_category_.json`
- 文章顺序：frontmatter `sidebar_position`；未设置时按文件名排序

笔记间引用使用标准 markdown 链接：

- 同主题：`[标题](./笔记名.md)`
- 跨主题：`[标题](../wsl/WSL笔记.md)`

## Agent 使用

- 索引入口：`Catalog.md`
- 笔记目录：`docs/<slug>/`（主题划分见 `Catalog.md`）
- 全部为标准 markdown，可直接全文读取或 grep
- 代码示例在 `example/`，每个子项目有独立 README
