'use client'

import { useTransition } from 'react'
import { deleteTodo, createTodo } from '../../actions'

// 演示：在 Client 组件里手动调用 Server Action
// useTransition 提供 isPending（和 useTransition 的 transition 不一样，但 isPending 一样可用）
export default function ToggleButtons() {
  const [isPending, startTransition] = useTransition()

  function handleAdd() {
    const title = window.prompt('新文章标题？')
    if (!title) return
    const fd = new FormData()
    fd.append('title', title)
    startTransition(async () => {
      await createTodo(fd)
    })
  }

  function handleDelete(id: number) {
    startTransition(async () => {
      await deleteTodo(id)
    })
  }

  return (
    <div>
      <button onClick={handleAdd} disabled={isPending}>
        {isPending ? '处理中...' : '新增（弹窗输入）'}
      </button>
      <p style={{ color: '#666', fontSize: 13 }}>
        ↑ 这次没用 form，是手动从 Client 组件调用 Server Action
      </p>
    </div>
  )
}
