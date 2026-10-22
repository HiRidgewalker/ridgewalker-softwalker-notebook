'use client'

import { useActionState } from 'react'
import { createTodoWithState, type ActionState } from '../../actions'

// Client 组件 + useActionState
// 可以拿到 isPending 状态 和 action 返回值
export default function ClientForm() {
  const [state, formAction, isPending] = useActionState<ActionState, FormData>(
    createTodoWithState,
    null
  )

  return (
    <form action={formAction}>
      <input name="title" placeholder="输入标题" disabled={isPending} />
      <button type="submit" disabled={isPending}>
        {isPending ? '提交中...' : '添加'}
      </button>
      {state && (
        <p className={state.ok ? 'success' : 'error'}>{state.message}</p>
      )}
    </form>
  )
}
