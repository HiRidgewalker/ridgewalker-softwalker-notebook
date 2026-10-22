// 01 - 箭头函数与解构赋值
// 对应 Hub/01_JavaScript笔记.md 第八、十一章

// ───── 1. 箭头函数基础 ─────
console.log('--- 箭头函数 ---')

const add = (a, b) => a + b
const square = n => n * n
const greet = (name = '游客') => `Hello, ${name}`

console.log(add(1, 2))          // 3
console.log(square(5))          // 25
console.log(greet())            // Hello, 游客

// ───── 2. 箭头函数 vs 普通函数的 this ─────
console.log('\n--- this 差异 ---')

const obj1 = {
  name: 'obj1',
  regular: function () { return this.name },
  arrow:   ()       => this?.name
}

console.log(obj1.regular())     // 'obj1'
console.log(obj1.arrow())       // undefined（继承外层 this，即模块作用域）

// ───── 3. 对象解构 ─────
console.log('\n--- 对象解构 ---')

const user = { name: 'Alice', age: 18, address: { city: 'Beijing' } }

const { name, age = 20 } = user
console.log(name, age)          // Alice 18

const { name: userName } = user
console.log(userName)           // Alice（重命名）

const { address: { city } } = user
console.log(city)               // Beijing（嵌套解构）

// ───── 4. 数组解构 ─────
console.log('\n--- 数组解构 ---')

const [first, second, ...rest] = [1, 2, 3, 4, 5]
console.log(first, second, rest)   // 1 2 [3, 4, 5]

// ───── 5. 函数参数解构 ─────
console.log('\n--- 函数参数解构 ---')

function printUser({ name, age }) {
  console.log(`${name} (${age})`)
}

printUser(user)                 // Alice (18)
