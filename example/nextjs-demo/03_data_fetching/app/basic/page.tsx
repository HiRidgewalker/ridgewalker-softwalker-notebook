// app/basic/page.tsx
// 演示：Server Component 顶层直接 await fetch
// 默认是 force-cache：第一次请求后结果被缓存

import { fetchUsers } from '../_lib/mockApi'

// 重要：默认静态渲染，因为 fetch 用了 force-cache
// 多次刷新页面会看到 timestamp 不变（命中缓存）
export default async function BasicPage() {
  const data = await fetchUsers()

  return (
    <article>
      <h2>基础 Server fetch（默认 force-cache）</h2>
      <p>这是 Server Component，<code>await</code> 发生在服务端。</p>
      <div className="card">
        <p>请求时间戳：<code>{data.timestamp}</code></p>
        <p>用户列表：</p>
        <ul>
          {data.users.map(u => <li key={u.id}>{u.name}</li>)}
        </ul>
      </div>
      <p>↑ <strong>多次刷新这个页面，时间戳不会变</strong>，因为 Next.js 缓存了 fetch 结果。</p>
    </article>
  )
}
