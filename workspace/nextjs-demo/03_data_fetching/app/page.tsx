export default function Home() {
  return (
    <article>
      <h2>数据获取 demo</h2>
      <p>
        这个 demo 演示 Next.js Server Component 中数据获取的几种方式。
        所有数据都在<strong>服务端</strong>获取，浏览器拿到的 HTML 里已经包含结果。
      </p>
      <ul>
        <li><code>/basic</code> — 最基本的 Server fetch（默认 force-cache）</li>
        <li><code>/parallel</code> — <code>Promise.all</code> 并行请求，消除瀑布流</li>
        <li><code>/revalidate</code> — ISR 风格的 <code>next.revalidate</code></li>
        <li><code>/no-store</code> — <code>cache: 'no-store'</code> 每次都重取</li>
      </ul>
    </article>
  )
}
