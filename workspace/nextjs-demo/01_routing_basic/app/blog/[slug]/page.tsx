// 动态段：app/blog/[slug]/page.tsx → /blog/:slug
// 演示：动态段 + 通过 params 读取 URL 参数

type Props = {
  params: { slug: string }
}

export default async function BlogPostPage({ params }: Props) {
  // 注意：在 Server Component 里 params 是同步可用的（Next.js 14）
  // Next.js 15+ 改为 Promise，需要 await
  const { slug } = params

  return (
    <article>
      <h2>博客详情</h2>
      <p>
        对应文件 <code>app/blog/[slug]/page.tsx</code>，URL 是 <code>/blog/{slug}</code>。
      </p>
      <p>
        当前 slug 参数：<code>{slug}</code>
      </p>
      <p>↑ 这是从 <code>params.slug</code> 读出来的。</p>
    </article>
  )
}
