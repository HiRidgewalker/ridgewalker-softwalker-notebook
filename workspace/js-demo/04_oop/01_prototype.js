// 01 - 构造函数与原型链
// 对应 Hub/02_JavaScript进阶笔记.md 第五章

// ───── 1. 构造函数的问题 ─────
console.log('--- 构造函数浪费内存 ---')

function PersonOld(name) {
  this.name = name
  this.sayHi = function () {        // ❌ 每个实例都创建一份新函数
    console.log(`Hi, I'm ${this.name}`)
  }
}

const p1 = new PersonOld('a')
const p2 = new PersonOld('b')
console.log(p1.sayHi === p2.sayHi)  // false

// ───── 2. 用原型共享方法 ─────
console.log('\n--- 原型共享 ---')

function Person(name) {
  this.name = name
}
Person.prototype.sayHi = function () {
  console.log(`Hi, I'm ${this.name}`)
}

const x = new Person('x')
const y = new Person('y')

console.log(x.sayHi === y.sayHi)    // ✅ true
x.sayHi()                           // Hi, I'm x

// ───── 3. 原型链核心关系 ─────
console.log('\n--- 原型链 ---')

console.log(x.__proto__ === Person.prototype)        // true
console.log(x.constructor === Person)                // true
console.log(Person.prototype.constructor === Person) // true
console.log(Person.prototype.__proto__ === Object.prototype) // true
console.log(Object.prototype.__proto__ === null)    // true（原型链终点）

// ───── 4. 覆盖原型时的 constructor 修复 ─────
console.log('\n--- constructor 修复 ---')

function Animal(name) {
  this.name = name
}

Animal.prototype = {                // 整体覆盖
  speak() { console.log('animal sound') }
}

console.log(Animal.prototype.constructor === Animal) // false（变成 Object）
console.log(Animal.prototype.constructor === Object) // true

// 修复
Animal.prototype = {
  constructor: Animal,
  speak() { console.log('animal sound') }
}
console.log(Animal.prototype.constructor === Animal) // true ✅
