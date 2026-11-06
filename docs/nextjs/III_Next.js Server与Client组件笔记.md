---
title: "Next.js 笔记 · Server 与 Client 组件"
sidebar_position: 3
---

# Next.js 笔记 · Server 与 Client 组件

> App Router 最核心的概念就是 **Server Component vs Client Component** 的划分。
> 配套 demo：[02_server_client_components](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/nextjs-demo/02_server_client_components)

## 一、为什么会有这种划分

传统 React 项目里**所有组件都在浏览器跑**，需要交互就 `useState` / `useEffect` / `onClick`，**没有"服务端组件"这个概念**。

但 App Router 引入了 React Server Components（RSC），允许组件：

- **在服务端渲染**（不发送到浏览器）
- **直接 `await fetch` / 读数据库 / 读文件**（不暴露密钥给前端）
- **不打包进 JS bundle**（首屏 JS 体积更小）

代价是：**服务端组件不能用浏览器侧的能力**（`useState`、`window`、`onClick` 等）。

为了兼顾"能跑服务端"和"能交互"，Next.js 给了两套组件模型。

---

## 二、两个组件模型对照

| 维度 | Server Component（默认） | Client Component |
|------|--------------------------|------------------|
| 标记方式 | 不需要标记 | 文件**顶部**加 `'use client'` |
| 运行环境 | 仅服务端 | 浏览器（也会在服务端预渲染 HTML） |
| 能用 hooks | ❌ | ✅ `useState` / `useEffect` / `useReducer` 等 |
| 能用事件 | ❌（`onClick` 等会报错） | ✅ |
| 能 `await fetch` | ✅（直接 await，无需 useEffect） | ❌（要 `useEffect` + 状态） |
| 能读环境变量 | ✅ 读所有变量（含 `SECRET_*`） | ❌ 只能读 `NEXT_PUBLIC_*` |
| 能用 `window` / `document` | ❌ | ✅ |
| 打包进 bundle | ❌ 不打包 | ✅ 打包 |
| 序列化为 RSC payload | ✅ 嵌套子组件可被序列化传入 | ✅ 也能接收 |

> 简单记：**没加 `'use client'` 就是 Server Component**，加了就变成 Client Component。

---

## 三、怎么写一个 Server Component

```tsx
// app/posts/page.tsx
// 注意：没有任何 'use client'

async function getPosts() {
  const res = await fetch('https://api.example.com/posts')
  return res.json()
}

export default async function PostsPage() {
  const posts = await getPosts()      // ← 直接 await，没有 useEffect
  return (
    <ul>
      {posts.map(p => <li key={p.id}>{p.title}</li>)}
    </ul>
  )
}
```

- 组件函数是 `async function`
- 顶层就能 `await`，**根本不需要 loading state 写法**
- 因为不打包到浏览器，**fetch 不会出现在客户端 bundle**

---

## 四、怎么写一个 Client Component

只要在**文件顶部**加 `'use client'`，整个文件**以及它 import 的所有东西**都被当作 Client。

```tsx
// app/counter/Counter.tsx
'use client'   // ← 一定要在文件最顶部，import 之前

import { useState } from 'react'

export default function Counter() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(c => c + 1)}>count: {count}</button>
}
```

> 父页面（`page.tsx`）可以是 Server Component，把 `<Counter />` 当作子节点用，**没毛病**。

---

## 五、最关键的概念：边界（Boundary）

`'use client'` 标记一个**边界**：从该文件起，所有子组件都被视作 Client 组件树的一部分。

```
app/page.tsx          ← Server（默认）
└── <Counter />       ← Client（import 自带 'use client' 的文件）
    └── <Display />   ← 也是 Client（因为父是 Client）
```

**反过来不行**：

```tsx
'use client'
import ServerOnlyThing from './ServerOnlyThing'   // ❌ 报错
```

> Client 组件**不能 import** Server 组件。
> 但 Server 组件**可以渲染** Client 组件，也可以把 Server 组件作为 `children` / props 传给 Client 组件（这是合法的，会被序列化）。

### 边界是"按文件 import 划"，不是"按函数"

```tsx
// FileA.tsx
export default function A() { return <div>A</div> }
```

```tsx
// FileB.tsx  ← 即使 FileA 没 'use client'，FileB 加了以后
'use client'        // A 在这里是 Client Component
import A from './FileA'
```

> `'use client'` 是**模块级**的，会传染到所有从该文件 import 的子模块。

---

## 六、Server 组件如何"嵌入"Client 组件

两种方式都合法。

### 方式 1：直接 import + 用 JSX

```tsx
// app/page.tsx（Server）
import Counter from './Counter'    // Counter 是 Client

export default function Page() {
  return (
    <div>
      <h1>标题</h1>
      <Counter />
    </div>
  )
}
```

### 方式 2：把 Server 组件作为 `children` / props 传给 Client

```tsx
// app/page.tsx（Server）
import ClientWrapper from './ClientWrapper'
import ServerPanel from './ServerPanel'

export default function Page() {
  return (
    <ClientWrapper>
      <ServerPanel />   {/* 这是 Server 组件，被作为 children 传过去 */}
    </ClientWrapper>
  )
}
```

```tsx
// ClientWrapper.tsx
'use client'

export default function ClientWrapper({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(true)
  return open ? <div>{children}</div> : null
}
```

> 这是合法的！Next.js 会在服务端把 `<ServerPanel />` 先渲染好，再把结果**序列化**后传给 Client。

> ⚠️ 注意：如果把 Server 组件当作**普通 prop** 传给 Client（不是 `children`），Next.js 不会识别它是 Server 组件 —— 它会被当作普通 JSX 重新在客户端渲染。

---

## 七、什么时候用哪个

| 场景 | 用哪种 |
|------|--------|
| 静态展示 | Server |
| 调接口读数据 | Server |
| 读数据库 / 文件 | Server |
| 调外部 SDK、用密钥 | Server |
| 表单交互（受控输入） | Client |
| 需要 `useState` / `useEffect` | Client |
| 需要 `onClick` / `onChange` | Client |
| 用了 `window` / `document` / `localStorage` | Client |
| 用了 React Context（Provider 模式） | Client |
| 用了浏览器侧第三方库（如某些图表库） | Client |

### 经验法则

> **默认全写 Server，**只在**需要交互**的**最小子树**切到 Client。
> Client 边界越小，发到浏览器的 JS 越少，首屏越快。

---

## 八、典型错误和正确写法

### 错误 1：把整个页面都标成 Client

```tsx
'use client'   // ❌ 整个页面都是 Client，SEO 优势没了
import { useState } from 'react'

export default function Page() {
  const [x, setX] = useState(0)
  return <div>{x}</div>
}
```

→ 改成 Server 页面 + Client 子组件。

### 错误 2：Server 组件里写 `onClick`

```tsx
// 没加 'use client'  ← Server Component
export default function Button() {
  return <button onClick={() => alert(1)}>x</button>   // ❌ 报错
}
```

→ 把这个 Button 文件加 `'use client'`，或者把它从 Server 文件里拆出去。

### 错误 3：Client 组件里 `await` 顶层数据

```tsx
'use client'
export default async function Page() {     // ❌ async + 'use client' 矛盾
  const data = await fetch(...)
}
```

→ Client 组件里 fetch 只能用 `useEffect` + `useState`，或者把 fetch 提到 Server 父组件。

### 错误 4：在 Client 组件里 import Server 组件

```tsx
'use client'
import ServerThing from './ServerThing'    // ❌

export default function ClientThing() {
  return <ServerThing />
}
```

→ 用 `children` 模式从父 Server 组件传进来。

---

## 九、几个常见的"必须 Client"的库

| 库 | 为什么必须 Client |
|----|------------------|
| `react-hook-form` | 大量 `useState` / 受控组件 |
| `framer-motion` | 动画需要在浏览器侧计算 |
| 图表库（echarts-for-react、recharts） | 用到 DOM 测量 |
| 任何用了 `window` / `localStorage` 的工具 | 浏览器 API |
| 任何 React Context Provider | Provider 必须 Client |

> 解决办法：把这些库包在一个**带 `'use client'` 的小组件**里，Server 父组件只 import 这个小组件，**不要把库 import 到 Server 组件**。

---

## 十、如何判断当前组件是 Server 还是 Client

- 文件顶部有 `'use client'` → Client
- 没写 → Server（默认）
- 在文件系统中：同一个目录下，`page.tsx` 是 Server，但 `Counter.tsx` 加了 `'use client'` 就是 Client

> 编译器会告诉你写错——比如在 Server Component 里写 `useState` 会立刻报错。

---

## 十一、对应 demo

- [02_server_client_components](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/nextjs-demo/02_server_client_components)
  - Server 页面 + Client 子组件组合
  - `children` 模式：把 Server 组件传给 Client 容器
  - 错误示例的对照（"use client 误用"）
