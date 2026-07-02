// 这个 Server 组件会作为 children 传给 ClientWrapper
// Next.js 会在服务端把它渲染好，再序列化塞进 children
async function getData() {
  return ['只能服务端看到的数据 A', '只能服务端看到的数据 B', '只能服务端看到的数据 C']
}

export default async function ServerPanel() {
  const items = await getData()
  return (
    <div>
      <span className="tag tag-server">Server Panel (passed as children)</span>
      <ul>
        {items.map((t, i) => <li key={i}>{t}</li>)}
      </ul>
    </div>
  )
}
