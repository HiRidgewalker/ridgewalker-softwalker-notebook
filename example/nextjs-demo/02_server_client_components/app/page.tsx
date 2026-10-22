// 入口页：纯 Server Component

export default function Home() {
  return (
    <article>
      <h2>Server vs Client 组件</h2>
      <p>
        Next.js 13+ 引入 React Server Components (RSC) 后，所有组件默认都是 <strong>Server Component</strong>。
        需要交互、事件、hooks 时才在文件顶部加 <code>'use client'</code>。
      </p>
      <ul>
        <li><code>/counter</code> — 顶层 Server 页面 + Client 子组件（最常见正确模式）</li>
        <li><code>/wrapper</code> — Client 组件作为容器，<strong>通过 children 接收 Server 组件</strong></li>
        <li><code>/show-time</code> — 错误示范（会触发 hydration 警告）</li>
      </ul>
    </article>
  )
}
