// 静态段：app/about/page.tsx → /about

export default function AboutPage() {
  return (
    <article>
      <h2>关于页</h2>
      <p>
        对应文件 <code>app/about/page.tsx</code>，URL 是 <code>/about</code>。
        完全静态，会在 <code>next build</code> 时生成。
      </p>
    </article>
  )
}
