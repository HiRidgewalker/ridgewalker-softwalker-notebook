// 02 - this 指向 5 条规则
// 对应 Hub/02_JavaScript进阶笔记.md 第四章

'use strict'

// ───── 1. 普通函数调用 ─────
console.log('--- 普通函数调用（严格模式）---')

function foo() {
  console.log(this)
}
foo()                               // undefined（严格模式）

// ───── 2. 对象方法调用 ─────
console.log('\n--- 对象方法 ---')

const obj = {
  name: 'obj',
  greet() {
    console.log(`Hi, I'm ${this.name}`)
  }
}
obj.greet()                         // Hi, I'm obj

// ⚠️ 解构后 this 丢失
const greetFn = obj.greet
greetFn()                           // Hi, I'm undefined

// ───── 3. 显式绑定：call / apply / bind ─────
console.log('\n--- 显式绑定 ---')

function introduce(greeting) {
  console.log(`${greeting}, I'm ${this.name}`)
}

const alice = { name: 'Alice' }
const bob   = { name: 'Bob' }

introduce.call(alice, 'Hello')      // Hello, I'm Alice
introduce.apply(bob, ['Hi'])        // Hi, I'm Bob

const bound = introduce.bind(alice)
bound('Hey')                        // Hey, I'm Alice

// ───── 4. new 绑定 ─────
console.log('\n--- new 绑定 ---')

function Person(name) {
  this.name = name
}
const p = new Person('Tom')
console.log(p.name)                 // Tom

// ───── 5. 箭头函数：继承外层 this ─────
console.log('\n--- 箭头函数 ---')

const group = {
  name: 'group',
  list: ['a', 'b', 'c'],
  // ✅ 用箭头函数保留外层 this（即 group）
  show() {
    this.list.forEach(item => {
      console.log(`${this.name}: ${item}`)
    })
  },
  // ❌ 普通函数会丢失 this
  showBroken() {
    this.list.forEach(function (item) {
      console.log(`${this?.name ?? '?'}: ${item}`)
    })
  }
}

group.show()
group.showBroken()
