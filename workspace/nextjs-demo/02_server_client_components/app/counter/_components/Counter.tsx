'use client'

import { useState } from 'react'

// 这是一个 Client Component
// 文件顶部 'use client' 标记整个文件为 Client
// 父页面是 Server，import 这个文件后这里会变成"客户端边界"
export default function Counter({ initial = 0 }: { initial?: number }) {
  const [count, setCount] = useState(initial)
  return (
    <div className="card">
      <span className="tag tag-client">Client Component</span>
      <p>当前计数：<strong>{count}</strong></p>
      <button onClick={() => setCount(c => c + 1)}>+1</button>{' '}
      <button onClick={() => setCount(c => c - 1)}>-1</button>{' '}
      <button onClick={() => setCount(initial)}>重置</button>
    </div>
  )
}
