# TypeScript 类型标注与 React 常用类型

> 适用场景：写 React + TS 项目时，判断**该让 TS 推断 vs 该手写类型**；
> 以及 React 项目里高频出现的类型写法（props、事件、Hooks、组件本身）。
>
> 配套可运行示例：[workspace/typescript-types/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/typescript-types)
> 由旧稿整理而来；旧稿目录已清理，当前以本文为准。

---

## 1. 核心原则

> **能稳定推断出来的，让 TS 推断；推断不出 / 是公共接口 / 是边界处的，主动写。**

判断写不写类型的本质就一句话：**这个类型是在描述「实现细节」还是在「声明接口」？**

- 实现细节 → 推断就够了
- 公共接口 / 边界 → 写明

---

## 2. 标注 vs 推断：决策表

| 场景 | 推荐做法 | 一句话理由 | 反例（推断会出什么错） |
|---|---|---|---|
| 局部变量带字面量初始值 | 推断 | `const x = 0` 已经是 `number` | — |
| 对象字面量只在本函数用 | 推断 | 结构直观，多写反而冗余 | — |
| 简单组件返回值 | 推断 | `return <div/>` 已经够明确 | — |
| 数组 `map/filter` 回调参数 | 推断 | 由数组元素类型自动推出 | — |
| `useState(0)` 这类初始值明确 | 推断 | 初始值已经能表达完整类型 | — |
| 函数 / 组件参数 | **手写** | 调用方靠这个契约 | 省略会变 `any`，调用方失去约束 |
| 组件 props | **手写** | 组件接口，必须明确 | 推断不出，老代码补类型很痛 |
| `useState(null)` / `useState([])` | **手写** | 推断会过窄或过宽 | `useState([])` 推出 `never[]`，没法 push |
| 对外导出的工具函数 / API | **手写** | 跨模块契约 | 实现改了返回值，调用方跟着坏 |
| 泛型参数 / 联合类型约束 | **手写** | 在定义规则，不只是描述 | — |
| 作为结构契约复用的对象 | **手写 `type User = {...}`** | 不应只靠字面量推断 | 多处对象字面量分散、形状漂移 |
| 空值 / 空集合 / 空对象 | **手写** | 推断极易过窄 | `useState({})` 推成 `{}`，加字段报错 |
| 想钉死返回值的函数 | **手写** | 防止未来被改坏 | 实现改动悄悄扩大返回值类型 |

---

## 3. React 项目里的实用判断

### 优先推断

- `map / filter / forEach` 回调参数
- 组件内部局部变量
- 简单组件的返回值
- 初始值明确的 `useState`
- 局部用的对象字面量

### 优先手写

- 组件 props
- 事件处理函数的事件对象（见第 4 节）
- `useRef` / `useImperativeHandle` 的 ref 类型
- `useState` 的空值 / 空数组 / 复杂对象
- 自定义 Hook 的参数和返回值
- `useReducer` 的 state / action 类型
- `useContext` 的 Context value 类型
- 对外导出的工具函数 / 公共组件

---

## 4. React 常用类型速查

### 4.1 组件返回值

```typescript
// 通常让 TS 推断
function Header() {
  return <h1>Hello</h1>
}

// 真要写：React.JSX.Element / JSX.Element / ReactElement 三者基本等价
function Header(): React.JSX.Element {
  return <h1>Hello</h1>
}
```

> **小坑**：`React.JSX.Element` 表示「一个完整的 JSX 元素」，不能表达 `null`/`string`/`number`。
> 如果组件可能返回 `null`（条件渲染），类型应该是 `React.ReactNode`，而不是 `React.JSX.Element`。

### 4.2 组件本身

```typescript
// 接收「任一组件」作为参数
import type { ComponentType, ReactNode } from 'react'

type Props = {
  component: ComponentType<{ title: string }>
  children?: ReactNode
}
```

> **现代社区共识**：不再推荐 `React.FC`。原因：
> 1. 隐式给 props 加 `children`，行为不直观
> 2. 泛型场景难写
> 3. 显式 `function Comp(props: Props)` 比 `const Comp: React.FC<Props>` 更清楚
>
> 直接 `function Button({ label }: ButtonProps) { return <button>{label}</button> }` 就好。

### 4.3 children 类型

```typescript
import type { ReactNode, ReactElement, PropsWithChildren } from 'react'

// 最常用：能塞任何可渲染内容（字符串、数字、元素、数组、null、Fragment…）
type CardProps = { children: ReactNode }

// 更严格：必须是单个 React 元素（不接受 string、number、数组）
type WrapperProps = { children: ReactElement }

// 自动给 props 加上 children?: ReactNode
function Card({ children }: PropsWithChildren<{ title: string }>) {
  return <section><h2>{title}</h2>{children}</section>
}
```

### 4.4 useRef

```typescript
import { useRef } from 'react'

// DOM ref：惯例是 null，方便后续 if 守卫
const inputRef = useRef<HTMLInputElement | null>(null)

// 保存可变值（不挂 DOM）
const timerRef = useRef<number | null>(null)
const renderCountRef = useRef(0)
```

> **注意**：`useRef<T | null>(null)` vs `useRef<T>(null!)`：
> 旧代码常见 `useRef<HTMLInputElement>(null)` —— TS 不报错但语义不对（`null` 不是 `HTMLInputElement`）。
> 现代写法是 `useRef<HTMLInputElement | null>(null)`，配合 `if (inputRef.current)` 守卫。

### 4.5 useState

```typescript
const [count, setCount] = useState(0)                 // 推断 number
const [visible, setVisible] = useState(false)         // 推断 boolean
const [user, setUser] = useState<User | null>(null)   // 必须写：null 不是 User
const [list, setList] = useState<string[]>([])        // 必须写：[] 推 never
const [data, setData] = useState<Record<string, string>>({})
```

setter 的本质类型：

```typescript
import type { Dispatch, SetStateAction } from 'react'

type Props = {
  setCount: Dispatch<SetStateAction<number>>
}

// 等价于：
type Props = {
  setCount: (value: number | ((prev: number) => number)) => void
}
```

也就是说 `setCount` 既能接值，也能接函数回调，不需要额外区分。

### 4.6 useReducer

```typescript
import { useReducer } from 'react'

type State = { count: number; loading: boolean }
type Action =
  | { type: 'inc' }
  | { type: 'set'; payload: number }

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'inc':   return { ...state, count: state.count + 1 }
    case 'set':   return { ...state, count: action.payload }
  }
}

const [state, dispatch] = useReducer(reducer, { count: 0, loading: false })
```

reducer 的 `state` / `action` 类型**几乎都该手写**，否则 switch 里 `action.type` 收窄不到具体变体。

### 4.7 useContext

```typescript
import { createContext, useContext } from 'react'

type Theme = 'light' | 'dark'
const ThemeCtx = createContext<Theme>('light')       // 默认值必须有

function useTheme() {
  return useContext(ThemeCtx)                        // 类型自动是 Theme
}
```

> **常见坑**：Context 默认值如果写 `null`，记得显式标 `Context<Theme | null>`，
> 使用处要 `if (!theme) throw ...` 或 `theme ?? 'light'`。

### 4.8 useImperativeHandle + ref

```typescript
import { forwardRef, useImperativeHandle, useRef } from 'react'
// React 19+ 可以不用 forwardRef，直接 ref 作为 prop

type Handle = { focus: () => void; clear: () => void }

const Input = forwardRef<Handle, { placeholder?: string }>(
  ({ placeholder }, ref) => {
    const innerRef = useRef<HTMLInputElement | null>(null)
    useImperativeHandle(ref, () => ({
      focus: () => innerRef.current?.focus(),
      clear: () => { if (innerRef.current) innerRef.current.value = '' },
    }))
    return <input ref={innerRef} placeholder={placeholder} />
  }
)
```

### 4.9 事件类型

```typescript
import type {
  ChangeEvent, FormEvent, MouseEvent, KeyboardEvent,
  FocusEvent, PointerEvent, DragEvent, WheelEvent,
  ClipboardEvent,
} from 'react'
```

| 事件 | 类型 | 触发元素例子 |
|---|---|---|
| 输入框 change | `ChangeEvent<HTMLInputElement>` | `<input>` |
| 文本域 change | `ChangeEvent<HTMLTextAreaElement>` | `<textarea>` |
| select change | `ChangeEvent<HTMLSelectElement>` | `<select>` |
| 表单 submit | `FormEvent<HTMLFormElement>` | `<form onSubmit>` |
| 按钮点击 | `MouseEvent<HTMLButtonElement>` | `<button onClick>` |
| 通用点击 | `MouseEvent<HTMLElement>` | 自定义组件 onClick |
| 键盘 | `KeyboardEvent<HTMLInputElement>` | `onKeyDown` |
| 聚焦 / 失焦 | `FocusEvent<HTMLInputElement>` | `onFocus` / `onBlur` |
| 鼠标按下 | `PointerEvent<HTMLDivElement>` | 拖拽场景 |
| 拖拽 | `DragEvent<HTMLDivElement>` | `onDragStart` 等 |
| 滚轮 | `WheelEvent<HTMLDivElement>` | `onWheel` |
| 剪贴板 | `ClipboardEvent<HTMLInputElement>` | 复制粘贴 |

示例：

```typescript
function Form() {
  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.value)
  }
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
  }
  const handleKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSubmit(/* ... */)
  }
  return <form onSubmit={handleSubmit}><input onChange={handleChange} onKeyDown={handleKey} /></form>
}
```

### 4.10 泛型组件

```typescript
type ListProps<T> = {
  items: T[]
  renderItem: (item: T) => ReactNode
  keyOf: (item: T) => string | number
}

function List<T>({ items, renderItem, keyOf }: ListProps<T>) {
  return <ul>{items.map(it => <li key={keyOf(it)}>{renderItem(it)}</li>)}</ul>
}

// 使用时显式指定
<List<User>
  items={users}
  renderItem={u => u.name}
  keyOf={u => u.id}
/>
```

### 4.11 常用辅助类型

```typescript
import type { PropsWithChildren, ComponentProps, ElementType, RefObject } from 'react'

// 自动加 children?: ReactNode
type Props = PropsWithChildren<{ title: string }>

// 拿到某个原生标签的所有 props
type ButtonProps = ComponentProps<'button'>

// 通用「任意元素 + 它的 props」
function Poly<T extends ElementType>({ as, ...rest }: { as: T } & ComponentProps<T>) {
  const Comp = as
  return <Comp {...rest} />
}

// 父组件暴露给子组件的 ref
type Handle = RefObject<{ focus: () => void }>
```

---

## 5. 现代写法小贴士

### 5.1 `satisfies`：校验但不丢失具体类型

```typescript
type Config = { endpoint: string; timeout?: number }

// ❌ 标注会 widen
const cfg: Config = { endpoint: '/api', timeout: 5000 }
// cfg.timeout 的类型是 number | undefined

// ✅ satisfies：确认符合 Config，但保留字面量类型
const cfg = {
  endpoint: '/api',
  timeout: 5000,
} satisfies Config
// cfg.timeout 的类型仍然是 5000（字面量类型）
```

### 5.2 `as const`：把对象/数组收成 readonly 字面量

```typescript
const NAV = [
  { key: 'home', path: '/' },
  { key: 'about', path: '/about' },
] as const

type NavKey = typeof NAV[number]['key']   // 'home' | 'about'
```

### 5.3 React 19 的 ref-as-prop

```typescript
// React 19 之前
const Input = forwardRef<HTMLInputElement, { placeholder?: string }>(
  ({ placeholder }, ref) => <input ref={ref} placeholder={placeholder} />
)

// React 19+：ref 就是普通 prop
function Input({ placeholder, ref }: { placeholder?: string; ref?: React.Ref<HTMLInputElement> }) {
  return <input ref={ref} placeholder={placeholder} />
}
```

---

## 6. 常见坑

### 6.1 空数组 / 空对象推断过窄

```typescript
const [list, setList] = useState([])             // never[]  ❌ 推不出
const [data, setData] = useState({})             // {}       ❌ 推不出
const [user, setUser] = useState(null)           // null     ❌ 推不出

// 必须显式：
const [list, setList] = useState<User[]>([])
const [data, setData] = useState<Record<string, string>>({})
const [user, setUser] = useState<User | null>(null)
```

### 6.2 联合类型被 widen

```typescript
type Status = 'idle' | 'loading' | 'success'

// ❌ TS 推成 string
const status = condition ? 'idle' : 'loading'

// ✅ 用 as const 或 satisfies
const status = (condition ? 'idle' : 'loading') as const
const status = (condition ? 'idle' : 'loading') satisfies Status
```

### 6.3 `as` 断言滥用

`as` 是**绕过**类型检查，不是修复类型。常见误用：

```typescript
// ❌ 用 as 掩盖「为什么类型不对」
const user = JSON.parse(json) as User

// ✅ 先 unknown，再校验
const user: User = JSON.parse(json)   // 配 zod / valibot / 手写守卫
// 或
const user = JSON.parse(json) as unknown as User   // 至少显式表达「我清楚这有风险」
```

### 6.4 `@types/react` 与 `react` 版本不对齐

`@types/react`、`@types/react-dom`、`@types/node` 三个包的版本必须和 `react`、`react-dom` 的版本同步升降。否则会出现「找不到 JSX.Element / 找不到 useRef 类型」之类的奇怪报错。

### 6.5 事件对象与原生 DOM 事件混用

`React.MouseEvent<HTMLButtonElement>` 和原生 `MouseEvent` **不是同一个东西**，前者多了 `currentTarget` / SyntheticEvent 那套。要给原生 API（如 `addEventListener` 回调）传值时记得 `e.nativeEvent`。

---

## 7. 一句话口诀

- 局部实现，能推断就推断
- 公共接口，尽量写明
- 空值场景，主动标注
- props / 参数 / state 结构，优先明确
- 「实现」靠推断，「契约」靠手写

---

## 8. 配套 demo

- [workspace/typescript-types/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/typescript-types)
  - 推断 vs 标注对比
  - React 常用类型全集示例
  - Hooks（useState / useReducer / useContext / useRef）类型实战
  - 常见坑（空数组推断、as 断言滥用、satisfies 修复 widen）的最小复现
