/**
 * 01_inference_vs_annotation.ts
 *
 * 涵盖知识点：
 *  1. 能让 TS 推断的场景（局部变量、map 回调、简单返回值）
 *  2. 必须手写的场景（函数参数、props、空值、对外 API、泛型）
 *  3. 空值 / 空集合 / 空对象 推断过窄/过宽的反例
 *  4. type User = {...}  作为结构契约复用
 *
 * 阅读方式：把鼠标悬停到每个变量上，看 TS 推断的类型；故意写错的行会有红色波浪线。
 */

// ====== 1. 适合让 TS 推断 ======

const count = 0                  // 推断为 number
const title = 'React'            // 推断为 string
const isOpen = false             // 推断为 boolean

const navItems = [
  { label: 'Home', path: '/' },
  { label: 'About', path: '/about' },
]
const labels = navItems.map((item) => item.label)
// item 自动从 navItems 元素类型推断，无需标注

function add(a: number, b: number) {
  return a + b                   // 返回值推断为 number，无需手写
}

// ====== 2. 必须手写：函数参数 / 公共接口 ======

function greet(name: string): string {
  return `Hello ${name}`
}
// 参数必须写：调用方靠这个契约。

export function parseDate(value: string): Date | null {
  // 导出 API：返回类型写明，防止实现改了返回值悄悄影响调用方
  if (!value) return null
  return new Date(value)
}

function getValue<T>(input: T): T {
  return input
}
// 泛型是「在定义规则」，不是推断。

// ====== 3. 必须手写：空值 / 空集合 / 空对象 ======

// ❌ 反例：TS 推断成 never[]，后续 .push() 会报错
const badList: never[] = []

// ❌ 反例：TS 推断成 {}，加任意字段都会报错
const badData: {} = {}

// ✅ 正确写法
type User = { id: number; name: string }
const users: User[] = []
const data: Record<string, string> = {}
const current: User | null = null

// ====== 4. 作为结构契约复用的对象 ======

type Order = {
  id: string
  total: number
  items: { sku: string; qty: number }[]
}

// 不应写成 const order = { id: ..., total: ..., items: ... }
// 后续多处引用 Order 时，形状漂移没人拦得住。
const order: Order = {
  id: 'o-001',
  total: 99.5,
  items: [{ sku: 'sku-1', qty: 2 }],
}

// ====== 5. 钉死返回值 ======

function buildOptions(): RequestInit {
  return { method: 'GET' }
}
// 后续如果改成返回 { method: string; ... }，调用方立刻看到差异