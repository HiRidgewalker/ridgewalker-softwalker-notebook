// app.js — ES Module 导入示例
// 对应 Hub/03_JavaScript异步与模块笔记.md 第六、七章

// ───── 命名导入 ─────
import { Person } from './person.js'

const alice = Person.create('Alice')
alice.sayHi()                         // Hi, I'm Alice
alice.revealSecret()                  // 这是私有方法
// alice.#secret()                   // ❌ SyntaxError

// ───── 默认导入 ─────
import Animal from './person.js'

const dog = new Animal('dog')
dog.speak()                           // dog makes a sound

// ───── 重命名导入 ─────
import { Person as P } from './person.js'

const bob = new P('Bob')
bob.sayHi()

// ───── 路径规则演示 ─────
// import x from './a.js'             // 同目录
// import x from '../a.js'            // 上一级
// import x from './models/a.js'      // 子目录

// ───── 尝试导入未导出的会报错 ─────
// import { InternalHelper } from './person.js'  // ❌ 报错

// ───── static vs 实例方法访问 ─────
console.log('\n--- static vs 实例 ---')

// Person.create('x')                // ✅ 通过类调用 static
// new Person().create('x')          // ❌ 实例不能调用 static
