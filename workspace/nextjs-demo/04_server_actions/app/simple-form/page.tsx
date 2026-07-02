// app/simple-form/page.tsx
// 演示：纯 Server 页面 + 原生 <form action={serverAction}>
// 不需要写一行 JS 也能工作（渐进增强）

import { createTodo, getTodos, deleteTodo } from '../actions'

export default async function SimpleFormPage() {
  const todos = await getTodos()

  return (
    <article>
      <h2>原生 form + Server Action</h2>
      <p>整个页面是 Server Component，<code>&lt;form&gt;</code> 直接绑定 <code>createTodo</code>。</p>
      <p>即使禁用浏览器 JS，表单也能提交（渐进增强）。</p>

      <div className="card">
        <form action={createTodo}>
          <input name="title" placeholder="输入标题" />
          <button type="submit">添加</button>
        </form>
      </div>

      <div className="card">
        <h3>当前列表</h3>
        {todos.length === 0 ? (
          <p>暂无数据</p>
        ) : (
          <ul>
            {todos.map(t => (
              <li key={t.id} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ flex: 1 }}>{t.title}</span>
                {/* 通过 .bind 把 id 注入 action */}
                <form action={deleteTodo.bind(null, t.id)}>
                  <button type="submit">删除</button>
                </form>
              </li>
            ))}
          </ul>
        )}
      </div>
    </article>
  )
}
