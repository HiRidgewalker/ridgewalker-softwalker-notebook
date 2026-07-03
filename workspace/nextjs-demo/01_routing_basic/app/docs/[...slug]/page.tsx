// Catch-all 段：app/docs/[...slug]/page.tsx
// 匹配：/docs/a、/docs/a/b、/docs/a/b/c ……
// 不匹配：/docs（会 404）

type Props = {
  params: { slug: string[] }
}

export default async function DocsPage({ params }: Props) {
  const path = params.slug?.join('/') ?? ''

  return (
    <article>
      <h2>文档</h2>
      <p>
        对应文件 <code>app/docs/[...slug]/page.tsx</code>，使用 <strong>Catch-all</strong> 段。
      </p>
      <p>
        当前路径：<code>/docs/{path}</code>
      </p>
      <p>
        <code>params.slug</code> = <code>{JSON.stringify(params.slug)}</code>
      </p>
      <p>
        访问 <code>/docs</code> 会 404（Catch-all 必须有路径段）。改用 <code>[[...slug]]</code>{' '}
        才能让 <code>/docs</code> 也命中。
      </p>
    </article>
  )
}
