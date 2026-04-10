好，这个问题我帮你整理成一份**体系化总结（模块引用 + 访问控制）**，你可以当作“JS 类的使用规则手册”来看 👇

---

# 📘 JavaScript 类的访问机制总结

---

# 一、类如何被其他文件使用（模块机制）

👉 JS 现在是基于 **ES Module（ESM）** 的

---

## 1️⃣ 导出类（export）

---

### ✅ 命名导出

```javascript
// person.js
export class Person {
  sayHi() {
    console.log("hi");
  }
}
```

---

### 使用

```javascript
// app.js
import { Person } from "./person.js";

const p = new Person();
p.sayHi();
```

---

---

### ✅ 默认导出

```javascript
// person.js
export default class Person {
  sayHi() {
    console.log("hi");
  }
}
```

---

### 使用

```javascript
import Person from "./person.js";
```

---

---

## 2️⃣ 路径规则（必须掌握）

---

### 同目录

```javascript
import { Person } from "./person.js";
```

---

### 上一级目录

```javascript
import { Person } from "../person.js";
```

---

### 子目录

```javascript
import { Person } from "./models/person.js";
```

---

👉 关键：

```text
"./" 当前目录
"../" 上级目录
```

---

---

# 二、类的方法访问范围（公开 / 私有）

---

## 1️⃣ 默认：全部公开（重要）

```javascript
class Person {
  sayHi() {}   // ✅ 公共方法
}
```

👉 外部可以直接访问：

```javascript
const p = new Person();
p.sayHi();
```

---

---

## 2️⃣ 私有方法（# 前缀）

👉 ES2022 新特性

```javascript
class Person {
  #secret() {
    console.log("private");
  }

  callSecret() {
    this.#secret();
  }
}
```

---

### ❌ 外部访问会报错

```javascript
const p = new Person();
p.#secret(); // ❌ SyntaxError
```

---

👉 特点：

```text
✔ 只能在类内部访问
✔ 完全无法外部访问（真正私有）
```

---

---

## 3️⃣ 私有属性

```javascript
class Person {
  #age = 18;
}
```

---

---

## 4️⃣ static 方法访问规则

```javascript
class Person {
  static foo() {}
  bar() {}
}
```

---

### 访问方式：

```javascript
Person.foo();     // ✅
new Person().bar(); // ✅
```

---

### ❌ 错误访问

```javascript
new Person().foo(); // ❌
Person.bar();       // ❌
```

---

---

# 三、总结：哪些能访问？

---

## ✅ 可以访问的

```text
✔ export 出去的类
✔ 类的 public 方法
✔ static 方法（通过类访问）
✔ 实例方法（通过实例访问）
```

---

## ❌ 不能访问的

```text
✔ 没 export 的类
✔ # 私有方法 / 属性
✔ 未导入的模块
```

---

# 四、模块作用域（非常重要🔥）

---

👉 JS 文件本身就是一个模块作用域：

```javascript
// a.js
class A {}
```

---

### ❌ 外部访问不到

```javascript
import { A } from "./a.js"; // ❌ 报错
```

👉 因为：

```text
没有 export
```

---

---

# 五、完整示例（推荐你理解）

---

## person.js

```javascript
export class Person {
  #secret() {
    console.log("秘密");
  }

  sayHi() {
    console.log("hi");
  }

  static create() {
    return new Person();
  }
}
```

---

## app.js

```javascript
import { Person } from "./person.js";

const p = new Person();

p.sayHi();        // ✅
Person.create();  // ✅

p.#secret();      // ❌
```

---

---

# 六、访问规则总结（最重要🔥）

---

## 1️⃣ 模块层面

```text
export → 才能被 import
```

---

## 2️⃣ 类层面

```text
默认方法 → public
#方法 → private
```

---

## 3️⃣ 调用层面

```text
实例方法 → 实例调用
static方法 → 类调用
```

---

# 七、你可以这样记（超级简化版）

---

```text
文件之间：
export + import 才能访问

类内部：
默认全公开
# 开头是私有

调用：
实例 → 普通方法
类 → static 方法
```

---

# 八、进阶补充（你以后会用到）

---

## ❗ 没有“protected”（不像 Java）

👉 JS 只有：

```text
public / private(#)
```

---

## ❗ 以前的“伪私有”

```javascript
_secret() {} // ❌ 只是约定，不是真私有
```

---

## ❗ Node / 浏览器都一样（ESM）

---

# 🚀 如果你想再进阶（强烈建议）

我可以帮你讲：

👉 前端项目真实结构（service / model / store 怎么拆）  
👉 React 项目中类 / hook / 模块如何组织

这会直接提升你工程能力 💪