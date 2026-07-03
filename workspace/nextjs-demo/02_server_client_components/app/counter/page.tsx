// app/counter/page.tsx
// 顶层是 Server Component，子组件里既有 Server 也有 Client
import Counter from './_components/Counter'
import ServerInfo from './_components/ServerInfo'

export default function CounterPage() {
  return (
    <article>
      <h2>混合 Server / Client 组件</h2>
      <p>
        这个页面本身是 <strong>Server Component</strong>，但它 import 并使用了：
      </p>
      <ul>
        <li><code>ServerInfo</code> — 另一个 Server Component，直接 await 服务端时间</li>
        <li><code>Counter</code> — 一个 Client Component（有 'use client'）</li>
      </ul>
      <Counter initial={10} />
      <ServerInfo />
    </article>
  )
}
