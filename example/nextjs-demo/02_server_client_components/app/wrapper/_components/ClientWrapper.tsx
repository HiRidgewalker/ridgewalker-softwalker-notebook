'use client'

import { useState } from 'react'

// Client 容器：用 children 接收 Server 组件
// 这是合法的：Server 组件渲染完成后会被序列化，作为 children 传给 Client
export default function ClientWrapper({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(true)
  return (
    <div className="card">
      <span className="tag tag-client">Client Wrapper</span>
      <p>
        <button onClick={() => setOpen(o => !o)}>{open ? '隐藏' : '显示'}</button>
      </p>
      {open ? children : <p>（已隐藏）</p>}
    </div>
  )
}
