# 01_JavaScript 笔记 — 基础与 ES6+

> 本笔记为以下原文档的提炼合并 + 补全版：
> - 旧稿（短路运算符）
> - 旧稿（引入方式 / 变量 / 数据类型）
> - 旧稿（剩余参数 / 展开运算符部分）
>
> 旧稿目录已清理，当前以本文为准。

---

## 一、引入方式

JS 程序不能独立运行，需要嵌入 HTML 中由浏览器（或 Node.js）执行。

### 1. 内联方式

```html
<script>
  alert('Hello JS')
</script>
```

### 2. 外部引入

```html
<script src="demo.js"></script>
```

> ⚠️ `<script>` 标签一旦使用 `src` 属性引入外部文件，标签内部的代码会被**忽略**。

---

## 二、注释与输入输出

### 注释

```javascript
// 单行注释

/*
  多行注释
  可任意换行
*/
```

### 输出

| API | 说明 |
|---|---|
| `alert(msg)` | 浏览器弹窗 |
| `document.write(msg)` | 写入页面 |
| `console.log(msg)` | 浏览器 / Node 控制台 |

### 输入

```javascript
const name = prompt('请输入姓名')   // 浏览器弹窗输入
```

---

## 三、变量声明

### 三个关键字对比

| 关键字 | 块级作用域 | 变量提升 | 重复声明 | 推荐度 |
|---|---|---|---|---|
| `var` | ❌ | ✅（值为 undefined） | ✅ | 不推荐 |
| `let` | ✅ | ❌（TDZ） | ❌ | ✅ 推荐 |
| `const` | ✅ | ❌（TDZ） | ❌ | ✅ 优先 |

### 使用注意事项

- `const` 声明必须赋初值
- `const` 声明**基本类型**不可重新赋值；**引用类型**仅冻结引用，属性仍可改

```javascript
const obj = { a: 1 }
obj.a = 2          // ✅ 允许
// obj = {}         // ❌ 报错：assignment to constant variable
```

### 命名规则

- 只能包含字母、数字、下划线、`$`，且不能数字开头
- 区分大小写
- 不能用关键字 / 保留字
- 见名知义

---

## 四、数据类型

### 基本类型（值类型）

| 类型 | 示例 | 注意点 |
|---|---|---|
| `number` | `1`, `3.14`, `NaN` | `NaN` 是 number，不等于任何值包括自身 |
| `string` | `'hi'`, `"hi"`, `` `hi ${name}` `` | 三种引号均可，反引号支持模板字符串 |
| `boolean` | `true`, `false` | — |
| `undefined` | `let a` | 变量已声明但未赋值 |
| `null` | `let a = null` | 主动赋值为空，常用于「将来存放对象」 |
| `symbol` | `Symbol('id')` | 唯一值，常用于对象属性键 |
| `bigint` | `123n` | 大整数 |

### 引用类型

`object`（含 `array` / `function` / 普通对象）

### 类型判断

```javascript
typeof 123              // 'number'
typeof undefined        // 'undefined'
typeof null             // 'object'  ⚠️ 历史遗留 bug
typeof []               // 'object'
typeof function(){}     // 'function'

Array.isArray([])       // true —— 数组专用判断
```

---

## 五、类型转换

### 显式转换

```javascript
Number('123')           // 123
Number('pink')          // NaN
parseInt('12px')        // 12
parseInt('12.94px')     // 12（截断小数）
parseFloat('12.94px')   // 12.94
```

### 隐式转换

```javascript
1 + 1                   // 2
'pink' + 1              // 'pink1'（字符串拼接）
2 + '2'                 // '22'
2 - '2'                 // 0（减法触发数字转换）
+'123'                  // 123（一元正号转数字）
```

> 记忆口诀：**`+` 遇字符串变拼接，其他运算符转数字**

---

## 六、运算符

### 短路运算符（核心特性）

| 表达式 | 结果 |
|---|---|
| `0 \|\| "hi"` | `"hi"`（返回第一个 truthy） |
| `"" \|\| 0 \|\| false \|\| "yes"` | `"yes"` |
| `null \|\| undefined \|\| 0` | `0`（全是 falsy，返回最后一个） |
| `"abc" && 123` | `123`（全是 truthy，返回最后一个） |
| `"abc" && 0` | `0`（返回第一个 falsy） |

> **本质：`||` 返回第一个 truthy 或最后一个 falsy；`&&` 返回第一个 falsy 或最后一个 truthy**

### 实战用法

```javascript
// 1. 默认值兜底
const name = userInput || '游客'

// 2. 条件执行
isAdmin && showAdminPanel()
```

### 真值表（falsy 值）

以下 6 个值在布尔上下文中为 false，其余都为 true：

`false` / `0` / `''` / `null` / `undefined` / `NaN`

---

## 七、控制流

### 条件

```javascript
if (condition) {
  // ...
} else if (other) {
  // ...
} else {
  // ...
}

switch (value) {
  case 1: /* ... */ break
  default: /* ... */
}
```

### 循环

```javascript
for (let i = 0; i < arr.length; i++) { /* ... */ }
for (const item of arr)              { /* ... */ }   // 值遍历（推荐）
for (const key in obj)               { /* ... */ }   // 键遍历（对象）
while (condition)                    { /* ... */ }
```

---

## 八、函数基础

### 三种定义方式

```javascript
// 1. 函数声明（有提升）
function foo(a, b = 0) { return a + b }

// 2. 函数表达式
const foo = function(a, b) { return a + b }

// 3. 箭头函数（无 this 绑定）
const foo = (a, b) => a + b
```

### 动态参数 `arguments`

只在普通函数中存在的伪数组：

```javascript
function getSum() {
  let sum = 0
  for (let i = 0; i < arguments.length; i++) {
    sum += arguments[i]
  }
  return sum
}
getSum(2, 3, 4)         // 9
```

### 剩余参数 `...arr`

更现代的写法，**真数组**：

```javascript
function getSum(a, b, ...arr) {
  console.log(arr)      // [3, 4, 5]
}
getSum(1, 2, 3, 4, 5)
```

### 箭头函数注意点

- 没有自己的 `this`（继承外层）
- 不能作为构造函数（`new` 会报错）
- 没有 `arguments`

---

## 九、数组常用方法

### 遍历 / 转换

| 方法 | 返回值 | 是否改原数组 |
|---|---|---|
| `forEach(fn)` | `undefined` | 否 |
| `map(fn)` | 新数组（每个元素经 fn 处理） | 否 |
| `filter(fn)` | 新数组（fn 返回 true 的元素） | 否 |
| `reduce(fn, init)` | 累计值 | 否 |
| `find(fn)` | 第一个匹配的元素 | 否 |
| `some(fn)` | `boolean`（任一匹配） | 否 |
| `every(fn)` | `boolean`（全部匹配） | 否 |

### 增删改

```javascript
arr.push(x)              // 末尾追加，返回新长度
arr.pop()                // 末尾删除
arr.unshift(x)           // 头部追加
arr.shift()              // 头部删除
arr.splice(start, count, ...items)   // 任意位置增删改
arr.slice(start, end)    // 截取（不修改原数组）
```

### 典型 reduce 写法（求和、去重、按字段分组）

```javascript
// 求和
[1, 2, 3].reduce((acc, n) => acc + n, 0)            // 6

// 按字段分组
const users = [{age: 18}, {age: 30}, {age: 18}]
users.reduce((acc, u) => {
  (acc[u.age] ||= []).push(u)
  return acc
}, {})
// → {18: [{age:18}, {age:18}], 30: [{age:30}]}
```

---

## 十、字符串常用方法

| 方法 | 说明 |
|---|---|
| `str.length` | 长度 |
| `str[i]` | 按索引取字符 |
| `str.indexOf(s)` / `str.includes(s)` | 查找 |
| `str.slice(start, end)` | 截取子串 |
| `str.split(sep)` | 拆数组 |
| `str.replace(old, new)` | 替换（仅替换第一个） |
| `str.replaceAll(old, new)` | 全部替换 |
| `str.trim()` | 去首尾空白 |
| `str.startsWith(s)` / `str.endsWith(s)` | 开头 / 结尾判断 |

---

## 十一、对象常用方法

```javascript
const obj = { a: 1, b: 2, c: 3 }

Object.keys(obj)             // ['a', 'b', 'c']
Object.values(obj)           // [1, 2, 3]
Object.entries(obj)          // [['a',1], ['b',2], ['c',3]]
Object.fromEntries([['a',1]]) // { a: 1 }（entries 的逆操作）
Object.assign(target, src)   // 浅合并
Object.freeze(obj)           // 冻结（不可改）
```

### 解构赋值

```javascript
// 对象解构
const { name, age = 18 } = user

// 数组解构
const [first, second, ...rest] = arr

// 重命名
const { name: userName } = user
```

---

## 十二、ES6+ 速记

### 模板字符串

```javascript
const greeting = `Hello ${name}, you are ${age} years old`
```

### 展开运算符 `...`

```javascript
// 数组合并
const merged = [...arr1, ...arr2]

// 求最大最小值
Math.max(...arr1)
Math.min(...arr1)

// 函数实参展开
fn(...args)

// 对象浅拷贝
const clone = { ...obj }
```

### Set / Map

```javascript
// Set：值唯一的集合
const s = new Set([1, 2, 2, 3])
;[...s]                      // [1, 2, 3]

// Map：任意类型的键值对
const m = new Map()
m.set('key', 'value')
m.set(obj, 'meta')
m.get('key')                 // 'value'
m.has('key')                 // true
```

### 可选链 `?.` 与空值合并 `??`

```javascript
user?.address?.city          // 任意一段为 null/undefined 即短路
input ?? '默认值'            // 仅在 null/undefined 时用默认值（比 || 更精确）
```

---

## 十三、字符串 / 数组 / 对象常用方法速查表

详见配套 demo：[workspace/js-demo/01_basics/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/js-demo/01_basics)

---

## 十四、可复用检查清单

写新代码前自问：

- [ ] 变量能用 `const` 就不用 `let`
- [ ] 数组遍历用 `for...of` / `map` / `filter` 而非手写 for
- [ ] 默认值用 `??` 而非 `\|\|`（避免 `0` / `''` 被误判）
- [ ] 模板字符串处理多行拼接，而非 `+` 拼接
- [ ] 对象批量取值用解构
