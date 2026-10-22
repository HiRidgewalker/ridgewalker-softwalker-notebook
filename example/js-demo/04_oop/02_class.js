// 02 - class 语法与继承
// 对应 Hub/02_JavaScript进阶笔记.md 第六章

// ───── 1. class 基础 ─────
console.log('--- class 基础 ---')

class Person {
  #age = 0                          // 私有字段

  constructor(name) {
    this.name = name
    this.#age = 18
  }

  sayHi() {
    console.log(`Hi, I'm ${this.name}`)
  }

  static create(name) {             // 静态工厂方法
    return new Person(name)
  }

  // 私有方法（ES2022）
  #secret() {
    console.log('this is private')
  }

  reveal() {
    this.#secret()
  }
}

const alice = Person.create('Alice')
alice.sayHi()                       // Hi, I'm Alice
alice.reveal()                      // this is private
// alice.#secret()                  // ❌ SyntaxError

// ───── 2. 继承 ─────
console.log('\n--- 继承 ---')

class Student extends Person {
  constructor(name, grade) {
    super(name)                     // 必须先调用 super
    this.grade = grade
  }

  study() {
    console.log(`${this.name} is studying in grade ${this.grade}`)
  }

  // 方法重写
  sayHi() {
    super.sayHi()                   // 调用父类方法
    console.log(`(I'm a student in grade ${this.grade})`)
  }
}

const tom = new Student('Tom', 3)
tom.sayHi()
tom.study()

// ───── 3. static 方法访问规则 ─────
console.log('\n--- static 访问 ---')

class Foo {
  static bar() { console.log('static bar') }
  baz()       { console.log('instance baz') }
}

Foo.bar()                           // ✅
new Foo().baz()                     // ✅
// new Foo().bar()                  // ❌ 实例不能调用 static
// Foo.baz()                        // ❌ 类不能调用实例方法

// ───── 4. instanceof ─────
console.log('\n--- instanceof ---')

console.log(tom instanceof Student) // true
console.log(tom instanceof Person)  // true
console.log(tom instanceof Object)  // true
