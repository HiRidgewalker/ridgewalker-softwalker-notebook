---
title: "Claude Code 笔记"
---

# Claude Code 笔记

> 由旧稿重新整理版本。原笔记按时间顺序记录了大量学习截图，本版本删除截图引用、按主题分组重排、补充结构化说明。旧稿目录已清理，当前以本文为准。
>
> 涉及 MCP / Skills / Subagents / Hooks 等概念时，与 [MCP笔记](./MCP笔记.md) / [Skills笔记](./Skills笔记.md) / [Agent总览笔记](./Agent总览笔记.md) 交叉引用。

## 一、是什么

Claude Code 是一个在终端中运行的代理编码助手。它在编码方面表现出色，同时也能做命令行能做的其他事：写文档、跑构建、搜文件、查资料等。

底层由两个组件驱动：

- **模型**：理解代码、推理任务（Sonnet 适合多数编码任务；Opus 适合复杂架构决策）
- **工具**：让 Claude 能采取行动（读文件、编辑、执行 shell、搜索网络、调用外部服务）

可用模型在会话内通过 `/model` 命令切换，或启动时用 `claude --model <name>`。

## 二、代理循环

Claude Code 的核心是 **代理循环**，三个阶段融合：

```
收集上下文（用工具读文件、搜代码）
    ↓
采取行动（编辑、运行命令、调用外部服务）
    ↓
验证结果（跑测试、检查输出）
    ↓
根据上一步的结果决定下一步，循环往复
```

每次循环都涉及工具使用。错误修复会循环多次，重构会涉及广泛的验证。用户可以随时中断，引导 Claude 朝不同方向发展。

## 三、`/sandbox` 详解

### 1. 默认开启 sandbox 吗？

**不开启**。Claude Code 默认运行在基于权限的模式（permission-based model）下，默认只读，在进行修改或运行命令之前会询问权限。Sandbox 是需要主动开启的功能，在会话中输入 `/sandbox` 命令启用。

### 2. 开启 auto-allow 模式后，写权限默认范围？

写入权限默认限定在**当前工作目录及其子目录**；读取权限则覆盖整个系统（除了明确拒绝的目录）。

在 auto-allow 模式下，bash 命令会尝试在 sandbox 内运行并自动允许，无需逐条询问权限；对于无法在 sandbox 内执行的命令（例如需要访问未允许的网络主机），则会回退到常规的权限流程。

### 3. 遇到 sandbox 无法执行的命令怎么办？

Claude Code 内置了 **escape hatch（逃生通道）机制**：当命令因 sandbox 限制失败时（例如网络连接问题或不兼容的工具），Claude 会被提示分析失败原因，并可能使用 `dangerouslyDisableSandbox` 参数重试该命令。

典型场景：

- 安装全局 Python 包（`pip install -g` 或 `pip install --user` 到 sandbox 工作目录之外）会触发逃生通道
- Claude 识别失败、分析原因，然后请求在 sandbox 外执行，用户会看到权限提示并可选择是否允许

## 四、扩展 Claude Code：CLAUDE.md / Skills / Rules / MCP / Subagents / Hooks

| 扩展 | 加载策略 | 解决的问题 |
| --- | --- | --- |
| **CLAUDE.md** | **始终加载**到上下文 | 项目级 / 用户级始终开启的指令和约定 |
| **Skills** | 按需加载 | 命名、可触发的能力封装 |
| **Rules**（`.claude/rules/`） | 模块化指令，部分可按文件路径限定加载 | 把项目约定拆成多个主题文件 |
| **MCP** | 客户端按需调用 MCP Server | 接入外部工具 / 服务 |
| **Subagents** | 委派子任务 | 上下文隔离、并行任务 |
| **Hooks** | 特定事件触发命令 | 自动化工作流 |

> **关键区别**：CLAUDE.md 始终占上下文，Skills 是按需加载的。每个加进来的扩展都会消耗上下文，过多会让 Claude 注意力分散、技能触发失败、丢失约定跟踪。

## 五、CLAUDE.md 文件位置

- **项目级别**：`./.claude/CLAUDE.md` 或 `./CLAUDE.md`
- **用户级别**：`~/.claude/CLAUDE.md`

项目 CLAUDE.md 通过版本控制与团队共享，应放项目级标准而非个人偏好。运行 `/init` 会自动生成起始 CLAUDE.md（如果已存在则建议改进而非覆盖）。

### 5.1 用 `@import` 引入其他文件

CLAUDE.md 可以用 `@path/to/import` 语法导入其他文件，导入的文件在启动时展开并加载到上下文中。相对路径相对于**包含导入的文件**解析（不是工作目录），递归导入最大深度 5 跳。

```md
有关项目概述，请参阅 @README，有关此项目的可用 npm 命令，请参阅 @package.json。

# 其他指令
- git 工作流 @docs/git-instructions.md
```

### 5.2 模块化的 `.claude/rules/`

对于较大的项目，可以用 `.claude/rules/` 目录把指令组织到多个文件：

- 每个 `.md` 文件覆盖一个主题（如 `testing.md` / `api-design.md`）
- 支持子目录组织（如 `frontend/` / `backend/`）
- 没有 `paths` frontmatter 的规则在启动时加载，优先级与 `.claude/CLAUDE.md` 相同
- 带 `paths` frontmatter 的规则只在 Claude 处理匹配文件路径时才加载，节省上下文

## 六、MCP：把外部工具接入 Claude Code

### 6.1 安装命令

```shell
# 基本语法
claude mcp add --transport http <name> <url>

# 真实示例：连接到 Notion
claude mcp add --transport http notion https://mcp.notion.com/mcp

# 带有 Bearer 令牌的示例
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"
```

### 6.2 三种安装范围

| 范围 | 存储位置 | 适用场景 |
| --- | --- | --- |
| **local**（默认） | `~/.claude.json` | 个人服务器、实验配置、含敏感凭据的服务器 |
| **project** | 项目根目录 `.mcp.json`（检入版本控制） | 团队共享、项目特定工具 |
| **user** | `~/.claude.json`（`mcpServers` 字段） | 跨多个项目的个人实用工具 |

选型原则：

- **本地范围**：个人服务器、实验配置或特定于一个项目的敏感凭据
- **项目范围**：团队共享的服务器、项目特定的工具或协作所需的服务
- **用户范围**：跨多个项目需要的个人实用程序、开发工具或经常使用的服务

> **MCP 存储位置小结**：
> - 用户和本地范围：`~/.claude.json`
> - 项目范围：项目根 `.mcp.json`（检入源代码控制）
> - 托管：系统目录 `managed-mcp.json`

项目范围的服务器首次使用前会提示批准（出于安全原因）。如需重置：`claude mcp reset-project-choices`。

### 6.3 常用的 MCP 工具

- `context7`：把库的最新文档注入上下文
  ```shell
  # api-key: ctx7sk-...
  ```

## 七、基本命令速查

| 命令 | 功能 | 示例 |
| --- | --- | --- |
| `claude` | 启动交互模式 | `claude` |
| `claude "task"` | 运行一次性任务 | `claude "fix the build error"` |
| `claude -p "query"` | 运行一次性查询，然后退出 | `claude -p "explain this function"` |
| `claude -c` | 在当前目录中继续最近的对话 | `claude -c` |
| `claude -r` | 恢复之前的对话 | `claude -r` |
| `claude commit` | 创建 Git 提交 | `claude commit` |
| `/clear` | 清除对话历史 | `> /clear` |
| `/help` | 显示可用命令 | `> /help` |
| `exit` / Ctrl+C | 退出 Claude Code | `> exit` |

补充：

```text
/exit | /quit  退出对话
/resume       查看对话历史
/model        查看当前使用的模型
/compact      压缩对话
/clear        清除对话记录
!             添加冒号可以执行命令
```

## 八、常用操作

### 8.1 中断和引导

Claude 在执行过程中可以随时被中断，用户可以引导 Claude 朝不同方向发展。

### 8.2 后台运行任务

任务可以后台运行，不阻塞当前窗口。

### 8.3 回滚

按两下 `Esc` 或输入 `\rewind` 可查看回滚点并选择回滚方式。

### 8.4 浏览图片

- 直接拖动图片到 Claude Code 窗口
- 或 `Ctrl + V` 粘贴

### 8.5 复现 UI 设计稿

把设计稿图片丢给 Claude Code，让它按设计稿实现。

## 九、三种模式

| 模式 | 说明 | 适用 |
| --- | --- | --- |
| **auto-allow** | 自动允许 sandbox 内命令 | 信任的本地工作流 |
| **normal**（默认） | 每次写操作询问权限 | 日常使用 |
| **plan** | Claude 先出方案再执行 | 复杂任务、不熟悉代码库 |

Windows 切换模式快捷键：`alt + m`。

## 十、上下文管理

接近上下文限制时 Claude Code 会自动压缩对话历史，保留重要代码和决策。长会话中 context window 可能被无关对话、文件内容、命令填满，导致性能下降、注意力分散。

实践：

- 任务之间频繁使用 `/clear` 完全重置 context window
- 自动压缩触发时，Claude 会总结最重要的内容（代码模式、文件状态、关键决策）
- 想更精细控制：`/compact <instructions>`，如 `/compact Focus on the API changes`
- 在 CLAUDE.md 中自定义压缩行为，例如：
  ```
  "When compacting, always preserve the full list of modified files and any test commands"
  ```

## 十一、配置文件作用域优先级

当多个作用域配置相同设置时，更具体的作用域优先：

1. **Managed**（最高）- 无法被任何内容覆盖
2. **命令行参数** - 临时会话覆盖
3. **Local** - 覆盖项目和用户设置
4. **Project** - 覆盖用户设置
5. **User**（最低）- 当没有其他内容指定设置时应用

例如：如果在用户设置中允许某个权限，但在项目设置中拒绝，则项目设置优先，权限被阻止。

## 十二、其他特性

### 12.1 Skills

Claude Code 原生支持 Skills 机制，与 [Skills笔记](./Skills笔记.md) 中描述的规范一致：description 决定模型何时主动触发，按需加载内容。

官方文档：[注入动态上下文](https://code.claude.com/docs/zh-CN/skills)

### 12.2 Memory

官方文档：[Memory](https://code.claude.com/docs/zh-CN/memory)

### 12.3 Hooks

特定事件发生时执行命令，用来自动化工作流。官方参考：[Hooks](https://code.claude.com/docs/zh-CN/hooks)

### 12.4 Plugin

[Plugin 文档](https://code.claude.com/docs/zh-CN/plugins)

[官方插件市场](https://code.claude.com/docs/zh-CN/discover-plugins#官方-anthropic-市场)

### 12.5 其他工具 / 扩展

- **ccusage**：查看模型使用量
- **GitHub CLI**：与 GitHub 集成
- **ccundo / cc switch**：回滚与切换
- **Claudia**：第三方增强工具

## 十三、优秀教程

### 视频

- [Claude Code 从 0 到 1 全攻略：MCP / SubAgent / Skill / Hook / 图片 / 上下文处理 / 后台任务](https://www.bilibili.com/video/BV14rzQB9EJj/)
- [最火 AI 编程 Claude Code 详细攻略，一期视频精通](https://www.bilibili.com/video/BV1XGbazvEuh/)

### 文章

- [10 分钟掌握 Claude Code 所有命令指南](https://www.claude-cn.org/posts/Claude-code-commands-guide.html)
- [Claude Code 超详细完整指南](https://blog.csdn.net/weixin_52136627/article/details/149719262)
- [Claude Code 添加 MCP 服务器完整指南](https://zhuanlan.zhihu.com/p/1933624323849032925)

### 资源站

- [easyclaude.com](https://easyclaude.com/)

## 十四、相关笔记

- MCP 协议详解：[MCP笔记](./MCP笔记.md)
- Skills 概念与构建：[Skills笔记](./Skills笔记.md)
- Agent 系统结构：[Agent总览笔记](./Agent总览笔记.md)
- Codex 对比参考：[Codex笔记](./Codex笔记.md)