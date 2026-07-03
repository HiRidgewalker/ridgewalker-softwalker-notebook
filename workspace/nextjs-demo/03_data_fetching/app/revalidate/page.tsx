// app/revalidate/page.tsx
// 演示：ISR 风格的 revalidate
// 缓存 30 秒，过期后下次请求触发后台重新生成

import { fetchUsers } from '../_lib/mockApi'

// 这一行的作用：让这个路由在 30 秒后过期
export const revalidate = 30

export default async function RevalidatePage() {
  const data = await fetchUsers()

  return (
    <article>
      <h2>ISR：定时重新生成（revalidate = 30s）</h2>
      <p>在文件顶部加 <code>export const revalidate = 30</code>。</p>
      <p>30 秒内：返回缓存的 HTML（多次刷新，时间戳不变）。</p>
      <p>30 秒后：先返回旧 HTML，<strong>后台</strong>异步重新生成，下次请求拿到新的。</p>
      <div className="card">
        <p>当前返回的时间戳：<code>{data.timestamp}</code></p>
      </div>
      <p>试试 30 秒后再刷新一次，看 timestamp 是否更新。</p>
    </article>
  )
}
