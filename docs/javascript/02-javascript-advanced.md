---
title: "02_JavaScript 进阶笔记 — 作用域 / 闭包 / this / 面向对象"
sidebar_position: 2
---

# 02_JavaScript 进阶笔记 — 作用域 / 闭包 / this / 面向对象

> 本笔记为以下原文档的提炼合并 + 补全版：
> - 旧稿（var vs let、闭包、构造函数、原型链）
>
> 旧稿目录已清理，当前以本文为准。

---

## 一、作用域

### 三种作用域

| 类型 | 说明 |
|---|---|
| 全局作用域 | `var` / 直接声明在文件顶层的变量 |
| 函数作用域 | 函数内部（`var` / `let` / `const` 都受限于函数） |
| 块级作用域 | `{}` 包裹的代码块（仅 `let` / `const` 受限，`var` 不受限） |

### `var` vs `let` 的作用域差异

```javascript
{
  var i1 = 10     // 没有块级作用域
  let i2 = 20     // 仅块内可见
}
console.log(i1)   // 10
console.log(i2)   // ❌ ReferenceError
```

经典陷阱：

```javascript
for (var i = 1; i <= 3; i++) { /* ... */ }
console.log(i)    // 4 —— var 穿透到全局

for (let i = 1; i <= 3; i++) { /* ... */ }
console.log(i)    // ❌ ReferenceError —— let 受限于块
```

---

## 二、变量提升（Hoisting）

```javascript
console.log(a1)   // undefined
console.log(a2)   // ❌ ReferenceError
var a1
let a2
```

- `var`：声明被提升到作用域顶部，初始值为 `undefined`
- `let` / `const`：也存在提升，但进入「暂时性死区（TDZ）」，在声明前访问会报错

---

## 三、闭包

### 定义

> **闭包 = 内层函数 + 外层函数的变量**

```javascript
function outer() {
  let a = 10
  function fn() {
    console.log(a)   // 内层函数引用外层变量
  }
  fn()
}
outer()
```

### 闭包的作用：数据私有

```javascript
// 普通写法：i 是全局变量，易被外部修改
let i = 0
function fn() { i++ }

// 闭包写法：i 被封闭在 count 内部，外部无法直接访问
function count() {
  let i = 0
  function fn() {
    i++
    console.log(`调用 ${i} 次`)
  }
  return fn
}
const fun = count()
fun(); fun(); fun()    // 调用 1 次 / 2 次 / 3 次
```

### 闭包的代价

- **内存泄漏风险**：闭包持有的外层变量无法被 GC 回收，长生命周期场景要注意手动释放
- 调试不直观：栈追踪困难

### 应用场景

- 数据私有化（模块模式）
- 函数柯里化 / 偏函数
- 防抖 / 节流

---

## 四、`this` 指向（5 条规则，按优先级）

### 1. `new` 调用 → 指向新创建的实例

```javascript
function Foo() { this.x = 1 }
const f = new Foo()
console.log(f.x)        // 1
```

### 2. `call` / `apply` / `bind` 显式绑定 → 指向第一个参数

```javascript
function fn() { console.log(this.x) }
const obj = { x: 10 }
fn.call(obj)            // 10
fn.apply(obj)           // 10
const bound = fn.bind(obj)
bound()                 // 10
```

### 3. 对象方法调用 → 指向调用对象

```javascript
const obj = {
  x: 10,
  foo() { return this.x }
}
obj.foo()               // 10

// ⚠️ 经典陷阱：解构后 this 丢失
const f = obj.foo
f()                     // undefined（this 指向全局）
```

### 4. 普通函数调用 → 严格模式 `undefined`，非严格模式全局对象

```javascript
function foo() { console.log(this) }
foo()                   // 浏览器非严格：window；严格模式：undefined
```

### 5. 箭头函数 → **继承外层 `this`**，自己无法绑定

```javascript
const obj = {
  x: 10,
  foo: () => console.log(this.x)   // 箭头函数，this 指向外层（这里是模块作用域）
}
obj.foo()               // undefined
```

### 速记口诀

> **new > 显式绑定 > 对象调用 > 默认绑定；箭头函数无视以上一切，继承外层**

---

## 五、构造函数与原型

### 构造函数的问题：方法重复占用内存

```javascript
function Person(name) {
  this.name = name
  this.sayHi = function () {
    console.log('hi')
  }
}

const p1 = new Person('a')
const p2 = new Person('b')
console.log(p1.sayHi === p2.sayHi)   // false —— 每个实例各有一份函数
```

### 用原型共享方法

```javascript
function Person(name) {
  this.name = name
}

Person.prototype.sayHi = function () {
  console.log('hi')
}

const p1 = new Person('a')
const p2 = new Person('b')
console.log(p1.sayHi === p2.sayHi)   // true —— 共用原型上的方法
```

### 核心概念

| 名称 | 作用 |
|---|---|
| **构造函数** | 用于创建对象的函数 |
| **原型（Prototype）** | 存放共享属性和方法的对象 |
| **`prototype`** | 构造函数的属性，指向原型对象 |
| **`__proto__`** | 每个实例的隐藏属性，指向其原型对象 |
| **`constructor`** | 原型上的属性，指向构造函数本身 |

### 原型链 6 条核心结论

```javascript
function Person(name) { this.name = name }

const p1 = new Person('x')

p1.__proto__ === Person.prototype                    // true
p1.constructor === Person                           // true
Person.prototype.constructor === Person              // true
Person.prototype.__proto__ === Object.prototype      // true
Object.prototype.__proto__ === null                 // true
```

1. 每个构造函数都有原型对象
2. 原型对象都有 `constructor` 指向构造函数
3. 实例通过 `__proto__` 指向原型对象
4. 实例可访问原型上的属性 / 方法
5. 不同构造函数的原型对象互不相等
6. 原型链终点是 `null`

### 覆盖原型时的 `constructor` 修复

```javascript
Person.prototype = {
  sayHi() {}
}
// ⚠️ 此时 Person.prototype.constructor === Object（被覆盖了）

// 必须手动指回
Person.prototype = {
  constructor: Person,
  sayHi() {}
}
```

---

## 六、class 语法（ES6）

### 基础写法

```javascript
class Person {
  constructor(name) {
    this.name = name
  }

  sayHi() {
    console.log(`Hi, I'm ${this.name}`)
  }

  static create(name) {
    return new Person(name)
  }
}

const p = new Person('Alice')
p.sayHi()                       // Hi, I'm Alice
Person.create('Bob')            // 通过类名调用 static 方法
```

### 继承

```javascript
class Student extends Person {
  constructor(name, grade) {
    super(name)                 // 必须先调用 super
    this.grade = grade
  }

  study() {
    console.log(`${this.name} is studying`)
  }
}

const s = new Student('Tom', 3)
s.sayHi()                       // 继承自 Person
s.study()                       // 子类自有
```

### class vs 构造函数

| 维度 | class | 构造函数 |
|---|---|---|
| 方法定义位置 | 类体内（自动进原型） | 需手动挂 prototype |
| `extends` / `super` | 原生支持 | 需手动设置原型链 |
| 提升 | ❌ 不会提升（TDZ） | 函数声明会提升 |
| 严格模式 | 强制 | 默认非严格 |

---

## 七、对象继承的几种方式（补充）

### 1. 原型链继承

```javascript
Child.prototype = new Parent()
```

问题：引用类型属性被所有实例共享

### 2. 构造函数继承（经典继承）

```javascript
function Child() {
  Parent.call(this)
}
```

问题：方法无法复用

### 3. 组合继承（最常用）

```javascript
function Child() {
  Parent.call(this)             // 继承属性
}
Child.prototype = new Parent()  // 继承方法
Child.prototype.constructor = Child
```

### 4. class extends（推荐）

ES6 之后优先用 class 继承，底层依然是原型链。

---

## 八、配套 demo

详见 [example/js-demo/03_scope_closure/](https://github.com/HiRidgewalker/soft-tech-notebook/tree/main/example/js-demo/03_scope_closure) 和 [example/js-demo/04_oop/](https://github.com/HiRidgewalker/soft-tech-notebook/tree/main/example/js-demo/04_oop)

---

## 九、可复用检查清单

- [ ] 闭包是否会导致外层变量无法回收？长生命周期场景是否手动释放？
- [ ] `this` 是否需要提前用变量保存（`const self = this`）？
- [ ] 公共方法是否放进原型 / class，避免每个实例一份？
- [ ] 修改 `prototype` 后是否补回 `constructor`？
- [ ] 继承链是否调用了 `super()`？
