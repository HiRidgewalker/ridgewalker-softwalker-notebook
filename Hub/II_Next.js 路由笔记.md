# Next.js 笔记 · 路由（App Router）

> App Router 是 Next.js 13+ 引入的**文件式路由系统**。
> 核心思想：**文件夹 = URL 段，文件 = 路由角色**。
> 配套 demo：[01_routing_basic](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/nextjs-demo/01_routing_basic)

## 一、文件即路由：约定文件

`app/` 目录下，每个文件夹对应 URL 的一段，每个特殊文件名对应一种"角色"。

| 文件 | 角色 | 是否必填 |
|------|------|----------|
| `page.tsx` | 该路由的页面 UI | 是（否则该段不出现在 URL 里） |
| `layout.tsx` | 包裹当前段与子段的**共享布局** | 否（但 `app/layout.tsx` 是根布局，必填） |
| `loading.tsx` | 加载状态（自动被 `<Suspense>` 包裹） | 否 |
| `error.tsx` | 错误边界（必须是 Client Component） | 否 |
| `not-found.tsx` | 404 页面 | 否 |
| `route.ts` | 该路径的 API 端点（不能与 `page.tsx` 同目录） | 否 |
| `template.tsx` | 类似 `layout` 但每次导航重新挂载 | 否 |
| `default.tsx` | 平行路由的兜底渲染 | 否 |

### 最简结构

```
app/
├── layout.tsx        ← 根布局（必须）
├── page.tsx          ← /
└── globals.css
```

`app/page.tsx`：

```tsx
export default function Home() {
  return <h1>Home</h1>
}
```

`app/layout.tsx`：

```tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh">
      <body>{children}</body>
    </html>
  )
}
```

---

## 二、嵌套路由：文件夹嵌套 = URL 嵌套

```
app/
├── page.tsx              → /
├── about/
│   └── page.tsx          → /about
└── blog/
    ├── page.tsx          → /blog
    └── [slug]/
        └── page.tsx      → /blog/:slug
```

- `app/blog/page.tsx` → `/blog`
- `app/blog/first/page.tsx` → `/blog/first`（**优先于**动态段）
- `app/blog/[slug]/page.tsx` → `/blog/anything-else`

> 越具体的路径（静态段）越优先匹配。

---

## 三、布局（layout）的嵌套特性

`layout.tsx` 在每个段都会**包裹**该段与所有子段，**且不会重新渲染**（导航切换时持久化）。

```
app/
├── layout.tsx            ← 根布局，包裹所有页面
└── dashboard/
    ├── layout.tsx        ← 只包裹 /dashboard 下的页面
    └── page.tsx
```

`app/dashboard/layout.tsx`：

```tsx
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="dashboard">
      <aside>侧边栏</aside>
      <main>{children}</main>
    </div>
  )
}
```

> 切换 `/dashboard` 与 `/dashboard/settings` 时，`layout` 不会卸载重挂载，状态会保留。

---

## 四、动态段

### 1. 单个动态段 `[slug]`

```
app/blog/[slug]/page.tsx
```

```tsx
export default function Post({ params }: { params: { slug: string } }) {
  return <h1>Post: {params.slug}</h1>
}
```

- 访问 `/blog/hello` → `params.slug === 'hello'`
- `params` 在 Server Component 里是**同步可用的**

### 2. Catch-all `[...slug]`

```
app/docs/[...slug]/page.tsx
```

- `/docs/a` → `params.slug === ['a']`
- `/docs/a/b/c` → `params.slug === ['a', 'b', 'c']`
- `/docs` → 404（**不会匹配**）

### 3. Optional Catch-all `[[...slug]]`

```
app/docs/[[...slug]]/page.tsx
```

- `/docs` → `params.slug === undefined`
- `/docs/a/b` → `params.slug === ['a', 'b']`

> 用法：常用于把"目录页"和"嵌套页"合到一个路由文件里。

### 4. 访问 query 参数

```tsx
// app/search/page.tsx
type Props = {
  searchParams: { q?: string }
}

export default function Search({ searchParams }: Props) {
  return <p>搜索：{searchParams.q}</p>
}
```

> ⚠️ `searchParams` 是动态的——用了它**整个路由会变成动态渲染**（无法静态化）。

---

## 五、特殊文件夹

### 1. 路由组 `(group)`：组织用，不影响 URL

```
app/
├── (marketing)/
│   ├── about/page.tsx      → /about
│   └── pricing/page.tsx    → /pricing
└── (app)/
    ├── dashboard/page.tsx  → /dashboard
    └── settings/page.tsx   → /settings
```

- 用法：**让多个段共享 layout**，但 URL 里没有 `marketing` / `app` 这一段
- 多个路由组可以**各自有不同的 `layout.tsx`**

### 2. 私有文件夹 `_folder`：不会被路由

```
app/
├── _components/        ← Next.js 不会把它当路由
│   └── Button.tsx      ← 可以正常 import 使用
└── page.tsx
```

> 约定：下划线开头的文件夹是"实现细节"，**不会被视为路由段**。

---

## 六、平行路由 `@slot`（Parallel Routes）

一个路由下可以**同时**渲染多个独立可导航的"槽位"。

```
app/
├── layout.tsx
├── page.tsx
├── @modal/
│   └── default.tsx
└── @sidebar/
    └── default.tsx
```

`app/layout.tsx`：

```tsx
export default function Layout({
  children,
  modal,
  sidebar,
}: {
  children: React.ReactNode
  modal: React.ReactNode
  sidebar: React.ReactNode
}) {
  return (
    <>
      {sidebar}
      {children}
      {modal}
    </>
  )
}
```

> 用法：常用于"模态框叠加在主内容上"、"侧边栏独立可替换"等。

---

## 七、拦截路由 `(.)` `(..)` `(..)(..)` `(...)`

**当用户通过前端导航**（`<Link>`）到达某路由时，可以**不跳转**而是用"拦截"覆盖当前页面（典型应用：模态弹窗展示详情页）。

```
app/
├── @modal/
│   ├── (.)photos/
│   │   └── [id]/
│   │       └── page.tsx   ← 拦截 /photos/[id]，在 modal 槽位渲染
│   └── default.tsx
└── photos/
    └── [id]/
        └── page.tsx        ← 正常 /photos/[id] 页面
```

| 写法 | 含义 |
|------|------|
| `(.)` | 拦截**同层级**的路由 |
| `(..)` | 拦截**上一层级**的路由 |
| `(..)(..)` | 拦截**上上一层级** |
| `(...)` | 拦截**根** `app/` 下的路由 |

> 刷新页面时（直接访问 URL）走"正常页面"分支，模态弹窗只在客户端导航触发。

---

## 八、客户端导航：`<Link>`

```tsx
import Link from 'next/link'

<Link href="/about">关于我们</Link>
<Link href={{ pathname: '/blog/[slug]', query: { slug: 'hello' } }}>博客</Link>
```

- 自动启用**客户端导航**（SPA 风格，无白屏）
- 默认**预取（prefetch）**视口内的链接 —— 进入视口就预下载
- 想关掉预取：`<Link href="/x" prefetch={false}>`
- 想强制替换当前历史记录（不留上一页）：`<Link href="/x" replace>`

---

## 九、编程式导航：`useRouter`

```tsx
'use client'
import { useRouter } from 'next/navigation'

function MyButton() {
  const router = useRouter()
  return <button onClick={() => router.push('/about')}>跳转</button>
}
```

- `router.push(href)`：入栈跳转
- `router.replace(href)`：替换当前历史
- `router.back()` / `router.forward()`：前进后退
- `router.refresh()`：刷新当前路由（重新跑 Server Component）
- `router.prefetch(href)`：手动预取

> ⚠️ App Router 里的 `useRouter` 来自 `next/navigation`，**不是**老版本 `next/router`。

---

## 十、404 与未找到页面

```
app/not-found.tsx      ← 全局 404
app/blog/not-found.tsx ← /blog/* 下的 404
```

手动触发 404：

```tsx
import { notFound } from 'next/navigation'

export default function Page({ params }: { params: { id: string } }) {
  if (!exists(params.id)) notFound()
  return <div>{params.id}</div>
}
```

---

## 十一、路由段配置（`export const`）

每个 `page.tsx` / `layout.tsx` 可以通过 `export const` 设置该段的渲染行为：

```tsx
// 强制动态渲染（不走缓存）
export const dynamic = 'force-dynamic'

// 强制静态
export const dynamic = 'force-static'

// ISR：每 60 秒重新生成
export const revalidate = 60
```

详见 [[05_Next.js 渲染模式笔记]]。

---

## 十二、API 端点：Route Handlers

不需要 `page.tsx`，写一个 `route.ts` 就成了一个 HTTP 端点。

```
app/api/hello/route.ts
```

```ts
export async function GET() {
  return Response.json({ msg: 'hello' })
}

export async function POST(request: Request) {
  const data = await request.json()
  return Response.json({ received: data })
}
```

> 注意：`route.ts` 与 `page.tsx` **不能在同一个目录**（二选一）。

---

## 十三、最常见的两个踩坑

1. **`app/` 目录是 App Router，`pages/` 目录是 Pages Router**，**两者不能混用**于同一个项目
2. **误把组件文件放到 `app/` 下**：所有放在 `app/` 下的文件都默认走路由系统，**只有特殊文件名才有效**，其它文件名会被忽略。**实现组件放 `app/_components/` 或 `components/`**

---

## 十四、对应 demo

- [01_routing_basic](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/nextjs-demo/01_routing_basic) — 文件式路由 + 嵌套布局 + 动态段 + 路由组
- 路由组 `(group)` 与平行路由 `@slot` 在主线 demo 里没全展开，需要时单独起 demo
