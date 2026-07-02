// 列表页：app/blog/page.tsx → /blog

const posts = [
  { slug: 'hello-world', title: 'Hello World' },
  { slug: 'next-routing', title: 'Next.js 文件式路由' },
  { slug: 'rsc-intro', title: 'Server Components 入门' },
]

export default function BlogPage() {
  return (
    <article>
      <h2>博客列表</h2>
      <p>对应文件 <code>app/blog/page.tsx</code>，URL 是 <code>/blog</code>。</p>
      <ul>
        {posts.map(p => (
          <li key={p.slug}>
            <a href={`/blog/${p.slug}`}>{p.title}</a>
          </li>
        ))}
      </ul>
      <p>
        点击链接会进入 <code>app/blog/[slug]/page.tsx</code> 动态段。
      </p>
    </article>
  )
}
