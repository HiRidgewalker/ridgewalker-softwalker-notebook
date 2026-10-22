// app/parallel/page.tsx
// 演示：Promise.all 并行请求
// 对比串行 await：多个请求"同时"发起，总耗时 = max，而不是 sum

import { fetchUsers, fetchPosts } from '../_lib/mockApi'

export default async function ParallelPage() {
  const start = Date.now()
  const [usersData, postsData] = await Promise.all([
    fetchUsers(),
    fetchPosts(),
  ])
  const elapsed = Date.now() - start

  return (
    <article>
      <h2>Promise.all 并行请求</h2>
      <p>用 <code>Promise.all</code> 同时发起多个 fetch。</p>
      <p>总耗时：<strong>{elapsed}ms</strong>（如果是串行会是两个 200ms 加起来）</p>
      <div className="card">
        <p>用户数：{usersData.users.length}</p>
        <p>文章数：{postsData.posts.length}</p>
      </div>
      <pre>{`// 串行（瀑布流）
const users = await fetchUsers()   // 200ms
const posts = await fetchPosts()   // 200ms → 总 400ms

// 并行
const [users, posts] = await Promise.all([
  fetchUsers(),
  fetchPosts(),
])  // 总 200ms`}</pre>
    </article>
  )
}
