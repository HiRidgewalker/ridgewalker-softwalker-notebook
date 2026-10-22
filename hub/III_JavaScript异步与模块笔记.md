# 03_JavaScript 异步与模块笔记 — 回调 / Promise / ES Module

> 本笔记为以下原文档的提炼合并 + 补全版：
> - 旧稿（回调函数参数注入机制）
> - 旧稿（ES Module + 类的访问控制）
>
> 旧稿目录已清理，当前以本文为准。

---

## 一、回调函数

### 核心结论：参数来自「调用者」，不是「自动注入」

> 你看到的「自动注入参数」，本质上都是：
> - 你把函数交给别人
> - 别人在合适时机调用这个函数
> - 调用时顺手传入参数

### 最普通的例子

```javascript
function run(callback) {
  callback('hello')          // ← 调用者主动传参
}

run(function (value) {
  console.log(value)         // 'hello'
})
```

回调函数：

- 有没有参数
- 参数是什么
- **全部取决于「谁调用它时传了什么」**

### React 事件中的 `event`

```jsx
<button onClick={(event) => console.log(event)}>click</button>
```

React 内部近似执行：

```javascript
const handler = (event) => console.log(event)
// 点击发生时：
handler(事件对象)
```

所以：

- `(event) => ...` 能收到事件对象
- `() => ...` 也能正常运行，只是你不接参数

### Zustand 中的 `set` / `state`

```javascript
create((set) => ({
  count: 1,
  inc: () => set((state) => ({ count: state.count + 1 }))
}))
```

内部近似：

```javascript
function create(initFn) {
  const set = 内部准备好的更新函数
  return initFn(set)
}
```

`set` 不是凭空出现的，是 Zustand 在执行你的初始化函数时主动传入的。

### 参数名可以随便写

```javascript
onClick={(event) => ...}
onClick={(e) => ...}
onClick={(abc) => ...}        // 都行
```

**参数名只是局部变量名，真正关键的是调用者传了什么。**

### 统一思维理解所有回调

| 场景 | 调用者 | 传入参数 |
|---|---|---|
| React `onClick` | React 内部 | `event` 事件对象 |
| `arr.map((item, i) => ...)` | `map` 内部遍历 | 当前元素 + 索引 |
| `arr.filter((item) => ...)` | `filter` 内部遍历 | 当前元素 |
| Zustand `create((set) => ...)` | Zustand 内部 | `set` 函数 |
| Zustand `set((state) => ...)` | Zustand `set` 内部 | 当前 `state` |

> 类比：餐厅点菜时你说「菜好了叫我」，餐厅叫号时额外告诉你「32 号餐好了」——这「32 号」就是调用时附加的参数。

---

## 二、同步 vs 异步

### 同步

代码一行一行执行，**前一行未完成会阻塞后续代码**。

### 异步

不阻塞主线程，任务完成后通过回调 / Promise / await 通知。

常见异步场景：

- `setTimeout` / `setInterval`
- 网络请求（fetch / axios）
- 文件读写（Node.js）
- 用户事件（点击、输入）
- Promise / async-await

---

## 三、事件循环（Event Loop）

JS 是**单线程**语言，异步通过事件循环实现。

### 执行模型

```
调用栈（Call Stack）          ← 同步任务
   ↓                       
微任务队列（Microtasks）     ← Promise.then / queueMicrotask
   ↓
宏任务队列（Macrotasks）     ← setTimeout / setInterval / I/O / UI 渲染
```

### 执行顺序

1. 执行调用栈中的同步代码
2. 调用栈空后，**先清空所有微任务**
3. 取一个宏任务执行
4. 重复 2~3

### 经典示例

```javascript
console.log('1')

setTimeout(() => console.log('2'), 0)

Promise.resolve().then(() => console.log('3'))

console.log('4')

// 输出：1 4 3 2
```

> 因为 `Promise.then` 是微任务，`setTimeout` 是宏任务。

---

## 四、Promise

### 基本用法

```javascript
const p = new Promise((resolve, reject) => {
  // 异步操作
  if (success) resolve(data)
  else         reject(error)
})

p.then(data => console.log(data))
 .catch(err => console.error(err))
 .finally(() => console.log('done'))
```

### 状态机

- `pending` → `fulfilled`（resolve 调用）
- `pending` → `rejected`（reject 调用）
- 状态一旦改变就**不可逆**

### 链式调用

```javascript
fetch('/api/user')
  .then(res => res.json())
  .then(user => fetch(`/api/posts/${user.id}`))
  .then(res => res.json())
  .then(posts => console.log(posts))
  .catch(err => console.error(err))
```

> 链式调用靠 **`then` 返回新的 Promise** 实现

### 静态方法

```javascript
Promise.all([p1, p2, p3])     // 全部成功才成功，任一失败立即失败
Promise.race([p1, p2, p3])    // 取第一个完成的（成功或失败）
Promise.allSettled([p1, p2])  // 等待全部完成（无论成功失败），返回结果数组
Promise.any([p1, p2])         // 取第一个成功的，全部失败才 reject
```

---

## 五、async / await

> async / await 是 Promise 的**语法糖**，让异步代码看起来像同步。

```javascript
async function getUser() {
  try {
    const res    = await fetch('/api/user')
    const user   = await res.json()
    const posts  = await fetch(`/api/posts/${user.id}`)
    return await posts.json()
  } catch (err) {
    console.error(err)
    throw err
  }
}
```

### 关键点

- `await` 只能在 `async` 函数中使用
- `await` 后面接 Promise，会阻塞直到该 Promise 决议
- 错误处理必须用 `try / catch`（或外层 `.catch`）
- `async` 函数总是返回 Promise

### 并发执行（不要被 await 串行化）

```javascript
// ❌ 串行：慢
const a = await fetchA()
const b = await fetchB()

// ✅ 并发：快
const [a, b] = await Promise.all([fetchA(), fetchB()])
```

---

## 六、模块化（ES Module）

### 历史背景

| 方案 | 环境 | 特点 |
|---|---|---|
| IIFE | 浏览器 | 函数作用域隔离 |
| CommonJS | Node.js | `require` / `module.exports`（同步） |
| AMD | 浏览器 | 异步加载，`define` / `require` |
| ES Module | 浏览器 + Node.js | **官方标准，目前主流** |

### ES Module 导入导出

#### 命名导出 / 导入

```javascript
// person.js
export class Person {
  sayHi() { console.log('hi') }
}

// app.js
import { Person } from './person.js'
const p = new Person()
```

#### 默认导出 / 导入

```javascript
// person.js
export default class Person {
  sayHi() { console.log('hi') }
}

// app.js —— 名字可自定义
import Person from './person.js'
```

### 路径规则

```javascript
import x from './a.js'         // 同目录
import x from '../a.js'        // 上一级
import x from './models/a.js'   // 子目录
```

> 注意：浏览器原生 ES Module **必须写完整后缀**（`.js`），Node.js 早期版本可不写，新版本也建议写。

### 一个文件 = 一个模块作用域

```javascript
// a.js
class A {}
```

```javascript
// app.js
import { A } from './a.js'      // ❌ 报错
```

> 因为 `A` 没有 `export`，外部无法访问——这天然实现**模块隔离**。

---

## 七、类的访问控制

### 默认：全部公开

```javascript
class Person {
  sayHi() {}          // ✅ 公共方法
}
const p = new Person()
p.sayHi()             // ✅ 外部可访问
```

### 私有字段 / 方法（`#` 前缀，ES2022）

```javascript
class Person {
  #secret() {
    console.log('private')
  }

  callSecret() {
    this.#secret()    // ✅ 内部可访问
  }
}

const p = new Person()
p.#secret()           // ❌ SyntaxError —— 外部无法访问
```

### static 方法

```javascript
class Person {
  static foo() {}     // 类方法
  bar() {}            // 实例方法
}

Person.foo()          // ✅
new Person().bar()    // ✅

new Person().foo()    // ❌ 实例不能调用 static
Person.bar()          // ❌ 类不能调用实例方法
```

### 模块访问规则汇总

```text
export → 才能被 import
默认方法 → public
#方法 → private（真私有，外部完全无法访问）
static 方法 → 只能通过类调用
```

### 注意：JS 没有 `protected`

```javascript
// 旧版「伪私有」约定
_secret() {}          // ❌ 只是命名约定，不是真私有，外部仍可访问
```

---

## 八、完整示例

### person.js

```javascript
export class Person {
  #age = 18           // 私有字段
  static create() {   // 静态工厂
    return new Person()
  }

  sayHi() {
    console.log('hi')
  }
}
```

### app.js

```javascript
import { Person } from './person.js'

const p = Person.create()
p.sayHi()             // ✅
p.#age                // ❌ 外部无法访问
```

---

## 九、配套 demo

详见：
- [example/js-demo/05_async/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/js-demo/05_async)（回调 / Promise / async-await / 事件循环）
- [example/js-demo/06_module/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/js-demo/06_module)（ES Module 导入导出 + 类访问控制）

---

## 十、可复用检查清单

- [ ] 异步错误是否用 `try / catch` 包住？
- [ ] 多个独立请求是否用 `Promise.all` 并发？
- [ ] 回调场景是否确认了「调用者是谁 / 会传什么参数」？
- [ ] 模块导入是否补全了 `.js` 后缀（浏览器原生 ESM）？
- [ ] 私有方法是否用 `#` 前缀（而非 `_` 命名约定）？
- [ ] `static` 方法是否仅通过类名调用，实例方法是否仅通过实例调用？
