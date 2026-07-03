// 01 - 作用域与闭包
// 对应 Hub/02_JavaScript进阶笔记.md 第一、二、三章

// ───── 1. var vs let 的作用域 ─────
console.log('--- var vs let ---')

{
  var v = 10      // 没有块级作用域
  let l = 20      // 仅块内可见
}

console.log(v)     // 10
// console.log(l)  // ❌ ReferenceError

// ───── 2. 变量提升 ─────
console.log('\n--- 变量提升 ---')

console.log(a)     // undefined（var 提升，初始值 undefined）
// console.log(b)  // ❌ ReferenceError（let TDZ）
var a = 1
let b = 2

// ───── 3. 闭包：数据私有化 ─────
console.log('\n--- 闭包 ---')

function makeCounter() {
  let count = 0
  return {
    inc() { count++ },
    get() { return count }
  }
}

const counter = makeCounter()
counter.inc()
counter.inc()
counter.inc()
console.log(counter.get())         // 3
console.log(count)                 // ❌ ReferenceError（外部无法直接访问 count）

// ───── 4. 闭包实战：函数调用计数 ─────
console.log('\n--- 调用计数 ---')

function countCalls() {
  let i = 0
  return function () {
    i++
    console.log(`第 ${i} 次调用`)
  }
}

const fn = countCalls()
fn()                               // 第 1 次调用
fn()                               // 第 2 次调用
fn()                               // 第 3 次调用

// ───── 5. 闭包陷阱：循环里的 var ─────
console.log('\n--- 循环闭包陷阱 ---')

// ❌ var：所有回调共享同一个 i
const funcs1 = []
for (var i = 0; i < 3; i++) {
  funcs1.push(() => console.log(i))
}
funcs1.forEach(f => f())           // 3 3 3

// ✅ let：每次循环创建独立的 i
const funcs2 = []
for (let i = 0; i < 3; i++) {
  funcs2.push(() => console.log(i))
}
funcs2.forEach(f => f())           // 0 1 2
