// 根路由：app/page.tsx → /
// 没有 'use client'，是 Server Component

export default function HomePage() {
  return (
    <article>
      <h2>文件式路由根页</h2>
      <p>
        这个页面对应文件 <code>app/page.tsx</code>，URL 是 <code>/</code>。
      </p>
      <p>整段头部 <code>app/layout.tsx</code> 会包裹这里的内容。</p>
    </article>
  )
}
