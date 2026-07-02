// app/client-form/page.tsx
// 顶层 Server 页面，里面嵌一个 Client 表单组件
import { getTodos } from '../actions'
import ClientForm from './_components/ClientForm'

export default async function ClientFormPage() {
  const todos = await getTodos()

  return (
    <article>
      <h2>Client 表单 + useActionState</h2>
      <p>表单组件加了 <code>'use client'</code>，用 <code>useActionState</code> 拿到 pending 状态和 action 返回值。</p>

      <div className="card">
        <ClientForm />
      </div>

      <div className="card">
        <h3>当前列表</h3>
        {todos.length === 0 ? <p>暂无数据</p> : (
          <ul>{todos.map(t => <li key={t.id}>{t.title}</li>)}</ul>
        )}
      </div>
    </article>
  )
}
