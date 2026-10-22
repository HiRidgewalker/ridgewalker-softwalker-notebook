/**
 * 04_common_pitfalls.ts
 *
 * 涵盖知识点：
 *  1. 空数组 / 空对象 / null 推断过窄 → 必须显式标注
 *  2. 联合类型被 widen → 用 as const / satisfies 修复
 *  3. as 类型断言滥用 → 用 unknown 中转
 *  4. satisfies：校验形状但不丢失字面量类型
 *  5. @types/react 与 react 版本不对齐（README 里说明）
 */

import { useState } from 'react'

// ---------- 1. 空值场景必须显式 ----------

// ❌ 反例：推断成 never[]
const badList = useState([])
// badList[0].push(1)                          // 报错：never 上不存在 push

// ✅ 正确写法
const [users, setUsers] = useState<{ id: number }[]>([])

// ❌ 反例：推断成 {}
const badData = useState({})
// badData[0].foo = 1                          // 报错：{} 上不存在 foo

// ✅ 正确写法
const [data, setData] = useState<Record<string, string>>({})

// ❌ 反例：推断成 null
const badUser = useState(null)
// badUser[0].name                             // 报错：null 上不存在 name

// ✅ 正确写法
type User = { id: number; name: string }
const [user, setUser] = useState<User | null>(null)


// ---------- 2. 联合类型 widen ----------

type Status = 'idle' | 'loading' | 'success'

const condition = true

// ❌ TS 推成 string
const badStatus = condition ? 'idle' : 'loading'

// ✅ 修复 1：as const
const goodStatus1 = (condition ? 'idle' : 'loading') as const
// typeof goodStatus1 = 'idle' | 'loading'（具体字面量）

// ✅ 修复 2：satisfies 校验形状 + 保留字面量类型
const config = {
  endpoint: '/api',
  timeout: 5000,
} satisfies { endpoint: string; timeout?: number }

// config.endpoint: string（没 widen）
// config.timeout: 5000（字面量类型，不是 number）

// ---------- 3. as 类型断言的边界 ----------

// ❌ 反例：用 as 掩盖「为什么类型不对」
const unsafeUser = JSON.parse('{"name":"Tom"}') as { name: string }
// 万一 JSON 字段不匹配，运行时炸

// ✅ 正确：unknown 中转 + 校验
const raw: unknown = JSON.parse('{"name":"Tom"}')
function isUser(x: unknown): x is { name: string } {
  return typeof x === 'object' && x !== null && 'name' in x && typeof (x as { name: unknown }).name === 'string'
}
if (isUser(raw)) {
  console.log(raw.name)                       // 这里 raw 被收窄到 { name: string }
}

// 或者用 unknown as 的双步表达「我知道这里有风险」
const anotherUser = JSON.parse('{}') as unknown as { name: string }


// ---------- 4. satisfies 的实战用法 ----------

const routes = [
  { path: '/', auth: false },
  { path: '/admin', auth: true },
] as const
// typeof routes[number] = { readonly path: '/' | '/admin'; readonly auth: false | true }

// 用 satisfies 校验「形状是 Route[]」，但保留字面量类型
type Route = { path: string; auth: boolean }

const nav = [
  { path: '/', auth: false },
  { path: '/admin', auth: true },
] satisfies Route[]

// nav[0].path: '/' （字面量，没 widen 成 string）


// ---------- 5. useState 的 setter 函数式更新 ----------

const [count, setCount] = useState(0)

setCount(10)
setCount((prev) => prev + 1)                   // 函数式更新，回调收到 prev

// 反例：写一个外部函数接收 setState，类型不写
// function reset(setter) { setter(0) }        // ❌ setter: any

// 正确：手写 Dispatch<SetStateAction<T>>
import type { Dispatch, SetStateAction } from 'react'

function reset(setter: Dispatch<SetStateAction<number>>) {
  setter(0)
  setter((prev) => prev + 1)
}