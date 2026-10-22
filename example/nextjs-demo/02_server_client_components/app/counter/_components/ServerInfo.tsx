// Server Component：不需要 'use client'
// 在服务端渲染，渲染结果会被序列化发给 Client
async function fetchServerTime() {
  // 模拟一个服务端才能拿到的数据
  await new Promise(r => setTimeout(r, 100))
  return new Date().toISOString()
}

export default async function ServerInfo() {
  const time = await fetchServerTime()
  return (
    <div className="card">
      <span className="tag tag-server">Server Component</span>
      <p>服务端时间：<code>{time}</code></p>
      <p>↑ 这是在服务端渲染的（不打包到 JS bundle）</p>
    </div>
  )
}
