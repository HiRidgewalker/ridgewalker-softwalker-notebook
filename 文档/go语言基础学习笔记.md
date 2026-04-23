## 注意点

- `:=`这种自动推导变量类型的方式只能够在函数内部使用

## `fmt.printf()`符号代表的变量类型

```
%c  单一字符
%T  动态类型
%v  本来值的输出
%+v 字段名+值打印
%d  十进制打印数字
%p  指针，十六进制
%f  浮点数
%b 二进制
%s string
%q 见下面详解
```

|   |   |
|---|---|
|类型|`%q`<br><br>表现|
|`string`|加双引号 `"..."`|
|`rune/char`|加单引号 `'...'`<br><br>，表示字符|
|`[]byte`|转义成合法字符串，加双引号|

## go语言定义变量的方式总结

### 一、用 `var` 关键字定义变量

#### 1. 显式声明 + 初始化

```
// 复制编辑
var a int = 10
```

#### 2. 类型推断

```
// 复制编辑
var b = "hello" // Go 自动推断 b 是 string 类型
```

#### 3. 声明但不初始化（默认为零值）

```
// 复制编辑
var c bool // 默认值为 false
```

#### 4. 一次声明多个变量

```
// 复制编辑
var x, y int = 1, 2
var name, age = "Alice", 25
```

---

### ⚡ 二、简洁变量定义 `:=`（只能在函数内部用）

```
// 复制编辑
d := 3.14       // 推断为 float64
message := "hi" // 推断为 string
```

✅ 优点：简洁、快速 ⚠️ 注意：**不能在函数外用**，否则会编译错误！

---

### 📦 三、结构体变量的定义

```
// 复制编辑
type Person struct {
    Name string
    Age  int
}

var p1 Person // 零值初始化
p2 := Person{Name: "Bob", Age: 30} // 字面量初始化
```

---

### 🧙 四、常量 `const`（不可变）

```
// 复制编辑
const Pi = 3.14159
const Name = "GoLang"
```

⚠️ 只能是编译期能确定的值，不能用函数或变量来初始化。

---

### 🎯 五、使用 `new` 创建指针变量

```
// 复制编辑
var ptr *int = new(int)
*ptr = 100
```

`new(T)` 返回 `*T` 类型（指针），该值指向类型为 `T` 的零值。

---

### 🧩 六、使用 `make` 初始化引用类型（slice、map、chan）

```
// 复制编辑
s := make([]int, 5)        // 创建长度为5的切片
m := make(map[string]int)  // 创建一个map
ch := make(chan int)       // 创建一个channel
```

`make` 只用于三种引用类型：`slice`、`map`、`chan`

---

### 📊 总结表格：

|   |   |   |
|---|---|---|
|定义方式|示例|场景|
|`var`<br><br>+ 显式类型|`var x int = 10`|明确控制类型|
|`var`<br><br>+ 推断|`var x = "hi"`|更简洁，仍能全局使用|
|`:=`<br><br>简洁声明|`x := 10`|快速定义，**只能函数内**|
|`const`<br><br>常量|`const Pi = 3.14`|不可变常量|
|`new`<br><br>关键字|`ptr := new(int)`|分配零值指针|
|`make`<br><br>关键字|`s := make([]int, 5)`|创建引用类型|
|多变量声明|`var a, b = 1, 2`|简洁定义多个变量|

## new关键字详解

new在go中是一个很简洁但是功能明确的内建函数, 它只做一件事情

分配一块内存, 储存一个类型的零值，并返回改类型的指针

### 语法

```
// T 是任意类型（可以是基本类型、数组、结构体、自定义类型等等）
// 返回值是 *T 类型，即一个指向该类型零值的指针
p := new(T)
```

### 🔧 可以用于哪些类型？

|   |   |
|---|---|
|类型分类|示例|
|基本类型|`new(int)`<br><br>、`new(bool)`<br><br>、`new(float64)`|
|结构体|`new(MyStruct)`|
|数组|`new([10]int)`|
|自定义类型|`type MyInt int`<br><br>然后用 `new(MyInt)`|
|组合类型|`new([5]*string)`<br><br>、`new(map[string]int)`<br><br>（虽然不推荐）|

### 示例讲解

#### 基本类型

```
p := new(int)
fmt.Println(*p) // 输出 0
*p = 42
fmt.Println(*p) // 输出 42
```

#### 结构体类型

```
type Person struct {
	Name string
	Age  int
}

p := new(Person)
p.Name = "Alice"
p.Age = 25
fmt.Println(p) // &{Alice 25}
```

#### 自定义类型

```
type MyInt int
x := new(MyInt)
*x = 100
fmt.Println(*x) // 100
```

### new和make的区别

|   |   |   |
|---|---|---|
|特性|`new`|`make`|
|返回类型|指针 `*T`|本体（非指针）|
|用于|所有类型|只能用于：slice、map、chan|
|分配的内容|零值|已初始化的引用结构|
|示例|`new(int)`<br><br>→ `*int`|`make([]int, 5)`<br><br>→ `[]int`|

## type关键字用法

Go 语言中的 `type` 关键字用法非常灵活强大，它的核心作用是：

✅ **定义新类型** 或 **为已有类型创建别名**，也可以用来定义结构体、接口、函数类型等。

---

### 🧱 基本语法：

```
type NewType ExistingType
```

---

### 👇 常见用法分类整理如下：

---

#### 1️⃣ 自定义基础类型（创建新的类型）

```
type MyInt int

var a MyInt = 10
```

- `MyInt` 是一个新类型，底层是 `int`，但它和 `int` 不是同一种类型，不能直接赋值。
- 需要类型转换：`int(a)` 或 `MyInt(100)`

📌 常用于：增加类型安全、创建领域相关的类型（如 `UserID`、`Money`）

---

#### 2️⃣ 类型别名（Go 1.9+）

```
type MyString = string
```

- `MyString` 只是 `string` 的别名，完全等价，可以互换使用。

📌 用于兼容旧代码、统一命名等。

---

#### 3️⃣ 定义结构体类型（struct）

```
type Person struct {
    Name string
    Age  int
}
```

📌 结构体是 Go 语言面向对象编程的核心，类似于类。

---

#### 4️⃣ 定义接口类型（interface）

```
type Reader interface {
    Read(p []byte) (n int, err error)
}
```

📌 接口在 Go 中用于抽象和多态，是非常核心的概念。

---

#### 5️⃣ 定义函数类型（function type）

```
type Adder func(a int, b int) int

func Sum(a int, b int) int {
    return a + b
}

var f Adder = Sum
```

📌 适用于函数作为参数、回调、组合函数等。

---

#### 6️⃣ 定义数组、切片、map、chan 的类型

```
type IntSlice []int
type StringMap map[string]string
type IntChan chan int
```

📌 让复杂类型的声明更清晰，更易管理。

---

#### 7️⃣ 嵌套类型（组合结构）

```
go


复制编辑
type Address struct {
	City string
}

type User struct {
	Name    string
	Address // 匿名字段，支持组合
}
```

📌 Go 的“继承”机制通过结构体嵌套实现。

---

### ✅ 总结：`type` 能干什么？

|   |   |   |
|---|---|---|
|用法|示例|说明|
|定义新类型|`type MyInt int`|类型不兼容，需要转换|
|类型别名|`type MyStr = string`|完全等价|
|定义结构体|`type Person struct {}`|类似类|
|定义接口|`type Reader interface {}`|抽象行为|
|函数类型|`type Handler func()`|函数作为值|
|容器类型别名|`type IntList []int`|更清晰的代码结构|

## 结构体

创建结构体的语法

```
// 写法1
type T struct {
    field1 type1
    field2 type2
    ...
}

// 写法2： 字段类型相同的情况下
type T struct {X,Y int}

// 实际案例
type Vertex struct {
    X int
    Y int
}

```

## 方法

### 方法定义

Go没有类。但是，您可以在类型上定义方法。方法是一个具有特殊接收器参数的函数。接收器出现在自己的参数列表中，位于func关键字和方法名称之间。语法如下

```
func (t 类型) 方法名(参数名 参数类型 ...) [返回值类型]{
}
```

### 案例1

```
package main

import (
	"fmt"
	"math"
)

type Vertex struct {
	X, Y float64
}

func (v Vertex) Abs() float64 {
	return math.Sqrt(v.X*v.X + v.Y*v.Y)
}

func main() {
	v := Vertex{3, 4}
	fmt.Println(v.Abs())
}
```

`函数`与`方法`的区别

在这个例子中，Abs方法有一个名为v的Vertex类型的接收器。请记住：方法只是一个带有接收器参数的函数。下面的Abs是作为一个普通函数编写的，函数本身没有变化。

```
func Abs(v Vertex) float64 {
	return math.Sqrt(v.X*v.X + v.Y*v.Y)
}

func main() {
	v := Vertex{3, 4}
	fmt.Println(Abs(v))
}
```

### 在非结构类型上申明一个方法

```
type MyFloat float64

func (f MyFloat) Abs() float64 {
	if f < 0 {
		return float64(-f)
	}
	return float64(f)
}
```

注意点： 在这个例子中，我们看到一个带有Abs方法的数字类型MyFloat。只能声明具有接收器的方法，该接收器的类型与该方法在同一个包中定义。不能使用类型在另一个包（包括int等内置类型）中定义的接收器来声明方法。

### 指针接收器

上面的定义方法例子中我们使用的都是值接收器，还可以使用指针接收器声明方法。这意味着接收器类型是类型T的指针_T。（此外，T本身不能是_int之类的指针。） 例如，此处的“Scale”方法是在“*Vertex”上定义的。

#### 示例

```
package main

import (
	"fmt"
	"math"
)

type Vertex struct {
	X, Y float64
}

func (v Vertex) Abs() float64 {
	return math.Sqrt(v.X*v.X + v.Y*v.Y)
}

func (v *Vertex) Scale(f float64) {
	v.X = v.X * f
	v.Y = v.Y * f
}

func main() {
	v := Vertex{3, 4}
	v.Scale(10)
	fmt.Println(v.Abs())
}
```

#### 值接收器和指针接收器的异同

带有指针接收器的方法可以修改接收器指向的值（就像Scale在这里所做的那样）。由于方法通常需要修改其接收器，因此指针接收器比值接收器更常见。可以试一下将 Scale 方法改为 值接收器方法看一下是否能起到相同的作用。对于值接收器，“Scale”方法对原始“Vertex ”值的副本进行操作。（这与任何其他函数参数的行为相同。）Scale方法必须有一个指针接收器才能更改主函数中声明的Vertex值。因此：

- 如果方法内部需要修改结构的字段值，并且对调用方可加则需要用指针接收器。
- 另外如果结构体有很多的字段，使用值接收器时会发生结构体的整体拷贝，为了减少拷贝可以使用指针接收器
- 其他情况，值接收器都可以被使用
- 给定类型上的所有方法都应该具有值或指针接收器，但不能同时具有这两者

## `nil`关键字

`nil` 是一个**预定义的标识符**，表示“零值”或“空值”，用于表示指针、接口、切片、通道、映射（map）、函数等类型在没有被初始化或为空的状态。

### 常见的使用场景：

1. **指针类型**

```
var p *int // p 是一个指针
fmt.Println(p == nil) // true
```

2. **接口类型**

```
var i interface{}
fmt.Println(i == nil) // true
```

3. **切片（slice）**

```
var s []int
fmt.Println(s == nil) // true
```

4. **映射（map）**

```
var m map[string]int
fmt.Println(m == nil) // true
```

5. **通道（channel）**

```
var ch chan int
fmt.Println(ch == nil) // true
```

6. **函数**

```
var f func()
fmt.Println(f == nil) // true
```

---

### 总结

`nil` 就是“什么都没有”的意思，但它只适用于那些**引用类型**（指针、slice、map、channel、interface、func），不是所有类型都能用 `nil`。