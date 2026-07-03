export default function Home() {
  return (
    <article>
      <h2>Server Actions demo</h2>
      <p>Server Action 是运行在服务端的异步函数，可以直接当作 <code>&lt;form action&gt;</code> 用。</p>
      <ul>
        <li><code>/simple-form</code> — Server 页面 + 原生 form，不需要写 JS 也能提交</li>
        <li><code>/client-form</code> — Client 组件 + <code>useActionState</code> 处理 pending / 返回值</li>
        <li><code>/toggle</code> — 点击按钮调用 Server Action（带参数）</li>
      </ul>
    </article>
  )
}
