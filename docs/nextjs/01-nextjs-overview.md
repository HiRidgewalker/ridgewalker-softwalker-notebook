---
title: "Next.js 笔记 · 总览"
sidebar_position: 1
---

# Next.js 笔记 · 总览

> Next.js 是基于 React 的**全栈应用框架**，由 Vercel 维护。
> 笔记默认基于 **Next.js 14+ App Router** 体系。

## 配套 demo

- [example/nextjs-demo/](https://github.com/HiRidgewalker/soft-tech-notebook/tree/main/example/nextjs-demo) — 4 个独立可运行子项目
  - [01_routing_basic](https://github.com/HiRidgewalker/soft-tech-notebook/tree/main/example/nextjs-demo/01_routing_basic) — App Router 文件式路由
  - [02_server_client_components](https://github.com/HiRidgewalker/soft-tech-notebook/tree/main/example/nextjs-demo/02_server_client_components) — Server / Client 组件边界
  - [03_data_fetching](https://github.com/HiRidgewalker/soft-tech-notebook/tree/main/example/nextjs-demo/03_data_fetching) — Server Component 数据获取
  - [04_server_actions](https://github.com/HiRidgewalker/soft-tech-notebook/tree/main/example/nextjs-demo/04_server_actions) — Server Actions 表单变更

## 目录结构

- [II_Next.js 路由笔记](02-nextjs-routing.md)
- [III_Next.js Server与Client组件笔记](03-nextjs-server-and-client-components.md)
- [IV_Next.js 数据获取与Server Actions笔记](04-nextjs-data-fetching-and-server-actions.md)
- [V_Next.js 渲染模式笔记](05-nextjs-rendering-modes.md)
- [VI_Next.js 常见问题笔记](06-nextjs-faq.md)

---

## 一、Next.js 是什么

**一句话**：Next.js 是 React 的"上半身"，把构建 React 应用所需的大部分工程决策（路由、构建、数据获取、部署、SSR/SSG、图片优化等）**内置到框架里**，让你写"项目"而不是拼凑一堆工具。

它不是一个新框架替代 React，而是 **React 的元框架（meta-framework）**：

- 下层仍是 React（写组件、写 hooks 的方式不变）
- 上层补齐了路由、SSR、构建、部署等所有"做完整应用"必备的能力

---

## 二、Next.js 相对 React SPA 的核心差异

很多人熟悉的是 `create-react-app` / Vite + React Router 这种**单页应用（SPA）**模式。Next.js 的关键差异如下。

### 1. 路由方式

| 维度 | 传统 SPA | Next.js App Router |
|------|----------|---------------------|
| 路由声明 | 在代码里写 `<Route path="...">` 路由表 | 把 `page.tsx` 文件放到对应文件夹，**文件即路由** |
| 路由表维护 | 手动维护，容易漏 | 天然零成本，新文件自动成路由 |
| 嵌套布局 | 需要第三方库或自己写 | 原生 `layout.tsx`，按目录层级自动嵌套 |
| 嵌套加载状态 | 自己写 | 原生 `loading.tsx`，自动 Suspense 包裹 |
| 错误边界 | 自己写 | 原生 `error.tsx` |

### 2. 渲染模型（最根本的差异）

| 模式 | 传统 SPA | Next.js |
|------|----------|---------|
| 默认渲染位置 | 浏览器（CSR） | **服务端**（Server Component 默认） |
| 首屏 HTML | 几乎是空壳 + 巨型 JS bundle | 服务端就生成好完整 HTML |
| SEO | 通常较差（爬虫跑不动 JS 时） | 友好（直接拿到完整内容） |
| 首屏速度 | 受网络+JS 解析拖累 | 更快（HTML 直出，JS 后到） |
| 交互 | 路由切换快 | 同上（App Router 切换时只下载该路由的 RSC payload） |

### 3. 组件的两种形态

Next.js 13+ 引入 **React Server Components (RSC)** 后，组件分为：

- **Server Component（默认）**：在服务端渲染，可以直接 `await fetch`、读数据库，但不能有 `useState` / `useEffect` / 事件处理
- **Client Component**：在文件顶部加 `"use client"`，能用所有 React hooks、能交互

这一划分是 SPA 完全不需要考虑的——SPA 里所有组件都在浏览器跑。

### 4. 数据获取

- **传统 SPA**：组件 `useEffect` 里发请求，有瀑布流问题
- **Next.js**：Server Component 里**直接 `await fetch`**，可以并行，可以缓存，可以在数据就绪前不渲染组件（消除瀑布流）

### 5. 变更与服务端写入

- **传统 SPA**：前端调 REST / GraphQL 接口，后端另外写
- **Next.js**：可以写 **Server Action** —— 一个普通函数直接当 `<form action>` 用，**不需要单独写 API 路由**

### 6. 资源优化内置

Next.js 默认帮你做了一堆优化，不用自己接：

- `<Image>`：自动懒加载、响应式、WebP 转换、CLS 防护
- `<Link>`：客户端导航、预取可见链接
- `next/font`：本地托管字体、零 CLS
- `next/script`：脚本加载策略

### 7. 工程一体化

| 能力 | 传统 SPA 自配 | Next.js |
|------|---------------|---------|
| 构建工具 | 自己选 Vite / Webpack | 内置（Webpack / Turbopack） |
| TypeScript | 手动配 | 开箱即用 |
| CSS Modules | 手动配 | 内置 |
| Tailwind | 手动配 | 一键集成 |
| ESLint | 手动配 | 内置 |
| 部署 | 自己处理 | `next start`，Vercel 一键部署 |

---

## 三、什么时候用 Next.js、什么时候用纯 SPA

### 适合 Next.js

- **有 SEO / 分享 / 首屏速度要求**的内容站、电商、博客、文档站
- **后端能力也想用 JS 一把梭**（BFF 场景）
- **希望框架帮你做对的事**（路由、缓存、图片优化别自己折腾）

### 适合纯 SPA

- 后台管理系统、纯内部工具（不需要 SEO、不在乎首屏）
- 应用逻辑极重、内容极轻（编辑器、设计工具、IDE 类）
- 团队已经重度投资在别的方案上

### 不是二选一

Next.js 也可以在特定路由下用 `"use client"` 退化成纯 SPA 风格，反过来用 Vite + React 也能做 SSR（但要自己接 SSR 框架，如 Remix 或自己用 React 18 streaming）。只是默认选择上，**面向用户的内容型项目，Next.js 是当前最省心的选择**。

---

## 四、Next.js 核心特性速览

按"用得上频率"排：

| 特性 | 用途 | 详见 |
|------|------|------|
| App Router | 文件式路由 + 嵌套布局 + loading/error | [II_Next.js 路由笔记](02-nextjs-routing.md) |
| Server Components | 默认在服务端渲染、减少 JS 体积 | [III_Next.js Server与Client组件笔记](03-nextjs-server-and-client-components.md) |
| Client Components | 交互组件用 `"use client"` 标记 | [III_Next.js Server与Client组件笔记](03-nextjs-server-and-client-components.md) |
| Server-side Fetch | `await fetch()` 在 Server Component | [IV_Next.js 数据获取与Server Actions笔记](04-nextjs-data-fetching-and-server-actions.md) |
| Server Actions | 服务端函数直接当 `<form action>` | [IV_Next.js 数据获取与Server Actions笔记](04-nextjs-data-fetching-and-server-actions.md) |
| 渲染模式 | SSR / SSG / ISR / Streaming / PPR | [V_Next.js 渲染模式笔记](05-nextjs-rendering-modes.md) |
| Image / Link / Font | 资源优化内置组件 | [VI_Next.js 常见问题笔记](06-nextjs-faq.md) |
| Middleware | 在请求到达页面之前跑代码 | [VI_Next.js 常见问题笔记](06-nextjs-faq.md) |
| Route Handlers | 写 API 端点（`route.ts`） | [IV_Next.js 数据获取与Server Actions笔记](04-nextjs-data-fetching-and-server-actions.md) |

---

## 五、版本与术语速记

- **Pages Router**：旧版路由系统（13 之前唯一选择），基于 `pages/` 目录
- **App Router**：13+ 引入、13.4 稳定的新路由系统，基于 `app/` 目录，本笔记默认讲这个
- **RSC (React Server Components)**：服务端组件，与 App Router 配合，是 Next.js 13+ 最大的架构变化
- **Turbopack**：Next.js 13+ 引入的新构建工具（Webpack 替代品），开发模式下启动更快
- **PPR (Partial Prerendering)**：Next.js 14 引入的实验性特性，把页面分成"静态外壳 + 动态洞"

---

## 六、第一个 Next.js 项目（最快 5 分钟起步）

```bash
# 不用 create-next-app 也能用，最小结构就是 app/ 目录里写个 page.tsx
npx create-next-app@latest my-app
# 选项都默认即可：TypeScript / App Router / Tailwind 可选

cd my-app
npm run dev
# 打开 http://localhost:3000
```

最小可运行的 `app/page.tsx`：

```tsx
export default function Home() {
  return <h1>Hello Next.js</h1>
}
```

> 没有任何 `useState`、没有任何 `"use client"`，这就是一个**纯 Server Component**，比 SPA 写法还短。

---

## 七、学习路径建议

1. **先看路由**：弄懂 `app/page.tsx`、`layout.tsx`、`loading.tsx`、`error.tsx` 的作用
2. **再切 Client**：找一处需要交互的地方，加 `"use client"`，感受边界
3. **再学数据获取**：把 `useEffect(fetch)` 改成 `await fetch`，对比差别
4. **再学 Server Actions**：把表单提交从"前端 fetch + 后端 API"改成 `<form action={serverAction}>`
5. **最后学渲染模式**：理解每个路由的"静态 / 动态"对缓存与性能的影响
