# Go 复合类型笔记

> 本篇覆盖 Go 的复合类型：数组、切片、map、指针、类型别名 vs 新类型。
> 对应 demo：[02_composite](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/go/demos/02_composite/main.go)

---

## 1. 数组（array）

### 1.1 是什么

**定长**的特定类型元素序列，长度是类型的一部分（`[3]int` 和 `[4]int` 是不同类型）。

### 1.2 声明与初始化

```go
var arr1 [3]int = [3]int{1, 2, 3}    // 显式
arr2 := [...]int{1, 2, 3, 4}          // ... 让编译器数长度
arr3 := [5]int{2: 99}                 // 给索引 2 赋值，其余 0
var grid [2][3]int                     // 多维
```

### 1.3 遍历

```go
for i, v := range arr {
    fmt.Printf("i=%d v=%d\n", i, v)
}
```

### 1.4 比较

两个数组**类型相同**（含长度和元素类型）可用 `==` / `!=` 比较。**不同长度不能比较**（编译错误）。

### 1.5 特点

- 长度固定，**不能 append**
- 传参是**值传递**（整数组拷贝）→ 大数组传参性能差
- **Go 中很少直接用**，实际项目几乎都用切片

---

## 2. 切片（slice）⭐ 最常用

### 2.1 是什么

**动态数组**，是对底层数组的一个"窗口"（包含指针 + len + cap 三个字段）。

### 2.2 三要素

```go
s := make([]int, 3, 5)    // make([]T, len, cap)
fmt.Println(len(s), cap(s))  // 3 5
```

| 字段 | 含义 |
| --- | --- |
| 指针 | 指向底层数组 |
| `len` | 当前元素个数（`len(s)`） |
| `cap` | 从指针位置到底层数组末尾的容量（`cap(s)`） |

### 2.3 声明方式

```go
// 字面量
s1 := []int{1, 2, 3}

// make
s2 := make([]int, 3)      // len=3 cap=3
s3 := make([]int, 3, 10)  // len=3 cap=10（预分配空间减少扩容）

// 从数组 / 切片截取
arr := [5]int{0, 1, 2, 3, 4}
s4 := arr[1:4]            // [1 2 3]
```

### 2.4 切片操作语法

```go
s := []int{0, 1, 2, 3, 4, 5}
s[1:4]   // [1 2 3]      左闭右开
s[:3]    // [0 1 2]      缺省开始 = 从头开始
s[3:]    // [3 4 5]      缺省结束 = 到末尾
s[:]     // [0 1 2 3 4 5] 全切
s[0:0]   // []           空切片（常用于复位）
```

### 2.5 append（追加元素）

```go
s := []int{1, 2, 3}
s = append(s, 4)         // [1 2 3 4]
s = append(s, 5, 6, 7)   // 一次追加多个
s = append(s, other...)  // 展开另一个切片
```

> **必须接收返回值**：append 可能扩容，生成新切片。
> 扩容规则：cap < 1024 时翻倍，cap ≥ 1024 时增长 ~25%。

### 2.6 copy（复制）

```go
src := []int{1, 2, 3, 4}
dst := make([]int, 3)
n := copy(dst, src)   // 只复制 3 个 → dst=[1,2,3], n=3
```

> 复制个数 = `min(len(dst), len(src))`。

### 2.7 共享底层数组的坑

```go
a := []int{1, 2, 3, 4}
b := a[:2]              // b 引用 a 的前 2 个
b[0] = 999
fmt.Println(a)          // [999 2 3 4] ← a 也被改了！
```

**正确做法**：`copy` 出来：`b := make([]int, 2); copy(b, a[:2])`。

---

## 3. map（字典）

### 3.1 是什么

**无序**的 `key → value` 映射。

### 3.2 声明

```go
var m1 map[string]int                      // nil（不能写，必须 make）
m2 := map[string]int{"a": 1, "b": 2}        // 字面量
m3 := make(map[string]int, 4)               // make（推荐：能预分配容量）
```

### 3.3 操作

```go
m := make(map[string]int)
m["x"] = 100         // 写
m["x"] = 999         // 改
delete(m, "x")       // 删
v := m["x"]          // 读
v, ok := m["x"]      // 查在不在，ok=false 表示 key 不存在
```

### 3.4 遍历（顺序不固定！）

```go
for k, v := range m {
    fmt.Printf("%s=%d\n", k, v)
}
```

> map 的迭代顺序**故意随机**（Go 故意设计），防依赖特定顺序。如果需要有序，把 key 拿出来排序再遍历。

### 3.5 常见坑

| 坑 | 说明 |
| --- | --- |
| `var m map[K]V` 写值 | `m["x"] = 1` 编译期就过，运行期 panic（assignment to entry in nil map） |
| 取不存在的 key | 返回值类型零值，`ok=false` |
| map 不是并发安全 | 多个 goroutine 同时读写要加锁 / 用 `sync.Map` |

---

## 4. 指针（pointer）

### 4.1 是什么

指针存的是**另一个变量的内存地址**。Go 指针**不能运算**（不像 C 那样 `p++`）。

### 4.2 三个核心操作

```go
x := 42
p := &x        // & 取址，p 是 *int
fmt.Println(*p) // * 解引用，42
*p = 100        // 通过指针改值
fmt.Println(x)  // 100
```

| 操作 | 符号 | 作用 |
| --- | --- | --- |
| 取址 | `&x` | 拿到 x 的内存地址 |
| 解引用 | `*p` | 通过地址拿值 / 改值 |
| 类型 | `*T` | 指向 T 的指针 |

### 4.3 new

```go
p := new(int)    // *int 指针，*p 初始是 0
*p = 100
```

`new(T)` 返回 `*T`，指向 T 的零值。**和 `&T{}` 区别**：`new(T)` 不初始化字段，`&T{}` 走字面量。

### 4.4 传指针 vs 传值

```go
func setX(x int)    { x = 100 }   // 改不到外面的 x
func setXP(x *int)  { *x = 100 }  // 改得到
```

> **什么时候用指针**：
> 1. 想修改原变量
> 2. 结构体很大，避免拷贝
> 3. 实现接口的某些方法（保持一致性）
>
> 其他情况用值传递更简单。

### 4.5 nil 指针

```go
var p *int     // p == nil
fmt.Println(p) // <nil>
```

`nil` 指针解引用会 panic（**和 C 一样**）。

---

## 5. 类型别名 vs 新类型（type）

### 5.1 类型别名（type X = T）

```go
type IntAlias = int
var a IntAlias = 10
var b int = a        // ✅ 不用转换，完全等价
```

- Go 1.9+
- **完全等价于原类型**，编译器看到 `IntAlias` 就当 `int` 处理
- 用于兼容旧代码、统一命名

### 5.2 新类型（type X T）

```go
type NewInt int
var a NewInt = 20
// var b int = a   // ❌ 编译错误：cannot use a (type NewInt) as type int
var b int = int(a) // ✅ 必须显式转换
```

- **新类型与原类型不兼容**
- 编译时检查更严
- 常用于：增加类型安全、领域类型（`UserID`、`Money`）

### 5.3 速记

| 写法 | 关系 | 能不能直接互赋 |
| --- | --- | --- |
| `type X = T` | 别名 | ✅ 完全等价 |
| `type X T` | 新类型 | ❌ 必须 cast |

---

## 6. 综合对比

| 类型 | 长度 | 传参 | 适用 |
| --- | --- | --- | --- |
| 数组 `[N]T` | 固定 | 值拷贝 | 知道固定长度（如 SHA256 结果） |
| 切片 `[]T` | 动态 | 引用（共享） | **90% 场景** |
| `map[K]V` | 动态 | 引用 | KV 查找 |
| `*T` 指针 | 固定 | 引用 | 修改 / 避免大结构拷贝 |

---

## 7. 常见坑汇总

1. **切片共享底层数组**：子切片改值会影响父切片
2. **append 没接收返回值**：`s = append(s, x)`，不能 `append(s, x)` 然后用 `s`
3. **nil map 写值**：panic
4. **map 遍历顺序随机**：不要假设顺序
5. **指针运算**：Go 指针不能 `p++`（编译错误）
6. **类型别名 vs 新类型混用**：编译错误时先看是不是这里
