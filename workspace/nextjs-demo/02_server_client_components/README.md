# 02_server_client_components · Server / Client 组件边界 demo

演示 **Next.js 14 中 Server Component 与 Client Component 的划分与组合**。

## 涵盖知识点

- 文件顶部 `'use client'` 标记 Client 组件
- Server 页面 import Client 子组件
- 同一个父页面里混用 Server / Client 子树
- **children 模式**：把 Server 组件作为 children 传给 Client 容器
- Hydration 失败的一个常见原因（用 `Date.now()` / `Math.random()`）

## 路由对照

| 路径 | 演示内容 |
|------|----------|
| `/` | 入口 |
| `/counter` | 顶层 Server 页面 + Client `Counter` + Server `ServerInfo` |
| `/wrapper` | Client 容器 `ClientWrapper` 通过 children 接收 Server `ServerPanel` |
| `/show-time` | ⚠️ 错误示范：Server 组件渲染了不稳定时间戳 |

## 运行

```bash
cd 02_server_client_components
npm install
npm run dev
# 打开 http://localhost:3000
```

## 关键观察点

1. 打开 `/counter`，在 DevTools Network → JS 中搜索 `Counter` 的代码：会看到它被打包进了 chunk
2. 打开 `/counter`，在 JS bundle 里搜索 `ServerInfo` 的内容（比如时间戳相关字符串）：**找不到**，因为它只在服务端跑
3. 打开 `/wrapper` 看 children 模式：Client 容器能 toggle 显隐，但里面的内容是 Server 渲染好的
4. 打开 `/show-time`，打开 DevTools Console，会看到 `Hydration failed` 警告

## 对应笔记

- [[Hub/03_Next.js Server与Client组件笔记]]
