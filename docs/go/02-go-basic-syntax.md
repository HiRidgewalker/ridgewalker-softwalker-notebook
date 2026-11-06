---
title: "Go 基础语法笔记"
sidebar_position: 2
---

# Go 基础语法笔记

> 本篇覆盖 Go 的基础语法：变量声明、基本类型、`fmt` 占位符、常量、类型转换、流程控制。
> 对应 demo：[01_basics](https://github.com/HiRidgewalker/soft-tech-notebook/blob/main/example/go/demos/01_basics/main.go)

---

## 1. 变量声明 6 种方式

| # | 方式 | 示例 | 适用 |
| --- | --- | --- | --- |
| 1 | `var` 显式类型 | `var a int = 10` | 想明确类型 / 全局变量 |
| 2 | `var` 类型推断 | `var b = "hello"` | 不想写类型，全局也能用 |
| 3 | `var` 零值（不初始化） | `var c bool` | 取类型零值（false/0/""） |
| 4 | 一次声明多个 | `var x, y = 1, 2` | 多变量简洁声明 |
| 5 | `:=` 简洁声明 | `d := 3.14` | **只能函数内**，最常用 |
| 6 | `new` 关键字 | `ptr := new(int)` | 需要指向零值的指针 |

```go
var a int = 10
var b = "hello"
var c bool                // 零值：false
var x, y = 1, 2
d := 3.14                 // 只能在函数内
ptr := new(int)           // *int 指针，*ptr 是 0
*ptr = 100
```

> **易混**：`var` 能用在包级（全局），`:=` **不能**。

---

## 2. 基本类型

### 2.1 类型清单

| 分类 | 类型 | 说明 |
| --- | --- | --- |
| 布尔 | `bool` | `true` / `false`（**不是** 1 / 0） |
| 字符串 | `string` | UTF-8 编码、不可变 |
| 字节 | `byte` | `uint8` 的别名 |
| Unicode 码点 | `rune` | `int32` 的别名 |
| 有符号整型 | `int` `int8` `int16` `int32` `int64` | `int` 长度随平台（32/64 位） |
| 无符号整型 | `uint` `uint8` `uint16` `uint32` `uint64` `uintptr` | 存指针用 `uintptr` |
| 浮点 | `float32` `float64` | 默认 `float64` |
| 复数 | `complex64` `complex128` | 很少用 |

### 2.2 整型范围

| 类型 | 范围 |
| --- | --- |
| `int8` | $-2^7$ ~ $2^7-1$（-128 ~ 127） |
| `uint8` | 0 ~ 255 |
| `int16` | -32768 ~ 32767 |
| `int32` | 约 ±21 亿 |
| `int64` | 约 ±9.2 × 10¹⁸ |

### 2.3 跨平台坑

> `int` 在 32 位机器是 4 字节、64 位机器是 8 字节。**跨平台写二进制协议 / 读写文件结构体时必须用 `int32` / `int64`**，否则换平台会出问题。

### 2.4 字符串 vs 字节 vs rune

```go
var s  string = "Go语言"   // 字符串，UTF-8
var b  byte   = 'A'        // byte = uint8，存 ASCII
var r  rune   = '中'       // rune = int32，存 Unicode 码点

fmt.Printf("%c %c %c\n", b, r, s[0])   // s[0] 是 byte，'G' = 71
```

| 写法 | 类型 | 用途 |
| --- | --- | --- |
| `'A'` | `rune`（int32） | 单个 Unicode 码点 |
| `"A"` | `string` | 字符串 |
| `[]byte("hello")` | `[]byte` | 字节切片（处理二进制 / 文件 IO） |
| `[]rune("你好")` | `[]rune` | Unicode 切片（按字符遍历中文） |

---

## 3. fmt 常用占位符

| 占位符 | 用途 | 示例输出 |
| --- | --- | --- |
| `%c` | 字符 | `A` |
| `%T` | 动态类型 | `string` |
| `%v` | 原值 | `Hello` |
| `%+v` | 字段名+值（结构体） | `{Name:Alice Age:25}` |
| `%d` | 十进制整数 | `255` |
| `%p` | 指针（十六进制） | `0xc00001a3b0` |
| `%f` | 浮点 | `3.140000` |
| `%.2f` | 浮点 2 位小数 | `3.14` |
| `%b` | 二进制 | `1010` |
| `%x` | 十六进制 | `ff` |
| `%s` | 字符串 | `hello` |
| `%q` | 加引号 | `"hello"` `'A'` |
| `%U` | Unicode 格式 | `U+0041` |

```go
fmt.Printf("name=%s age=%d\n", "alice", 25)
fmt.Printf("pi=%.2f\n", 3.14159)
fmt.Printf("%+v\n", person)            // 结构体带字段名
```

### 3.1 %q 加引号规则

| 类型 | 表现 |
| --- | --- |
| `string` | 加双引号 `"..."` |
| `rune` / `byte` | 加单引号 `'A'` |
| `[]byte` | 转义成合法字符串，加双引号 |

---

## 4. 类型转换

Go **不做隐式转换**，必须显式 cast。

```go
var f float64 = 3.14
var n int = int(f)              // 浮点转 int：截断小数
var r rune = 'A'
var s string = string(r)        // rune → string
```

### 4.1 规则

- 取值范围**小 → 大**：安全（如 `int16` → `int32`）
- 取值范围**大 → 小**：可能**精度丢失**（如 `int32` → `int16`、`float64` → `int`）
- **底层类型不同**不能转换（如 `bool` → `int` 编译错误）
- 数值 ↔ 字符串：用 `strconv`（见 [VI_Go包与工程笔记](06-go-packages-and-projects.md)）

---

## 5. 常量

```go
const Pi       = 3.14159         // 无类型常量
const Greeting = "Hello"         // 字符串常量

// 块声明
const (
    StatusOK       = 200
    StatusNotFound = 404
)

// iota 枚举
const (
    Mon = iota  // 0
    Tue         // 1
    Wed         // 2
)
```

### 5.1 规则

- 必须是**编译期能确定的值**（不能用 `:=`、不能用变量初始化）
- 没有类型时，可以赋给任何兼容类型

---

## 6. 流程控制

### 6.1 if（支持初始化语句）

```go
if x := 10; x > 5 {
    fmt.Println("big")
} else if x > 0 {
    fmt.Println("small")
} else {
    fmt.Println("zero or negative")
}
```

> `x` 只在 `if-else` 块内可见。

### 6.2 for（Go 只有 for，没有 while）

```go
// 经典
for i := 0; i < 10; i++ { ... }

// while 等价
for x > 0 { ... }

// 死循环
for { ... }

// range 遍历
for i, v := range []int{1, 2, 3} { ... }    // 索引 + 值
for k, v := range map[string]int{} { ... }  // 键 + 值
for i := range 5 { ... }                     // 只要索引 0..4（Go 1.22+）
```

> `_` 忽略返回值：`for _, v := range slice`。

### 6.3 switch（自动 break，不穿透）

```go
switch day {
case "Mon", "Tue":
    fmt.Println("工作日")
case "Sat", "Sun":
    fmt.Println("周末")
default:
    fmt.Println("未知")
}

// tag-less switch（if-else 链替代）
switch {
case x < 0:
    fmt.Println("负")
case x == 0:
    fmt.Println("零")
default:
    fmt.Println("正")
}
```

> 不写 `break`，**case 默认不穿透**。要穿透用 `fallthrough`（少用）。

### 6.4 goto / break / continue / label

- `break` 默认跳最近一层循环
- `continue` 跳过本轮
- `label` 可跳出多层循环（少用，可读性差）

```go
Outer:
for i := 0; i < 3; i++ {
    for j := 0; j < 3; j++ {
        if i*j == 2 { break Outer }
    }
}
```

---

## 7. 常见坑

| 坑 | 说明 |
| --- | --- |
| `int` 跨平台 | 32/64 位机器长度不同，二进制 IO 必须用定长类型 |
| 字符串不可变 | `s[0] = 'X'` 编译错误；要 `[]byte(s)` 转 |
| 数组 vs 切片 | `[3]int` 是值传递；`[]int` 是引用（共享底层数组） |
| `:=` 全局报错 | `:=` 只能在函数内，全局必须用 `var` |
| 变量声明不用 | 编译错误（除 `_`、包级 `var`、函数内 `:=` 零值可被覆盖外） |
| `nil` map 写报错 | `var m map[string]int` 是 nil，必须 `make` 才能写 |
