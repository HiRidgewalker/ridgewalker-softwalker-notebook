---
title: "Codex 笔记"
---

# Codex 笔记

> 由旧稿重新整理版本，补全了与 ClaudeCode 的对比。旧稿目录已清理，当前以本文为准。

## 一、官方文档

- Prompting 指南：<https://developers.openai.com/codex/prompting>
- 基础配置：<https://developers.openai.com/codex/config-basic>
- Agent 审批与安全：<https://developers.openai.com/codex/agent-approvals-security>

## 二、记忆文件 `AGENTS.md`

Codex 的记忆文件是 **`AGENTS.md`**（不是 ClaudeCode 的 `CLAUDE.md`）。

> `AGENTS.md` 为 Codex 提供持久的项目指南，会随代码库一起传输，在代理开始工作之前应用。请保持其简洁。

### 文件位置

| 级别 | 路径 |
| --- | --- |
| 用户级别 | `~/.codex/AGENTS.md` |
| 项目级别 | `./AGENTS.md` |

## 三、沙箱模式

Codex 提供三种沙箱模式，按权限递增：

| 模式 | 说明 | 适用场景 |
| --- | --- | --- |
| **`read-only`** | 可以查看文件，但未经批准不能编辑或运行命令 | 只读分析、代码审查 |
| **`workspace-write`**（默认） | 读取文件、在工作区内编辑、运行常规本地命令 | 本地日常工作的低摩擦模式 |
| **`danger-full-access`** | 无沙箱限制，移除文件系统和网络边界 | 仅在希望 Codex 拥有完全访问权限时使用 |

## 四、MCP 配置

| 级别 | 路径 |
| --- | --- |
| 用户级别 | `~/.codex/config.toml` |
| 项目级别 | `.codex/config.toml` |

详见 [MCP笔记](../mcp/MCP笔记.md)。

## 五、Tools

### web_search

Codex 自带原生网络搜索工具。本地任务中默认启用 web 搜索，**结果来自 OpenAI 维护的网络搜索缓存**（预先索引的结果而非实时获取页面），降低了从任意实时内容中获取**提示注入**的风险，但仍应将结果视为不可信。

控制方式：

- 使用 `--yolo` 或 `danger-full-access` 沙箱设置时，web 搜索默认使用**实时结果**
- 单次运行传 `--search` 获取最新数据
- 在配置中设 `web_search = "live"` 切换到实时
- 设 `web_search = "disabled"` 关闭工具

## 六、与 ClaudeCode 的对比

| 维度 | ClaudeCode | Codex |
| --- | --- | --- |
| 记忆文件 | `CLAUDE.md` | `AGENTS.md` |
| 默认运行模式 | 基于权限的模式（只读，需授权） | `workspace-write`（工作区内低摩擦） |
| MCP 客户端命令 | `claude mcp add ...` | 通过 `config.toml` 配置 |
| 沙箱 | `/sandbox` 手动开启 | 启动时指定沙箱模式 |
| 思维强度 | 支持调节 | — |
| Skills 机制 | 原生支持 | 支持 |

## 七、相关笔记

- ClaudeCode 详解：[ClaudeCode笔记](./ClaudeCode笔记.md)
- MCP 协议：[MCP笔记](../mcp/MCP笔记.md)
- Skills 概念：[Skills笔记](../skills/Skills笔记.md)