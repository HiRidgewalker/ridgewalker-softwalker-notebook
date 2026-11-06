# Software Tech Notebook

个人软件技术知识库。源文件是纯 markdown，不绑定任何笔记软件；通过 Docusaurus 生成静态站点在浏览器中阅读。

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
| `docs/` | 技术笔记，按 14 个技术域分子目录 |
| `docs/<group>/_category_.json` | 该分类的显示名、顺序、折叠状态 |
| `blog/` | 跨技术主题文章（选型对比、方案总览等），日期统一为 2026-11-06 |
| `Catalog.md` | 跨技术逻辑索引，首页与 agent 导航的索引入口 |
| `example/` | 可运行代码 demo（仓库静态资源，笔记通过 GitHub 链接引用） |
| `hiduck/` | 写作规则、计划与 PRD |
| `scripts/` | 构建与生成脚本 |
| `src/` | Docusaurus 自定义样式 |
| `static/` | 站点静态资源（favicon 等） |
| `build/` | 构建产物，已 gitignore |

## 内容维护

1. 在 `docs/<对应技术域>/` 新增或修改笔记
2. 在 `Catalog.md` 对应主题下加入 `[[笔记名]]`（用于首页索引与 agent 导航）
3. 运行 `npm start` / `npm run build`，会自动生成 `docs/index.md`（站点首页）

跨技术主题文章（选型对比、方案总览、跨栈整合）放在 `blog/`，以博客形式呈现；其余单技术笔记放在 `docs/`。

侧边栏由 `docs/` 目录结构自动生成：

- 分类名与顺序：`docs/<group>/_category_.json`
- 条目顺序：frontmatter `sidebar_position`；未设置时按文件名排序

新增技术域时，创建目录和对应的 `_category_.json` 即可，无需改配置。

笔记间引用使用标准 markdown 链接，Obsidian 与站点都能识别：

- 同目录：`[标题](./笔记名.md)`
- 跨目录：`[标题](../devops/I_Docker笔记.md)`

## Agent 使用

- 索引入口：`Catalog.md`
- 笔记目录：`docs/`（中文主题索引见 Catalog，物理分类见子目录名）
- 全部为标准 markdown，可直接全文读取或 grep
- 代码示例在 `example/`，每个子项目有独立 README
