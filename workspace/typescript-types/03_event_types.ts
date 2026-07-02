/**
 * 03_event_types.ts
 *
 * 涵盖知识点：
 *  - React 事件类型全集（ChangeEvent / FormEvent / MouseEvent / KeyboardEvent /
 *    FocusEvent / PointerEvent / DragEvent / WheelEvent / ClipboardEvent）
 *  - 每个类型携带的元素泛型（如 ChangeEvent<HTMLInputElement>）
 *  - event.target / event.currentTarget 的常见取值
 *  - event.nativeEvent 与原生 DOM 事件的区别
 *
 * 注：本文件只展示「类型签名」，不真正执行 React 组件。
 *     真实使用要把这些 handler 放在函数组件里。
 */

import type {
  ChangeEvent,
  FormEvent,
  MouseEvent,
  KeyboardEvent,
  FocusEvent,
  PointerEvent,
  DragEvent,
  WheelEvent,
  ClipboardEvent,
} from 'react'

// ---------- 1. ChangeEvent：输入框 / 文本域 / select ----------

function onInputChange(e: ChangeEvent<HTMLInputElement>) {
  console.log(e.target.value)                 // string
}

function onTextareaChange(e: ChangeEvent<HTMLTextAreaElement>) {
  console.log(e.target.value)
}

function onSelectChange(e: ChangeEvent<HTMLSelectElement>) {
  console.log(e.target.value)
}

// ---------- 2. FormEvent：表单提交 ----------

function onFormSubmit(e: FormEvent<HTMLFormElement>) {
  e.preventDefault()                          // 表单提交必须 preventDefault
}

// ---------- 3. MouseEvent：点击 / 双击 / 鼠标进入离开 ----------

function onButtonClick(e: MouseEvent<HTMLButtonElement>) {
  console.log(e.clientX, e.clientY)
}

function onDivClick(e: MouseEvent<HTMLDivElement>) {
  console.log(e.currentTarget)                // 类型是 HTMLDivElement
}

function onGenericClick(e: MouseEvent<HTMLElement>) {
  // 自定义组件 onClick 转发到任意元素时
  console.log(e.currentTarget.dataset)
}

// ---------- 4. KeyboardEvent：键盘 ----------

function onKeyDown(e: KeyboardEvent<HTMLInputElement>) {
  if (e.key === 'Enter') {
    // 触发提交
  }
  if (e.ctrlKey || e.metaKey) {
    // ⌘/Ctrl 组合键
  }
}

function onKeyUp(e: KeyboardEvent<HTMLTextAreaElement>) {
  console.log(e.key, e.code)
}

// ---------- 5. FocusEvent：聚焦 / 失焦 ----------

function onInputFocus(e: FocusEvent<HTMLInputElement>) {
  console.log(e.target.name)
}

function onInputBlur(e: FocusEvent<HTMLInputElement>) {
  // 校验 / 自动保存
}

// ---------- 6. PointerEvent：鼠标按下 / 移动 / 抬起 ----------

function onPointerDown(e: PointerEvent<HTMLDivElement>) {
  console.log(e.pointerId, e.pressure)
}

function onPointerMove(e: PointerEvent<HTMLCanvasElement>) {
  // 拖拽 / 绘图
}

// ---------- 7. DragEvent：拖拽 ----------

function onDragStart(e: DragEvent<HTMLDivElement>) {
  e.dataTransfer.setData('text/plain', e.currentTarget.id)
}

function onDrop(e: DragEvent<HTMLDivElement>) {
  e.preventDefault()
  const data = e.dataTransfer.getData('text/plain')
  console.log(data)
}

// ---------- 8. WheelEvent：滚轮 ----------

function onWheel(e: WheelEvent<HTMLDivElement>) {
  console.log(e.deltaY)
}

// ---------- 9. ClipboardEvent：复制 / 粘贴 / 剪切 ----------

function onPaste(e: ClipboardEvent<HTMLInputElement>) {
  const text = e.clipboardData.getData('text/plain')
  console.log(text)
}

// ---------- 10. SyntheticEvent 与原生 DOM 事件的区别 ----------

function withNative(e: MouseEvent<HTMLButtonElement>) {
  // e 的类型是 React 合成事件，带 currentTarget 等
  console.log(e.currentTarget)

  // 如果要给原生 API 用：
  document.addEventListener('click', (nativeEvent) => {
    // nativeEvent 是原生 MouseEvent，不是 React.MouseEvent
    console.log(nativeEvent instanceof MouseEvent)  // true
  })

  // 把 React 事件传给原生 API 时，取 nativeEvent
  // doSomethingWithNative(e.nativeEvent)
}