# Next.js 笔记 · 渲染模式

> Next.js 的核心优势之一是**把"什么时候、用什么方式渲染"做成可声明的配置**。
> 本节梳理 SSR / SSG / ISR / CSR / Streaming / PPR 的区别与适用场景。

---

## 一、Next.js 支持的渲染模式

| 模式 | 全称 | 何时生成 HTML | 适用 |
|------|------|----------------|------|
| **SSG** | Static Site Generation | 构建时 | 变化不频繁的内容（博客、文档） |
| **ISR** | Incremental Static Regeneration | 构建时 + 后台重生成 | 周期性更新的静态内容 |
| **SSR** | Server-Side Rendering | 每次请求 | 用户个性化、需登录态、需实时数据 |
| **CSR** | Client-Side Rendering | 浏览器 | 不需要 SEO 的纯交互页面（后台系统） |
| **Streaming** | 流式渲染 | 服务端分块推 HTML | 大页面有慢数据，先返回外壳 |
| **PPR** | Partial Prerendering | 静态外壳 + 动态洞 | 14+ 实验性，混合静态/动态最佳 |

---

## 二、SSG：构建时生成

```tsx
// app/about/page.tsx
export default function About() {
  return <h1>关于我们</h1>
}
```

- 没写 `async`、没 `await fetch`、没用 `cookies()` / `headers()`
- Next.js 在 `next build` 时把它生成成静态 HTML
- 部署后**几乎零成本**：直接 CDN 命中

> Next.js 默认**尽可能静态化**。

---

## 三、SSR：每次请求都跑

当组件满足以下任一条件时，**自动变成 SSR**：

- 函数是 `async` 且 `await` 了请求
- 用了 `cookies()` / `headers()` / `searchParams`
- 用了 `export const dynamic = 'force-dynamic'`

```tsx
import { cookies } from 'next/headers'

export default async function Page() {
  const cookieStore = await cookies()   // ← 用了 cookies，自动 SSR
  const session = cookieStore.get('session')
  return <div>Hello, {session?.value}</div>
}
```

---

## 四、ISR：构建后定期重新生成

```tsx
// app/posts/page.tsx
export const revalidate = 60   // ← 60 秒后过期，下次请求后台重新生成

export default async function PostsPage() {
  const posts = await fetch('https://api.example.com/posts').then(r => r.json())
  return <ul>{posts.map(p => <li key={p.id}>{p.title}</li>)}</ul>
}
```

- 表现上像 SSG：用户拿到的是缓存 HTML（快）
- 过期后：先返回旧 HTML，**后台异步**重新生成，下次请求命中新的
- 适合：博客文章列表、新闻列表、商品列表

### 按需重新生成

```ts
import { revalidatePath } from 'next/cache'

// 在某个 Server Action 中
revalidatePath('/posts')      // 让 /posts 缓存失效
revalidatePath('/posts/123')  // 精确到某一篇
```

---

## 五、CSR：客户端渲染

完全不加 `'use client'` 也行——只要把所有交互都放到子 Client 组件里，**外层是 Server**。这才是 Next.js 推荐写法。

但如果是"完全不在乎首屏 SEO 的纯交互页面"（如后台），可以**整体标 Client**：

```tsx
'use client'
import { useState, useEffect } from 'react'

export default function Dashboard() {
  const [data, setData] = useState(null)
  useEffect(() => {
    fetch('/api/dashboard').then(r => r.json()).then(setData)
  }, [])
  // ...
}
```

> 这就退化成了"SPA 风格"的页面。Next.js 没禁止，只是不推荐。

---

## 六、Streaming：流式渲染

**什么时候用**：页面里有"快数据"也有"慢数据"，想让用户先看到外壳，再慢慢填充慢部分。

### 核心机制：`loading.tsx` + `<Suspense>`

```
app/
├── page.tsx           ← 快：直接渲染
├── loading.tsx        ← 等待慢组件时显示
└── slow/
    └── page.tsx       ← 慢：await 一个长耗时数据
```

```tsx
// app/slow/page.tsx
async function getSlowData() {
  await new Promise(r => setTimeout(r, 3000))   // 模拟慢请求
  return '慢数据就绪'
}

export default async function SlowPage() {
  const data = await getSlowData()
  return <p>{data}</p>
}
```

```tsx
// app/loading.tsx
export default function Loading() {
  return <p>加载中...</p>
}
```

> 访问 `/slow` 时，Next.js **立即**推回 HTML + Loading 状态，3 秒后通过**流式 chunk**把真实内容推回浏览器。**用户感受到的就是"页面没卡住"**。

### 手动 Suspense（更细粒度）

```tsx
// app/page.tsx
import { Suspense } from 'react'
import SlowPart from './SlowPart'

export default function Page() {
  return (
    <>
      <h1>外壳内容（秒出）</h1>
      <Suspense fallback={<p>慢部分加载中...</p>}>
        <SlowPart />
      </Suspense>
    </>
  )
}
```

---

## 七、PPR（Partial Prerendering）：静态外壳 + 动态洞

**目标**：同一个页面里，**静态部分走 SSG，动态部分走 SSR/Streaming**。

```tsx
// app/product/[id]/page.tsx
import { Suspense } from 'react'
import { cookies } from 'next/headers'

// 静态部分（构建时生成）
function ProductInfo({ id }: { id: string }) {
  return <h1>Product {id}</h1>
}

// 动态部分（每次请求跑）
async function CartBadge() {
  const cartId = (await cookies()).get('cart')?.value
  return <span>购物车：{cartId ?? '空'}</span>
}

export default async function Page({ params }: { params: { id: string } }) {
  return (
    <>
      <ProductInfo id={params.id} />              {/* 静态 */}
      <Suspense fallback={<span>...</span>}>
        <CartBadge />                              {/* 动态 */}
      </Suspense>
    </>
  )
}
```

### 启用 PPR

```js
// next.config.js
module.exports = {
  experimental: {
    ppr: 'incremental',  // 每个路由可以单独 opt-in
  },
}
```

```tsx
// 在某个 page.tsx 顶部
export const experimental_ppr = true
```

> 状态（截至 Next.js 14）：实验性，需要 `experimental.ppr` 开启，但**这是 Next.js 未来渲染的默认方向**。

---

## 八、路由级渲染控制

```tsx
// 强制静态
export const dynamic = 'force-static'

// 强制动态
export const dynamic = 'force-dynamic'

// ISR：每 60 秒重新生成
export const revalidate = 60

// 不缓存数据 fetch（默认 fetch 是 force-cache）
export const fetchCache = 'force-no-store'

// PPR opt-in
export const experimental_ppr = true
```

---

## 九、模式选择决策树

```
内容是否需要用户登录 / 个性化？
├── 是 → SSR（或 CSR）
│
└── 否
    ├── 数据是否每次请求都不同？
    │   ├── 是 → SSR + Streaming（Suspense 包裹慢部分）
    │   └── 否
    │       ├── 数据是否周期性更新？
    │       │   ├── 是 → ISR（revalidate: N）
    │       │   └── 否 → SSG（最便宜）
    │       └── 是否还有别的慢数据？→ 加 Suspense + Streaming
    │
    └── 是否部分静态 + 部分动态？→ PPR（14+ 实验性）
```

---

## 十、性能与可缓存性关系

| 模式 | 服务器开销 | CDN 友好 | 首屏速度 |
|------|-----------|----------|----------|
| SSG | 构建时一次性 | ✅ | ⚡⚡⚡ |
| ISR | 周期后台生成 | ✅ | ⚡⚡⚡ |
| SSR | 每次请求 | ❌ | ⚡ |
| Streaming | 每次请求分块推 | ❌ | ⚡⚡ |
| PPR | 静态 + 动态结合 | ✅ 静态部分 | ⚡⚡⚡（静态部分） |
| CSR | 几乎无服务端 | ✅ | ⚠️（依赖 JS） |

> 默认追求 **SSG > ISR > SSR+Streaming > SSR > CSR** 的成本顺序。

---

## 十一、对应 demo

- 当前 demo 未专门展示渲染模式切换（每个 demo 都默认 SSG/SSR 按需），后续可补：
  - [ ] ISR 显式 revalidate 切换对照
  - [ ] PPR 实验性 demo
- 相关数据获取 demo：[03_data_fetching](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/nextjs-demo/03_data_fetching)
