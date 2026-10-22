# Go 面向对象笔记

> Go **没有 class**，但用 `struct`（数据）+ `method`（行为）+ `interface`（多态）+ `embedding`（复用）四件套实现"面向对象"。
> 这套设计是 Go 的精髓——比传统 OOP 简单，但需要换一种思维方式。
> 对应 demo：[04_oop](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/example/go/demos/04_oop/main.go)

---

## 1. struct：数据载体

### 1.1 定义

```go
type Person struct {
    Name string
    Age  int
    City string
}
```

### 1.2 字段类型相同的简化

```go
type Point struct{ X, Y int }
```

### 1.3 6 种实例化方式

```go
// 1. 零值
var p1 Person
// 2. 字面量（按字段顺序，不推荐）
p2 := Person{"张三", 25, "北京"}
// 3. 字面量（指定字段名，✅ 推荐）
p3 := Person{Name: "李四", Age: 30}
// 4. 取指针
p4 := &Person{Name: "王五", City: "上海"}
// 5. new（零值指针）
p5 := new(Person)
p5.Name = "赵六"
// 6. 构造函数（约定返回 *T）
p6 := NewPerson("周八", 40, "广州")
```

```go
func NewPerson(name string, age int, city string) *Person {
    return &Person{Name: name, Age: age, City: city}
}
```

> 字段访问永远用 `.`：`p1.Name`、`p4.Name`（指针自动解引用）。

### 1.4 字段可见性（重要！）

- **首字母大写**：导出（其他包可见）
- **首字母小写**：包内私有

```go
type User struct {
    Name  string  // 导出
    email string  // 不导出（其他包访问不到）
}
```

---

## 2. 方法（method）

### 2.1 定义

```go
func (接收器) 方法名(参数) 返回值 { ... }
```

### 2.2 接收器两种类型

#### 值接收器

```go
func (p Person) Greet() string {
    return "Hi, I'm " + p.Name
}
```

- 操作的是**副本**
- 不会修改原对象
- 适合：只读、值很小、纯计算

#### 指针接收器

```go
func (p *Person) HaveBirthday() {
    p.Age++   // 改的是原对象
}
```

- 操作的是**原对象**
- 可以修改
- 适合：要改 / 结构体大 / 接口一致性

### 2.3 选择规则

| 情况 | 选 |
| --- | --- |
| 方法要修改接收器 | 指针 |
| 结构体字段多、避免拷贝 | 指针 |
| Map、Slice、Channel 内元素 | 指针 |
| 其他情况 | 值 |

> **混用规则**：**一个类型上的方法，要么全是值接收器，要么全是指针接收器**。混用容易出 bug。

### 2.4 给自定义类型加方法

```go
type MyFloat float64
func (f MyFloat) Abs() float64 { ... }
```

> **不能**给**别的包定义的类型**加方法（如 `int`、`time.Time`），但可以基于它们定义**新类型**再加方法。

---

## 3. 嵌入（embedding）—— Go 的"继承"

### 3.1 是什么

把一个 struct 当**匿名字段**放到另一个 struct 里，外层自动获得内层的字段和方法（字段提升）。

```go
type Person struct { Name string; Age int; City string }
type Employee struct {
    Person                // 匿名字段
    Salary int
    Dept   string
}
```

```go
e := Employee{
    Person: Person{Name: "钱七", Age: 28, City: "深圳"},
    Salary: 30000,
}

// 字段提升：e.Name 等价于 e.Person.Name
fmt.Println(e.Name, e.City, e.Salary)

// 方法也提升：e.Greet() 等价于 e.Person.Greet()
fmt.Println(e.Greet())
```

### 3.2 vs 传统继承

| 维度 | 传统继承（Java） | Go 嵌入 |
| --- | --- | --- |
| 关系 | "is-a" | **"has-a"**（内部有） |
| 多态 | 通过父类 | **不能**当父类用（多态靠 interface） |
| 重写 | override | **没有**，要"重写"用同名字段遮蔽 |

### 3.3 同名字段遮蔽

```go
type Employee struct {
    Person
    Name string   // 遮蔽了 Person.Name
}
e := Employee{Person: Person{Name: "内层"}, Name: "外层"}
fmt.Println(e.Name)        // "外层"
fmt.Println(e.Person.Name) // "内层"
```

---

## 4. interface：多态 ⭐ 关键

### 4.1 是什么

一组**方法签名**的集合。**任何类型只要实现了接口里所有方法，就自动实现了接口**（鸭子类型，编译期检查）。

### 4.2 定义与实现

```go
// 任何有 Speak() string 的类型都实现 Speaker
type Speaker interface {
    Speak() string
}

type Dog struct{ Name string }
func (d Dog) Speak() string { return d.Name + ": 汪" }

type Cat struct{ Name string }
func (c Cat) Speak() string { return c.Name + ": 喵" }
```

### 4.3 多态用法

```go
speakers := []Speaker{Dog{Name: "旺财"}, Cat{Name: "小花"}}
for _, s := range speakers {
    fmt.Println(s.Speak())   // 调各自的实现
}
```

### 4.4 接口组合

```go
type Reader interface { Read(p []byte) (n int, err error) }
type Writer interface { Write(p []byte) (n int, err error) }

// 嵌入组合出新接口
type ReadWriter interface {
    Reader
    Writer
}
```

### 4.5 多类型 / 多接口关系

| 场景 | Go 怎么写 |
| --- | --- |
| 一个类型实现多个接口 | 直接满足多个接口的方法集即可 |
| 多个类型实现同一个接口 | 同上，**不需要** `implements` 关键字 |
| 一个类型嵌入另一个类型 | 内嵌类型实现的接口，**外层也自动实现** |

### 4.6 空接口 `interface{}` / `any`

能存**任意类型**（Go 1.18+ 推荐用 `any` 替代 `interface{}`）：

```go
var x interface{} = 42
var y any = "hello"

fmt.Printf("%v %T\n", x, x)  // 42 int
```

空接口的三个常见用途：
1. `fmt.Println(a ...any)` — 接收任意类型
2. `map[string]any` — 通用 KV
3. JSON 反序列化到 `map[string]any`

### 4.7 类型断言（从 interface 拿回具体类型）

```go
var s Speaker = Dog{Name: "旺财"}

// 不安全（panic 风险）
dog := s.(Dog)               // 断言失败 panic

// 安全（ok 模式）
dog, ok := s.(Dog)
if ok {
    fmt.Println(dog.Name)
}
```

### 4.8 type switch

```go
switch v := s.(type) {
case Dog:
    fmt.Println("dog:", v.Name)
case Cat:
    fmt.Println("cat:", v.Name)
default:
    fmt.Println("other")
}
```

---

## 5. 常见坑

| 坑 | 说明 |
| --- | --- |
| 混用值/指针接收器 | 同一类型的方法要么全值，要么全指针 |
| nil 接口 != 持有 nil 指针的接口 | 后者调用方法会 panic（"method on nil"） |
| 接口零值是 nil | `var s Speaker` 是 nil，调方法 panic |
| 空接口性能 | `any` 涉及 boxing，开销比具体类型大；高频路径别用 |
| 接口"小而美" | 倾向于定义**只含 1~3 个方法**的小接口（`io.Reader` 只有一个方法） |
| 接口断言没 ok | 没 `ok` 模式断言失败会 panic |
| 嵌入遮蔽 | 字段/方法名同优先级时，外层遮蔽内层 |

---

## 6. Go OOP 与传统 OOP 对比

| 维度 | Java/C++/Python | Go |
| --- | --- | --- |
| 数据 + 行为 | class | struct + method |
| 复用 | 继承 | 嵌入（has-a） |
| 多态 | 父类引用 + override | interface（鸭子类型） |
| 封装 | private/public | 命名大小写 |
| 抽象类 / 接口继承 | abstract class | interface 嵌入 |

> **思维转换**：从"is-a 继承链"切到"组合 + 小接口"。

---

## 7. 速记口诀

- **方法 = 函数 + 接收器**
- **嵌入 = has-a**（不是 is-a）
- **接口 = 方法签名集合**，实现靠"长得像"
- **空接口 = any**，慎用（性能 + 类型丢失）
- **类型断言**：从 interface 拿回具体类型
