---
title: "Next.js 笔记 · 常见问题"
sidebar_position: 6
---

# Next.js 笔记 · 常见问题

> 收录 Next.js App Router 开发中最容易踩的坑与对应的速查。
> 详细概念见 [II_Next.js 路由笔记](02-nextjs-routing.md) / [III_Next.js Server与Client组件笔记](03-nextjs-server-and-client-components.md) / [V_Next.js 渲染模式笔记](05-nextjs-rendering-modes.md)

---

## 一、动态 API：什么会让路由变成动态

下面这些用法**都会让整个路由段变成动态渲染**（不再是静态化 SSG/ISR）：

| 用法 | 影响 |
|------|------|
| `cookies()` | 动态 |
| `headers()` | 动态 |
| `searchParams`（作为 props） | 动态 |
| `fetch(url, { cache: 'no-store' })` | 这次请求不缓存 |
| `export const dynamic = 'force-dynamic'` | 强制动态 |

**反过来说**：能不用就别用，能提到子段就用子段，否则整个 layout 链都会变动态。

### 例外：动态 API 也可以配合静态

```tsx
// page.tsx
import { Suspense } from 'react'
import DynamicPart from './DynamicPart'

export default function Page() {
  return (
    <>
      <h1>静态外壳</h1>     {/* 这部分仍然可被预渲染 */}
      <Suspense fallback={<p>加载中...</p>}>
        <DynamicPart />     {/* 动态部分包在 Suspense 里 */}
      </Suspense>
    </>
  )
}
```

> 这就是 Streaming + 部分静态化的雏形（PPR 走得更远）。

---

## 二、`cookies()` / `headers()` 异步化

Next.js 14 起 `cookies()` / `headers()` **返回 Promise**：

```ts
// ✅ 正确（Next.js 14+）
const cookieStore = await cookies()
const session = cookieStore.get('session')

const headersList = await headers()
const userAgent = headersList.get('user-agent')

// ❌ 旧写法（13）会报错
const session = cookies().get('session')
```

> 如果看到 `cookies() should be awaited` 之类的报错，就是忘了 `await`。

---

## 三、环境变量

| 前缀 | 暴露给 | 用途 |
|------|--------|------|
| `NEXT_PUBLIC_*` | 浏览器 + 服务端 | 公开变量（如 API base URL） |
| 不带前缀 | 仅服务端 | 密钥、数据库连接串 |

```ts
// .env.local
DATABASE_URL=postgres://...      // 仅服务端可见
NEXT_PUBLIC_SITE_URL=https://x   // 浏览器也能读
```

> 服务端组件里 `process.env.DATABASE_URL` 正常可用。
> Client 组件里读 `process.env.DATABASE_URL` 是 `undefined`（安全）。

---

## 四、`<Image>` 与 `<Link>`

### `<Image>`

```tsx
import Image from 'next/image'

<Image
  src="/hero.png"
  alt="封面"
  width={800}
  height={400}
  priority             // 首屏关键图片，关掉懒加载
/>
```

- 自动懒加载、自动响应式、自动转 WebP
- **必须传 `width` + `height`**（或用 `fill` 配合 `position: relative` 的父容器）
- 远程图片需要在 `next.config.js` 的 `images.remotePatterns` 配置允许的域名

### `<Link>`

```tsx
import Link from 'next/link'

<Link href="/about">关于</Link>
<Link href={{ pathname: '/blog/[slug]', query: { slug: 'x' } }}>博客</Link>
<Link href="/x" prefetch={false}>不快取</Link>
<Link href="/x" replace>替换历史</Link>
```

- 默认 prefetch 进入视口的链接
- 内部链接走客户端导航，**不要**用 `<a>` 内部跳转

### `<Script>`

```tsx
import Script from 'next/script'

<Script src="https://example.com/analytics.js" strategy="afterInteractive" />
```

- `strategy`: `beforeInteractive` / `afterInteractive` / `lazyOnload` / `worker`

---

## 五、Middleware：在请求到达页面前跑

`middleware.ts` 放在**项目根目录**（与 `app/` 平级）或 `src/` 下。

```ts
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // 例：检查 token
  const token = request.cookies.get('token')?.value
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
  return NextResponse.next()
}

// 限定匹配范围
export const config = {
  matcher: ['/dashboard/:path*', '/api/protected/:path*'],
}
```

> 用途：鉴权、A/B 测试、地理位置重定向、添加请求头。

---

## 六、`'use client'` 常见误用

| 误用 | 后果 | 正确做法 |
|------|------|----------|
| 整个页面加 `'use client'` | 首屏 HTML 变空，丧失 SEO 优势 | 顶层 Server，只把交互子树标 Client |
| 在 Client 组件里 import Server 组件 | 报错 | 用 `children` 模式从父 Server 传入 |
| 在 Server 组件里写 `onClick` | 报错 | 把那一行拆到 Client 子组件 |
| `'use client'` 写在文件中间 | 编译错误 | 必须文件**最顶部**，import 之前 |
| 给纯展示组件加 `'use client'` | 增加 bundle 体积 | 没必要加 |

---

## 七、常见错误速查

| 报错 | 原因 | 修复 |
|------|------|------|
| `You're importing a component that imports useState. It only works in a Client Component` | Server 组件里用了 hooks | 加 `'use client'` 或拆出 Client 子组件 |
| `Event handlers cannot be passed to Client Component props` | 给 Client 组件传了函数 prop | 把函数包在 Client 子组件里 |
| `cookies() should be awaited` | 14+ 异步化 | `await cookies()` |
| `Route ... used \`searchParams\` ... cannot be static` | searchParams 让路由变动态 | 显式接受动态，或用 `searchParams` 配合 Suspense |
| `params should be awaited` | 15+ 异步化 | `const { id } = await params` |
| `Hydration failed` | 服务端和客户端渲染不一致 | 不要在渲染中用 `Date.now()` / `Math.random()` / `window` |

---

## 八、文件命名规范

| 位置 | 命名 | 备注 |
|------|------|------|
| `app/page.tsx` | 必须小写 | 路由入口 |
| `app/layout.tsx` | 必须小写 | 布局 |
| `app/_components/` | 下划线开头 | 私有文件夹，不被路由 |
| 组件文件 | PascalCase | `UserCard.tsx` |
| 工具函数 | camelCase 或 kebab-case | `format-date.ts` |

---

## 九、TypeScript 类型

### 路由参数

```tsx
type Props = {
  params: Promise<{ slug: string }>           // Next.js 15+
  searchParams: Promise<{ [k: string]: string | string[] | undefined }>
}

export default async function Page({ params, searchParams }: Props) {
  const { slug } = await params
  const { q } = await searchParams
}
```

### Page props 完整签名（Next.js 14）

```tsx
type Props = {
  params: { slug: string }
  searchParams?: { [key: string]: string | string[] | undefined }
}
```

### 环境变量类型

```ts
// next-env.d.ts（自动生成）
/// <reference types="next" />
/// <reference types="next/image-types/global" />
```

> 自定义 env 变量类型可以在 `env.d.ts` 里写：

```ts
namespace NodeJS {
  interface ProcessEnv {
    DATABASE_URL: string
    NEXT_PUBLIC_SITE_URL: string
  }
}
```

---

## 十、构建与部署

### 本地开发

```bash
npm run dev          # 默认
npm run dev --turbo  # 启用 Turbopack（更快）
```

### 构建

```bash
npm run build        # 生产构建
npm run start        # 跑生产服务
```

### 部署目标

| 平台 | 支持 |
|------|------|
| Vercel | 一键，最佳体验 |
| Node.js 自托管 | `next start`，需要 Node 18.17+ |
| Docker | 用 `node:18-alpine` + `next start` |
| 静态导出 | `next export`（注意：App Router 静态导出能力有限） |

### 静态导出（`output: 'export'`）

```js
// next.config.js
module.exports = {
  output: 'export',
}
```

- 把整个站生成成纯静态文件
- 限制：**不能用** Server Actions、Route Handlers（带动态参数）、`cookies()` / `headers()`、中间件
- 适合：纯内容站、博客、文档

---

## 十一、容易忽略的小点

1. **`app/` 和 `pages/` 不能共存于一个项目**
2. **`app/` 下**所有文件**都默认是"路由系统的一部分"**，未被识别的文件名会被忽略
3. **Server Component** 里不要用 `Date.now()` / `Math.random()` —— 这会导致构建期/运行期渲染不一致
4. **Client 组件**用的库（包括 UI 组件库）必须自己支持 RSC，否则会报错
5. **`'use client'` 是模块级**：整个文件 + 它 import 的所有东西都被传染
6. **Server Action 默认需要重新验证**：写操作后记得 `revalidatePath` / `revalidateTag`
7. **Client fetch 不要绕过 Server 父组件拉首屏数据**——首屏会"白一下"

---

## 十二、对应 demo

- [01_routing_basic](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/nextjs-demo/01_routing_basic) — 文件式路由、layout、动态段
- [02_server_client_components](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/nextjs-demo/02_server_client_components) — Server/Client 边界、误用对照
- [03_data_fetching](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/nextjs-demo/03_data_fetching) — Server fetch、缓存、revalidate
- [04_server_actions](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/nextjs-demo/04_server_actions) — Server Action + useActionState
