// person.js — ES Module 导出示例
// 对应 Hub/03_JavaScript异步与模块笔记.md 第六、七章

// ───── 命名导出 ─────
export class Person {
  #age = 18                          // 私有字段

  constructor(name) {
    this.name = name
  }

  sayHi() {
    console.log(`Hi, I'm ${this.name}`)
  }

  static create(name) {
    return new Person(name)
  }

  #secret() {
    console.log('这是私有方法')
  }

  revealSecret() {
    this.#secret()                   // 类内部可访问
  }
}

// ───── 默认导出 ─────
export default class Animal {
  constructor(type) {
    this.type = type
  }

  speak() {
    console.log(`${this.type} makes a sound`)
  }
}

// ───── 模块作用域：未 export 则外部无法访问 ─────
class InternalHelper {
  help() { console.log('internal only') }
}
// export { InternalHelper }          // ← 不写这行，外部就 import 不到
