// app/no-store/page.tsx
// 演示：cache: 'no-store' 禁用缓存
// 适合：用户登录后数据、实时行情、聊天消息

import { fetchUsers } from '../_lib/mockApi'

// 强制动态渲染（每次都重取）
export const dynamic = 'force-dynamic'

export default async function NoStorePage() {
  const data = await fetchUsers({ noStore: true })

  return (
    <article>
      <h2>不缓存（cache: 'no-store'）</h2>
      <p>文件顶部加 <code>export const dynamic = 'force-dynamic'</code>。</p>
      <p>每次请求都会重新拉数据 → 路由变成<strong>动态渲染</strong>。</p>
      <div className="card">
        <p>当前时间戳：<code>{data.timestamp}</code></p>
        <p>请求计数：<code>{data.requestCount}</code></p>
      </div>
      <p>↑ <strong>每次刷新时间戳都会变</strong>，证明没有被缓存。</p>
    </article>
  )
}
