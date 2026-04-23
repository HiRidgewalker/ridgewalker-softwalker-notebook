## TypeScript需要标注和自行推断类型情况梳理


原则很简单：

- 能从上下文稳定、准确推断出来的，优先让 TypeScript 推断
- 推断不清楚、容易变宽、需要约束公共接口的时候，手写类型

### 更适合让 TypeScript 自动推断的情况

#### 1. 局部变量初始化时很明确

```typescript
const count = 0
const title = 'React'
const isOpen = false
````

这里写成 `const count: number = 0` 通常是多余的。

#### 2. 有明确初始值的简单返回值

```typescript
function add(a: number, b: number) {
  return a + b
}
```

返回值一般能推断成 `number`。

#### 3. 数组 map、filter、forEach 的回调参数

```typescript
navItems.map((item) => item.label)
```

`item` 会从 `navItems` 自动推断。

#### 4. React 组件的普通返回值

```typescript
function Header() {
  return <h1>Hello</h1>
}
```

返回值通常没必要手写。

#### 5. useState 能从初始值明确看出的场景

```typescript
const [count, setCount] = useState(0)
const [visible, setVisible] = useState(false)
```

#### 6. 对象字面量在局部使用，结构很直观时

```typescript
const user = {
  name: 'Tom',
  age: 18,
}
```

---

### 更适合手写类型的情况

#### 1. 函数参数

```typescript
function greet(name: string) {
  return `Hello ${name}`
}
```

参数几乎总是应该显式写，因为调用方要靠这个契约。

#### 2. 组件 props

```typescript
type ButtonProps = {
  label: string
  onClick: () => void
}
```

props 是组件接口，应该明确。

#### 3. useState 初始值不足以表达完整类型时

```typescript
const [user, setUser] = useState<User | null>(null)
const [list, setList] = useState<string[]>([])
```

如果只写 `useState([])`，常常推断得太弱或不对。

#### 4. 对外暴露的函数、工具函数、公共 API

```typescript
export function parseDate(value: string): Date | null {
  // ...
}
```

公开接口建议写明，稳定、清晰。

#### 5. 联合类型、泛型、约束需要你明确表达时

```typescript
function getValue<T>(input: T): T {
  return input
}
```

这种不是推断不出，而是你要定义规则。

#### 6. 对象要作为“结构契约”长期复用时

```typescript
type User = {
  id: number
  name: string
}
```

这时不应只靠对象字面量推断。

#### 7. null、空数组、空对象这类容易推断过窄或过弱的场景

```typescript
const [data, setData] = useState<Record<string, string>>({})
```

#### 8. 你想防止返回值未来被意外改坏时

```typescript
function buildOptions(): RequestInit {
  return { method: 'GET' }
}
```

给返回值类型是一种约束。

---

### React 项目里的实用判断

#### 优先推断：

- map 回调参数
    
- 组件内部局部变量
    
- 简单组件返回值
    
- 明确初始值的 useState
    

#### 优先显式写：

- props
    
- 事件类型
    
- useRef
    
- useState 的空值 / 空数组 / 复杂对象
    
- 自定义 Hook 返回值或参数
    
- 对外导出的工具函数
    

---

### 一个很实用的经验

如果你写的类型只是把推断结果机械重复一遍，通常不用写。  
如果这个类型是在「声明接口、限制边界、帮助调用方理解」，就应该写。

---

### 简单口诀

- 局部实现，能推断就推断
    
- 公共接口，尽量写明
    
- 空值场景，主动标注
    
- props / 参数 / state 结构，优先明确
    

---

## React + TypeScript 常见类型总结

### 1. 组件返回值类型

通常不手写，让 TS 自动推断：

```typescript
function MyComponent() {
  return <div>Hello</div>
}
```

如果需要手写：

```typescript
function MyComponent(): React.JSX.Element {
  return <div>Hello</div>
}
```

---

### 2. 组件本身的类型

```typescript
type ButtonProps = {
  text: string
}

const Button: React.FC<ButtonProps> = ({ text }) => {
  return <button>{text}</button>
}
```

更推荐：

```typescript
type ButtonProps = {
  text: string
}

function Button({ text }: ButtonProps) {
  return <button>{text}</button>
}
```

接收组件作为参数：

```typescript
type Props = {
  component: React.ComponentType<{ title: string }>
}
```

---

### 3. children 类型

```typescript
import type { ReactNode } from 'react'

type CardProps = {
  children: ReactNode
}
```



---

### 4. useRef 类型

```typescript
const inputRef = useRef<HTMLInputElement | null>(null)
const timerRef = useRef<number | null>(null)
const renderCountRef = useRef(0)
```

---

### 5. useState 的 setter 类型

useState 返回：

- 当前 state
    
- setState
    

其中 setState 的类型本质上是：

- `Dispatch<SetStateAction<T>>`
    

```typescript
const [count, setCount] = useState(0)
```

这里 `setCount` 的类型可以理解成：

```typescript
(value: number | ((prev: number) => number)) => void
```

也就是说它既能接具体值，也能接回调函数。

```typescript
setCount(10)
setCount((prev) => prev + 1)
```

如果手写 setter：

```typescript
import type { Dispatch, SetStateAction } from 'react'

type Props = {
  setCount: Dispatch<SetStateAction<number>>
}
```

---

### 6. 常见事件类型

```typescript
import type { ChangeEvent, FormEvent } from 'react'

function handleChange(event: ChangeEvent<HTMLInputElement>) {
  console.log(event.target.value)
}

function handleSubmit(event: FormEvent<HTMLFormElement>) {
  event.preventDefault()
}
```

---

### 7. 常见 props 结构类型

```typescript
import type { ReactNode } from 'react'

type UserCardProps = {
  name: string
  age: number
  children?: ReactNode
}
```

---

### 8. 最实用的一组

- 组件 props：自己写 `type Props = { ... }`
    
- children：`ReactNode`
    
- 组件返回值：通常不写
    
- DOM ref：`useRef<HTMLInputElement | null>(null)`
    
- state setter：`Dispatch<SetStateAction<T>>`
    
- 输入框事件：`ChangeEvent<HTMLInputElement>`
    
- 表单事件：`FormEvent<HTMLFormElement>`
    

---

### 9. 关键结论

```typescript
Dispatch<SetStateAction<T>>
```

等价理解为：

```typescript
(value: T | ((prev: T) => T)) => void
```

- 不需要额外区分传值还是传函数
    
- 类型系统已经帮你处理好了

## 常用的几个react对象
返回jsx类型：`React.JSX.Element`
组件本身： `React.FC<props 类型>`
children : `ReactNode`