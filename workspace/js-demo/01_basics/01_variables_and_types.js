// 01 - 变量声明与数据类型
// 对应 Hub/01_JavaScript笔记.md 第三、四章

// ───── 1. var / let / const 对比 ─────
console.log('--- 变量声明 ---')

var a = 10
let b = 20
const c = 30

// c = 40   // ❌ TypeError: Assignment to constant variable
b = 25     // ✅ let 可重新赋值

console.log({ a, b, c })

// ───── 2. 数据类型判断 ─────
console.log('\n--- 类型判断 ---')

console.log(typeof 123)             // number
console.log(typeof 'hello')         // string
console.log(typeof true)            // boolean
console.log(typeof undefined)       // undefined
console.log(typeof null)            // object  ⚠️ 历史 bug
console.log(typeof [])              // object
console.log(typeof {})              // object
console.log(Array.isArray([]))      // true  ✅ 数组判断正确姿势
console.log(typeof Symbol('id'))    // symbol

// ───── 3. 类型转换 ─────
console.log('\n--- 类型转换 ---')

// 显式
console.log(Number('123'))          // 123
console.log(Number('abc'))          // NaN
console.log(parseInt('12px'))       // 12
console.log(parseFloat('12.94px'))  // 12.94

// 隐式
console.log(1 + '2')                // '12'（字符串拼接）
console.log(2 - '1')                // 1（减法触发数字转换）
console.log(+'123')                 // 123（一元正号）

// ───── 4. 短路运算符 ─────
console.log('\n--- 短路运算符 ---')

console.log(0 || 'default')         // 'default'
console.log('hi' || 'default')      // 'hi'
console.log(null && 'x')            // null
console.log('a' && 'b' && 'c')      // 'c'（全是 truthy，返回最后一个）
