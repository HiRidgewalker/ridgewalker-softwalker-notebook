# Next.js 笔记 · 数据获取与 Server Actions

> Next.js 的数据获取**主要在 Server Component** 里完成，配合 **Server Actions** 处理服务端变更。
> 配套 demo：[03_data_fetching](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/nextjs-demo/03_data_fetching) / [04_server_actions](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/nextjs-demo/04_server_actions)

---

## 一、为什么数据获取放在 Server Component

传统 SPA：

```
Component 挂载
  → useEffect 触发 fetch
    → setState
      → 重新渲染
```

- 用户看到"骨架屏"
- 数据请求要等 JS 下载完才发起
- 嵌套组件会出现"瀑布流"（一个接一个请求）

Server Component：

```
请求到达服务器
  → Server Component 顶层直接 await fetch（多个请求可并行）
    → 渲染完整 HTML 返回
      → 浏览器立刻看到内容
```

- 没有骨架屏
- JS 还没下完数据就已经好了
- 多个 fetch 用 `Promise.all` 即可并行，没有瀑布流

---

## 二、最基本的 fetch 用法

```tsx
// app/posts/page.tsx （Server Component）

export default async function PostsPage() {
  const res = await fetch('https://api.example.com/posts')
  const posts = await res.json()

  return (
    <ul>
      {posts.map(p => <li key={p.id}>{p.title}</li>)}
    </ul>
  )
}
```

没有 `useState`、没有 `useEffect`、没有 loading 状态——**在服务端就跑完了**。

---

## 三、Next.js 扩展的 fetch 缓存机制

Next.js 扩展了原生 `fetch`，加了**请求级缓存**。

```ts
// 1. 默认：force-cache
fetch(url)
// → 第一次请求后结果被缓存，后续请求复用

// 2. 显式不缓存
fetch(url, { cache: 'no-store' })
// → 每次都重新请求

// 3. 重新校验：缓存但带过期
fetch(url, { next: { revalidate: 60 } })
// → 缓存 60 秒，过期后下次请求时后台重新生成

// 4. 标签失效
fetch(url, { next: { tags: ['posts'] } })
// → 配合 revalidateTag('posts') 主动失效
```

### 缓存粒度选择

| 场景 | 写法 |
|------|------|
| 博客文章列表（变化不频繁） | `next: { revalidate: 60 }` |
| 用户个性化数据 | `cache: 'no-store'` |
| 实时数据（行情、聊天） | `cache: 'no-store'` + WebSocket |
| 构建时决定的内容 | `next: { revalidate: false }`（永久缓存） |

---

## 四、并行请求：消除瀑布流

```tsx
// ❌ 瀑布流：串行
const user = await fetch('/user').then(r => r.json())
const posts = await fetch(`/users/${user.id}/posts`).then(r => r.json())

// ✅ 并行：同时发起
const [user, posts] = await Promise.all([
  fetch('/user').then(r => r.json()),
  fetch('/posts').then(r => r.json()),
])
```

或者把数据获取放到**子组件**，让 React 并行渲染它们：

```tsx
// app/dashboard/page.tsx
export default function Dashboard() {
  return (
    <>
      <UserInfo />     {/* 自己 fetch /user */}
      <UserPosts />    {/* 自己 fetch /user/:id/posts */}
    </>
  )
}
// 两个组件并行获取，不会一个等另一个
```

---

## 五、`use` Hook：Client 组件里读 Promise

有时 Client 组件也想用 Server 已经准备好的数据，但又不想自己 fetch。可以用 **`use` Hook 拆包 Promise**：

```tsx
// app/page.tsx (Server)
import { Suspense } from 'react'
import Comments from './Comments'

export default function Page() {
  const commentsPromise = fetch('/api/comments').then(r => r.json())

  return (
    <Suspense fallback={<p>加载中...</p>}>
      <Comments commentsPromise={commentsPromise} />
    </Suspense>
  )
}
```

```tsx
// Comments.tsx ('use client')
'use client'
import { use } from 'react'

export default function Comments({ commentsPromise }: { commentsPromise: Promise<any[]> }) {
  const comments = use(commentsPromise)   // ← 拆包，会自动触发 Suspense
  return <ul>{comments.map(c => <li key={c.id}>{c.text}</li>)}</ul>
}
```

> 适用场景：Server 准备好数据 → Client 在交互时**逐步消费**这份数据（如搜索过滤）。

---

## 六、`revalidatePath` / `revalidateTag`：主动失效缓存

### 按路径失效

```ts
// app/actions.ts
'use server'
import { revalidatePath } from 'next/cache'

export async function createPost() {
  // ... 写库
  revalidatePath('/blog')          // 失效 /blog 路由的缓存
  revalidatePath('/blog', 'page')  // 精确指定 page
}
```

### 按标签失效

```ts
// 1. fetch 时打标签
fetch(url, { next: { tags: ['posts'] } })

// 2. Server Action 中主动失效
import { revalidateTag } from 'next/cache'
revalidateTag('posts')   // 所有带 'posts' 标签的请求都失效
```

> **重要**：写操作完成后调用 `revalidatePath` 或 `revalidateTag`，否则用户看到的还是缓存的旧数据。

---

## 七、Server Actions：服务端函数直接当 action 用

### 是什么

Server Action 是**运行在服务端的异步函数**，可以直接绑定到 `<form action>` 上，**完全不需要写 API 路由**。

```tsx
// app/actions.ts
'use server'    // ← 整个文件都是 Server Actions

export async function createPost(formData: FormData) {
  const title = formData.get('title')
  // ... 写数据库
  return { ok: true }
}
```

```tsx
// app/new-post/page.tsx （Server Component）
import { createPost } from '../actions'

export default function NewPostPage() {
  return (
    <form action={createPost}>
      <input name="title" />
      <button type="submit">提交</button>
    </form>
  )
}
```

> 这个 `<form>` **不用 JavaScript 也能工作**（渐进增强）。
> 浏览器原生表单提交 → 直接调用 Server Action。

### 在 Client 组件里调用

```tsx
'use client'
import { createPost } from '../actions'

export default function Form() {
  return (
    <form action={createPost}>
      <input name="title" />
      <button type="submit">提交</button>
    </form>
  )
}
```

> 在 Client 里也能直接当 prop 用，**但要先 `'use client'`**。

### 用 `useActionState` 处理返回与 pending

```tsx
'use client'
import { useActionState } from 'react'
import { createPost } from './actions'

export default function Form() {
  const [state, formAction, isPending] = useActionState(createPost, { ok: false })

  return (
    <form action={formAction}>
      <input name="title" />
      <button disabled={isPending}>{isPending ? '提交中...' : '提交'}</button>
      {state.message && <p>{state.message}</p>}
    </form>
  )
}
```

> `state` 是 action 的返回值，`isPending` 是"提交中"标志。

### 绑定参数：`<form action={action.bind(null, arg)}>`

```tsx
// actions.ts
export async function deletePost(id: string) { ... }

// page.tsx
<form action={deletePost.bind(null, post.id)}>
  <button>删除</button>
</form>
```

---

## 八、Server Actions vs Route Handlers

| 维度 | Server Action | Route Handler (`route.ts`) |
|------|---------------|----------------------------|
| 用途 | 表单提交、按钮点击、mutation | 通用 HTTP 端点（Webhook、REST API） |
| 调用方 | 直接 `<form action>` 或 `useActionState` | 任意 HTTP 客户端 |
| 鉴权 | 函数内部手动做 | 端点入口做 |
| 适用 | 页面内变更 | 跨应用、对接第三方 |

> **优先用 Server Action** 处理"我自己的 UI 触发的写操作"。
> 第三方需要 Webhook / REST API 时用 Route Handler。

---

## 九、数据获取的层级选择

| 场景 | 推荐位置 |
|------|----------|
| 列表页需要用户登录态 | Server Component 顶层 await（鉴权更容易） |
| 用户操作后才需要的附加数据 | Client 组件 `useEffect` 或 Server Action 配合 |
| 初始页面有、用户筛选后再加 | Server 准备基础数据 + Client 用 `use` 拆包过滤 |
| 实时数据（聊天、行情） | Client WebSocket，不要走 Server fetch |

---

## 十、Client 组件里要 fetch 怎么办

并非绝对禁止，但要清楚代价：

```tsx
'use client'
import { useEffect, useState } from 'react'

export default function ClientList() {
  const [data, setData] = useState(null)
  useEffect(() => {
    fetch('/api/list').then(r => r.json()).then(setData)
  }, [])
  if (!data) return <p>加载中...</p>
  return <ul>{data.map(...)}</ul>
}
```

> 适用场景：用户登录后**只在某个交互区域**需要的数据，不在首屏关键路径上。
> 不适用：**首屏就需要的核心数据**（应该放 Server 父组件）。

---

## 十一、对应 demo

- [03_data_fetching](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/nextjs-demo/03_data_fetching) — Server Component 中 fetch、`Promise.all` 并行、`revalidateTag`
- [04_server_actions](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/nextjs-demo/04_server_actions) — Server Action + `<form action>` + `useActionState`
