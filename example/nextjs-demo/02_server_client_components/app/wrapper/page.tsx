// app/wrapper/page.tsx
// 演示：把 Server 组件作为 children 传给 Client 容器
import ClientWrapper from './_components/ClientWrapper'
import ServerPanel from './_components/ServerPanel'

export default function WrapperPage() {
  return (
    <article>
      <h2>children 模式：Client 容器 + Server 子树</h2>
      <p>
        <code>ClientWrapper</code> 是带 <code>'use client'</code> 的容器，
        它通过 <code>children</code> prop 接收一个 <code>ServerPanel</code>。
      </p>
      <p>Next.js 会在服务端把 ServerPanel 渲染好，再把结果序列化传给 ClientWrapper。</p>
      <ClientWrapper>
        <ServerPanel />
      </ClientWrapper>
    </article>
  )
}
