# workspace/nextjs-demo · Next.js 演示项目集合

> 这里放着与 [[01_Next.js 笔记]] 系列配套的 **4 个独立可运行的 Next.js 14 demo 子项目**。
> 每个子项目可以单独 `npm install && npm run dev` 跑起来。

## 子项目列表

| 子项目 | 演示主题 | 入口 |
|--------|----------|------|
| `01_routing_basic` | 文件式路由、layout、动态段、Catch-all、`<Link>` | [01_routing_basic/README.md](./01_routing_basic/README.md) |
| `02_server_client_components` | Server / Client 组件边界、`'use client'`、`children` 模式、hydration 警告 | [02_server_client_components/README.md](./02_server_client_components/README.md) |
| `03_data_fetching` | Server fetch、`Promise.all` 并行、`revalidate` ISR、`force-dynamic` | [03_data_fetching/README.md](./03_data_fetching/README.md) |
| `04_server_actions` | Server Action + `<form action>` + `useActionState` + 手动调用 | [04_server_actions/README.md](./04_server_actions/README.md) |

## 每个子项目都包含

- 完整的 `package.json`（Next.js 14.2 / React 18.3 / TypeScript 5.4）
- 完整的 `next.config.mjs` / `tsconfig.json` / `next-env.d.ts`
- `app/` 下的多种 page.tsx 演示
- `README.md` 列出涵盖的知识点和观察点

## 统一运行方式

```bash
cd 01_routing_basic    # 或 02_/03_/04_
npm install
npm run dev
# 打开 http://localhost:3000
```

## 设计与命名约定

- **下划线前缀的目录不会被路由**：如 `_components/`、`_lib/`
- 演示项目用 `app/` 目录（App Router）
- 配色一致：黑色顶栏 + 白色主区 + monospace 代码
- 不依赖第三方 UI 库，便于阅读

## 对应笔记

- [[01_Next.js 笔记]] — 总览
- [[02_Next.js 路由笔记]]
- [[03_Next.js Server与Client组件笔记]]
- [[04_Next.js 数据获取与Server Actions笔记]]
- [[05_Next.js 渲染模式笔记]]
- [[06_Next.js 常见问题笔记]]
