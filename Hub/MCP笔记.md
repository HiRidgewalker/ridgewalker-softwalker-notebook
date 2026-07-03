# MCP 笔记

> 原 `文档/MCP学习笔记.md` 的重新整理版本，补全了 MCP 概念、架构、三种传输方式对比、三类原语、生态。原笔记保留在原位置供回溯。

## 一、MCP 是什么

**MCP（Model Context Protocol，模型上下文协议）** 是由 Anthropic 提出的开放协议，目标是为 LLM 应用提供一套**标准化的工具 / 资源接入方式**。

它解决的问题：

- 每个 LLM 应用（Claude Code、Cursor、Cline 等）想接入工具，都要自己实现一套适配逻辑
- 不同工具的接口、鉴权、数据格式各异，难以复用
- MCP 通过统一协议，让**任何 MCP Server 都能被任何 MCP Client 调用**，类似"AI 时代的 USB-C 接口"

---

## 二、MCP 架构

MCP 采用经典的 **Host / Client / Server** 三层架构：

| 角色 | 职责 | 例子 |
| --- | --- | --- |
| **Host** | 跑 LLM 的应用，负责与用户交互 | Claude Code、Cursor、Cline |
| **Client** | 在 Host 内维护与 Server 的连接，转发 LLM 的工具调用 | MCP Client SDK |
| **Server** | 暴露具体能力（资源 / 工具 / 提示词），响应 Client 请求 | 文件系统 MCP Server、Git MCP Server、数据库 MCP Server |

一次工具调用的典型链路：

```
LLM 决定调工具
  ↓
Host 通过 MCP Client 发出标准化请求
  ↓
MCP Server 接收并执行
  ↓
结果通过 Client 回传给 LLM
```

---

## 三、三种传输方式

MCP 规范定义了三种主流传输方式（transport），用于 Client 和 Server 之间的通信。

### 1. stdio

- **机制**：本地进程间通信
- **原理**：MCP Server 作为子进程，通过标准输入 / 标准输出和 Client 通信
- **适用场景**：本地工具（文件系统、Git、数据库本地访问）
- **优点**：零网络开销、部署简单
- **现状**：**最常见、最推荐用于本地场景**

### 2. SSE（Server-Sent Events）

- **机制**：基于 HTTP，服务端通过 SSE 向客户端单向推送消息
- **原理**：长连接 + 事件流
- **适用场景**：早期的远程 MCP Server
- **现状**：偏旧，很多文档里会叫 **legacy SSE transport**，新项目建议直接用 Streamable HTTP

### 3. Streamable HTTP

- **机制**：也叫 **HTTP transport / Streaming HTTP**
- **原理**：使用标准 HTTP POST / GET 通信，可选用 SSE 做流式返回
- **适用场景**：**远程 MCP Server 的当前推荐方案**
- **优点**：请求更标准、与现有 HTTP 基础设施兼容好、可选流式返回

### 三种方式对比

| 维度 | stdio | SSE | Streamable HTTP |
| --- | --- | --- | --- |
| 通信介质 | 进程 stdio | HTTP + SSE | 标准 HTTP |
| 部署位置 | 本地 | 远程 | 远程 |
| 推荐度 | 本地首选 | 已不推荐 | **远程首选** |
| 流式返回 | 不需要 | 原生支持 | 可选 SSE |
| 与现有基础设施兼容性 | 差 | 中 | 好 |

> 选型原则：**本地用 stdio，远程用 Streamable HTTP**。SSE 仅出现在遗留系统中。

---

## 四、三类原语（Primitives）

MCP Server 可以暴露三类能力：

| 原语 | 作用 | 典型例子 |
| --- | --- | --- |
| **Resources（资源）** | 提供只读、结构化或非结构化的数据 | 文件内容、数据库表、网页内容 |
| **Tools（工具）** | 提供可执行的副作用操作 | 发邮件、写文件、调 API |
| **Prompts（提示词）** | 提供预定义的提示模板 | 常用 prompt 模板、few-shot 模板 |

LLM 通过 MCP Client 可以**列出**这些能力（list）并**调用**它们（call / read / render）。

---

## 五、生态资源

### 官方

- [Model Context Protocol 官方仓库](https://github.com/modelcontextprotocol)
- [Python SDK 文档](https://py.sdk.modelcontextprotocol.io/)
- [官方 Server 收集平台](https://github.com/modelcontextprotocol/servers)

### 社区平台

- [阿里云百炼 MCP 市场](https://bailian.console.aliyun.com/tab=mcp#/mcp-market)
- [smithery.ai/servers](https://smithery.ai/servers)
- [mcp.so/zh](https://mcp.so/zh)
- [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)
- [Microsoft Learn MCP](https://learn.microsoft.com/api/mcp)

### 中文资源

- [MCPcn.com](https://mcpcn.com/)

---

## 六、为什么 SSE 变 legacy

SSE 的主要问题：

1. **单向**：SSE 本身只支持服务端 → 客户端推送，反向通信需要额外 HTTP POST，协议复杂
2. **HTTP/2 不友好**：很多代理、网关、CDN 对长连接支持差
3. **与现有 REST 基础设施割裂**：需要专门的 endpoint 和事件格式

Streamable HTTP 解决了这些问题：双向通信、标准 HTTP POST / GET、可以选 SSE 做流式返回而不强制长连接。

---

## 七、与 Skills 的关系

- **MCP 解决"工具如何接入"** —— 标准化协议，跨应用复用
- **Skills 解决"能力如何组织"** —— 把一组 Tool + 文档 + 工作流封装成可自动触发的单元

二者并不冲突，**一个 Skill 内部完全可以调用 MCP Server 提供的 Tool**。