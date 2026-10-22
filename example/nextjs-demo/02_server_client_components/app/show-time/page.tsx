// ⚠️ 错误示范：Server Component 用了会变的值，会触发 hydration 警告
// 把这个文件改成 'use client' 就能修复

export default function ShowTimePage() {
  return (
    <article>
      <h2>错误示范：服务端/客户端渲染不一致</h2>
      <div className="warn">
        <p>
          <strong>这个页面会触发 hydration 警告。</strong>
        </p>
        <p>当前渲染时间：<code>{new Date().toLocaleTimeString()}</code></p>
        <p>
          服务端渲染了一个时间戳，浏览器拿到 HTML 后又跑了一次，
          两个时间不一样 → React 报错"hydration failed"。
        </p>
        <p>
          修复办法：把组件改成 Client 组件（加 <code>'use client'</code>），
          或者在 <code>useEffect</code> 里再设置时间（避免 SSR 期间渲染）。
        </p>
      </div>
    </article>
  )
}
