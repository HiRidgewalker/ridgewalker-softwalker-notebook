/**
 * 02_react_hooks_types.ts
 *
 * 涵盖知识点：
 *  1. useState 在「初始值能表达完整类型」时直接推断
 *  2. useState 在「null / [] / 复杂对象」时必须手写
 *  3. setter 的本质类型 Dispatch<SetStateAction<T>>
 *  4. useReducer 的 state / action 必须手写
 *  5. useContext 的 Context value 类型
 *  6. useRef 在 DOM ref vs 可变值容器两种场景
 *  7. useImperativeHandle + forwardRef 的 handle 类型
 *  8. 泛型组件
 *  9. PropsWithChildren / ComponentProps / ComponentType / RefObject
 *
 * 注：本文件只展示「类型层面」的代码，不真正执行 React 运行时。
 *     在真实项目里这些代码要放进 React 函数组件里用。
 */

import {
  useState, useReducer, useContext, createContext,
  useRef, useImperativeHandle, forwardRef,
} from 'react'
import type {
  Dispatch, SetStateAction,
  PropsWithChildren, ComponentProps, ComponentType, ReactNode, RefObject,
} from 'react'

// ---------- 1. useState：初始值明确时让 TS 推断 ----------

const [count, setCount] = useState(0)              // number
const [visible, setVisible] = useState(false)      // boolean

setCount(10)
setCount((prev) => prev + 1)                       // 函数式更新

// ---------- 2. useState：null / [] / 复杂对象必须手写 ----------

type User = { id: number; name: string }

const [user, setUser] = useState<User | null>(null)        // ✅ 写明
const [list, setList] = useState<User[]>([])               // ✅ 写明
const [data, setData] = useState<Record<string, string>>({})

// 反例（仅作演示，会编译报错）：
// const [badList, setBadList] = useState([])              // 推断 never[]
// badList.push({ id: 1, name: 'Tom' })                   // ❌ never 上不存在 push

// ---------- 3. setter 类型 Dispatch<SetStateAction<T>> ----------

type CounterProps = {
  setCount: Dispatch<SetStateAction<number>>
}
// 等价于：
// type CounterProps = {
//   setCount: (value: number | ((prev: number) => number)) => void
// }

// ---------- 4. useReducer：state / action 必须手写 ----------

type State = { count: number; loading: boolean }
type Action =
  | { type: 'inc' }
  | { type: 'dec' }
  | { type: 'set'; payload: number }

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'inc': return { ...state, count: state.count + 1 }
    case 'dec': return { ...state, count: state.count - 1 }
    case 'set': return { ...state, count: action.payload }
    // 如果不写 Action 类型，case 'set' 里 action.payload 会被推成 any
  }
}

const [state, dispatch] = useReducer(reducer, { count: 0, loading: false })

// ---------- 5. useContext：Context value 类型 ----------

type Theme = 'light' | 'dark'
const ThemeCtx = createContext<Theme>('light')     // 默认值必须有，类型写明
const theme = useContext(ThemeCtx)                 // 类型自动是 Theme

// Context 默认值为 null 的写法
type Auth = { user: User | null }
const AuthCtx = createContext<Auth | null>(null)
const auth = useContext(AuthCtx)                   // Auth | null
// 使用处要守卫：if (!auth) throw new Error(...)

// ---------- 6. useRef：DOM ref vs 可变值容器 ----------

// DOM ref：惯例是 null，访问时 if 守卫
const inputRef = useRef<HTMLInputElement | null>(null)
// if (inputRef.current) inputRef.current.focus()

// 保存可变值（不挂 DOM）
const timerRef = useRef<number | null>(null)
const renderCountRef = useRef(0)

// 反例（仅作演示，旧代码常见）：
// const inputRef2 = useRef<HTMLInputElement>(null)   // null 不是 HTMLInputElement

// ---------- 7. useImperativeHandle + forwardRef ----------

type InputHandle = { focus: () => void; clear: () => void }

const Input = forwardRef<InputHandle, { placeholder?: string }>(
  ({ placeholder }, ref) => {
    const inner = useRef<HTMLInputElement | null>(null)
    useImperativeHandle(ref, () => ({
      focus: () => inner.current?.focus(),
      clear: () => { if (inner.current) inner.current.value = '' },
    }))
    // 真实 React 项目里这里 return <input ref={inner} ... />
    return null
  },
)

// ---------- 8. 泛型组件 ----------

type ListProps<T> = {
  items: T[]
  renderItem: (item: T) => ReactNode
  keyOf: (item: T) => string | number
}

function List<T>({ items, renderItem, keyOf }: ListProps<T>) {
  // return <ul>{items.map(it => <li key={keyOf(it)}>{renderItem(it)}</li>)}</ul>
  return null
}
// 使用：
// <List<User> items={users} renderItem={u => u.name} keyOf={u => u.id} />

// ---------- 9. 辅助类型 ----------

// 自动给 props 加 children?: ReactNode
type CardProps = PropsWithChildren<{ title: string }>

// 拿到原生标签的所有 props
type ButtonProps = ComponentProps<'button'>
// type ButtonProps = ComponentProps<'a'>
// type DivProps = ComponentProps<'div'>

// 接收任意组件作为参数
type WrapperProps = {
  component: ComponentType<{ title: string }>
}

// 父组件暴露给子组件的 ref 类型
type Handle = RefObject<{ focus: () => void }>