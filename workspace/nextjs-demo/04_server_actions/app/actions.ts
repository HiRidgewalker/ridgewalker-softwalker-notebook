'use server'

// 整个文件都是 Server Actions
// 这些函数运行在服务端，可以直接 await fetch、读数据库
// 通过 <form action={fn}> 或客户端调用来触发

import { revalidatePath } from 'next/cache'

// 模拟一个内存数据源
let db: { id: number; title: string }[] = [
  { id: 1, title: '初始文章 1' },
  { id: 2, title: '初始文章 2' },
]

export async function getTodos() {
  await new Promise(r => setTimeout(r, 100))
  return db
}

// 接收 FormData：最常见的"提交表单"模式
export async function createTodo(formData: FormData) {
  const title = formData.get('title')?.toString().trim()
  if (!title) {
    return { ok: false, message: '标题不能为空' } as const
  }
  await new Promise(r => setTimeout(r, 200))  // 模拟写入
  db.push({ id: Date.now(), title })
  revalidatePath('/simple-form')
  revalidatePath('/toggle')
  return { ok: true, message: `已添加：${title}` } as const
}

export async function deleteTodo(id: number) {
  await new Promise(r => setTimeout(r, 100))
  db = db.filter(t => t.id !== id)
  revalidatePath('/simple-form')
  revalidatePath('/toggle')
}

// 接收旧 state + FormData：用于 useActionState
export type ActionState = { ok: boolean; message: string } | null

export async function createTodoWithState(
  prevState: ActionState,
  formData: FormData
): Promise<ActionState> {
  const title = formData.get('title')?.toString().trim()
  if (!title) {
    return { ok: false, message: '标题不能为空' }
  }
  await new Promise(r => setTimeout(r, 400))
  db.push({ id: Date.now(), title })
  revalidatePath('/client-form')
  revalidatePath('/simple-form')
  return { ok: true, message: `已添加：${title}` }
}
