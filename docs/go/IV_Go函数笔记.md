---
title: "Go 函数笔记"
sidebar_position: 4
---

# Go 函数笔记

> 本篇覆盖 Go 的函数特性：定义、参数、多返回值、命名返回值、不定参数、闭包、`defer`、`panic`/`recover`。
> 对应 demo：[03_functions](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/example/go/demos/03_functions/main.go)
>
> 范围说明：方法（method）见 [V_Go面向对象笔记](./V_Go面向对象笔记.md)，本篇只讲"独立函数"。

---

## 1. 函数定义

### 1.1 基础语法

```go
func 函数名(参数列表) (返回值列表) {
    // 函数体
}
```

### 1.2 三个特点

1. **参数类型合并**：相邻同类型可只写一次
2. **多返回值必须用括号**：`func f() (int, error)`，比 Python tuple 更类型安全
3. **函数顺序无关**：Go 是编译型，函数在哪定义都能调用

```go
func max(a, b int) int {              // 同类型合并
    if a > b { return a }
    return b
}

func div(a, b int) (int, int) {        // 多返回值：商 + 余
    return a / b, a % b
}
```

### 1.3 调用

```go
m := max(3, 5)
q, r := div(10, 3)                    // 多返回值直接多变量接
q, _ = div(10, 3)                     // 用 _ 忽略部分返回值
```

---

## 2. 形参三种形态

### 2.1 值传递（默认）

```go
func setX(x int) { x = 100 }    // 改不到外面的 x
```

### 2.2 指针传递（修改原值 / 避免大结构拷贝）

```go
func setXP(x *int) { *x = 100 } // 改得到
```

### 2.3 不定参数（variadic）

```go
func sum(prefix string, args ...int) int {  // args 是 []int
    total := 0
    for _, v := range args {
        total += v
    }
    return total
}

sum("hi", 1, 2, 3)          // 直接传
sum("hi", slice...)          // 切片展开
```

> - 不定参数本质是切片，可 `range`、可 `len`
> - 一个函数只能有一个不定参数，且要在最后

---

## 3. 返回值三种写法

### 3.1 单返回值

```go
func add(a, b int) int { return a + b }
```

### 3.2 多返回值

```go
func div(a, b int) (int, error) {
    if b == 0 { return 0, errors.New("div by zero") }
    return a / b, nil
}
```

### 3.3 命名返回值

```go
func f1() (names []string, m map[string]int, num int) {
    m = make(map[string]int)   // m 默认是 nil map
    m["k1"] = 2
    return                     // 隐式返回命名返回值的当前值
}
```

> 优点：返回值含义清晰；适合 defer 修改返回值（如 mutex 解锁、错误包装）
> 缺点：变量提前声明，函数体里能改它（有时是坑）

---

## 4. 函数作为值（first-class function）

### 4.1 函数类型

```go
type Handler func(int) int
```

### 4.2 函数作为形参和返回值

```go
func apply(n int, h Handler) int {
    return h(n)
}

func getMultiplier() func(int) int {
    return func(x int) int { return x * 2 }
}
```

### 4.3 匿名函数

```go
// 1. 直接调用
func(x int) { fmt.Println(x) }(42)

// 2. 赋给变量
double := func(x int) int { return x * 2 }

// 3. 传参
visit([]int{1, 2, 3}, func(v int) { fmt.Println(v) })
```

---

## 5. 闭包（closure）

闭包 = **函数 + 它引用的外层变量**。闭包捕获的是**变量本身**（不是值），所以多个闭包共享同一份变量。

```go
counter := func() func() int {
    i := 0
    return func() int {
        i++       // 捕获外层 i
        return i
    }
}()

fmt.Println(counter())  // 1
fmt.Println(counter())  // 2
fmt.Println(counter())  // 3  ← 同一个 i 累加
```

### 5.1 经典坑：循环变量捕获

```go
// Go 1.21 及之前
for i := 0; i < 3; i++ {
    go func() { fmt.Println(i) }()  // 几乎都打 3 3 3
}

// Go 1.22+ 修复：for 循环的 i 每次迭代独立
for i := 0; i < 3; i++ {
    go fmt.Println(i)  // 打 0 1 2
}
```

---

## 6. defer（延迟调用）⭐ Go 特色

### 6.1 是什么

`defer` 把函数调用**压栈**，在**外层函数返回前**按 LIFO（后进先出）顺序执行。

```go
func main() {
    defer fmt.Println("1")
    defer fmt.Println("2")
    defer fmt.Println("3")
    fmt.Println("main")
}
// 输出：
//   main
//   3
//   2
//   1
```

### 6.2 参数预求值

`defer` 后面的**参数在 defer 那一行就求值**了，后面的修改不影响它。

```go
x := 1
defer fmt.Println(x)   // 此时 x=1 被快照
x = 99
// 最终打 1
```

### 6.3 典型用法

```go
// 1. 释放资源
f, _ := os.Open("file")
defer f.Close()

// 2. 解锁
mu.Lock()
defer mu.Unlock()

// 3. 计时
start := time.Now()
defer fmt.Printf("took %v\n", time.Since(start))
doSomething()
```

### 6.4 配合命名返回值改结果

```go
func do() (err error) {
    defer func() {
        if r := recover(); r != nil {
            err = fmt.Errorf("panic: %v", r)
        }
    }()
    panic("oops")
}
```

---

## 7. panic + recover（异常机制）

Go 的 `panic` 相当于其他语言的"抛异常"，`recover` 是 catch。

### 7.1 区别

| 维度 | `error`（普通） | `panic`（严重） |
| --- | --- | --- |
| 处理 | 调用方判断 | `recover()` 捕获 |
| 适用 | 预期的错误（文件不存在、网络断） | 真正的异常情况（bug、配置错误） |
| 频率 | 高频 | 极低频 |
| 不捕获会怎样 | 调用方自己处理 | 程序崩溃 |

### 7.2 捕获模式

```go
func safeCall(fn func()) (recovered interface{}) {
    defer func() {
        recovered = recover()   // 接住 panic
    }()
    fn()                       // 这里 panic 就被上面接住
}
```

### 7.3 规则

- `recover()` 只能在 `defer` 里调用才有效
- `recover()` 之后程序从 panic 处继续**正常返回**，不会中断
- 不要用 panic 做正常错误处理

---

## 8. 函数 vs 方法

| 项 | 函数（function） | 方法（method） |
| --- | --- | --- |
| 语法 | `func f(...)` | `func (r T) f(...)` |
| 归属 | 包 | 类型 |
| 体现 | 独立工具 | "对象"行为 |

```go
// 函数
func max(a, b int) int { ... }

// 方法
func (p Person) Greet() string { ... }
```

方法详见 [V_Go面向对象笔记](./V_Go面向对象笔记.md)。

---

## 9. 常见坑

1. **defer 关闭资源的位置**：`f, _ := os.Open(...)` **紧接着** `defer f.Close()`，不要隔着其他代码
2. **defer 在循环里**：循环里的 defer 会在函数结束时一次性执行（栈累积），可能**耗尽文件描述符**
3. **闭包捕获循环变量**：Go 1.22 前需要手动传参（`go func(i int) {}(i)`）
4. **panic 没 recover**：直接崩溃整个进程
5. **多返回值忽略 error**：`f, _ := os.ReadFile(...)` 编译能过，但读失败时 `f` 是 nil
6. **命名返回值被提前改**：`return x` 会覆盖之前对命名返回值的修改
