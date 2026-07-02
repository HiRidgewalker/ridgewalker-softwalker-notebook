// app/toggle/page.tsx
import { getTodos } from '../actions'
import Buttons from './_components/Buttons'

export default async function TogglePage() {
  const todos = await getTodos()

  return (
    <article>
      <h2>手动调用 Server Action</h2>
      <p>不是表单提交，而是按钮点击时通过 JS 调用 Server Action。</p>

      <div className="card">
        <Buttons />
      </div>

      <div className="card">
        <h3>当前列表</h3>
        {todos.length === 0 ? <p>暂无数据</p> : (
          <ul>
            {todos.map(t => (
              <li key={t.id}>{t.title}</li>
            ))}
          </ul>
        )}
      </div>
    </article>
  )
}
