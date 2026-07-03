// 01_basics: Go 基础语法速览
//
// 涵盖：
//   - 变量声明的 6 种方式（var 显式/推断/多变量/零值、:= 简洁、new、make、const）
//   - 基本类型（int/uint/float/bool/string/byte/rune）
//   - fmt.Printf 常用占位符
//   - 类型转换
//   - 常量（const）
//   - 流程控制（if/for/switch）
//
// 运行：go run main.go
package main

import "fmt"

// 1. var 显式声明 + 初始化（包级/全局变量必须用 var）
var globalInt int = 42

// 2. var 类型推断
var inferred = "hello go"

// 3. var 零值（不初始化就是类型零值）
var zeroInt int       // 0
var zeroStr string    // ""
var zeroBool bool     // false

// 4. const 常量（编译期确定，不可修改）
const Pi = 3.14159
const Greeting = "你好"

// 多常量 + 块声明
const (
	StatusOK       = 200
	StatusNotFound = 404
)

func main() {
	fmt.Println("===== 1. 变量声明的 6 种方式 =====")

	// 方式 1：var + 显式类型
	var a int = 10
	fmt.Printf("var a int = 10            → a=%d, 类型=%T\n", a, a)

	// 方式 2：var + 类型推断
	var b = "hello"
	fmt.Printf("var b = \"hello\"          → b=%q, 类型=%T\n", b, b)

	// 方式 3：var 零值（声明不初始化）
	var c bool
	fmt.Printf("var c bool                → c=%v（默认值 false）\n", c)

	// 方式 4：一次声明多变量
	var x, y = 1, 2
	var name, age = "alice", 25
	fmt.Printf("var x, y = 1, 2           → x=%d y=%d\n", x, y)
	fmt.Printf("var name, age = ...       → name=%q age=%d\n", name, age)

	// 方式 5：:= 简洁声明（仅限函数内，不能用于全局）
	d := 3.14
	msg := "hi"
	fmt.Printf("d, msg := 3.14, \"hi\"      → d=%v msg=%q, 类型=%T %T\n", d, msg, d, msg)

	// 方式 6：new 返回 *T 指针
	ptr := new(int) // 指向 int 零值的指针
	*ptr = 100
	fmt.Printf("ptr := new(int); *ptr=100 → *ptr=%d, ptr 类型=%T\n", *ptr, ptr)

	fmt.Println("\n===== 2. 基本类型 =====")
	// int 随系统（32/64），跨平台写代码用 int32/int64
	var i8 int8 = 127
	var u8 uint8 = 255
	var f32 float32 = 3.14
	var f64 float64 = 3.141592653589793
	var boo bool = true
	var str string = "Go 语言"
	var by byte = 'A'  // byte = uint8
	var ru rune = '中' // rune = int32（一个 Unicode 码点）
	fmt.Printf("int8=%d  uint8=%d  float32=%v  float64=%.10f\n", i8, u8, f32, f64)
	fmt.Printf("bool=%v  string=%q  byte=%c(%d)  rune=%c(%d)\n", boo, str, by, by, ru, ru)

	fmt.Println("\n===== 3. fmt 常用占位符 =====")
	// 表格见 Hub/Go基础语法笔记.md
	fmt.Printf("%%c  字符       : %c\n", 'A')
	fmt.Printf("%%T  动态类型   : %T\n", str)
	fmt.Printf("%%v  原值       : %v\n", str)
	fmt.Printf("%%+v 字段+值    : %+v\n", struct{ Name string }{Name: "x"})
	fmt.Printf("%%d  十进制     : %d\n", 255)
	fmt.Printf("%%p  指针       : %p\n", ptr)
	fmt.Printf("%%f  浮点       : %f\n", 3.14)
	fmt.Printf("%%b  二进制     : %b\n", 10)
	fmt.Printf("%%s  字符串     : %s\n", "hi")
	fmt.Printf("%%q  加引号     : %q (string) / %q (rune)\n", "abc", 'X')
	fmt.Printf("%%x  十六进制   : %x\n", 255)

	fmt.Println("\n===== 4. 类型转换 =====")
	// Go 不做隐式转换，必须显式 cast
	var f float64 = 3.14
	var n int = int(f) // 浮点转 int 截断小数
	fmt.Printf("float64(3.14) → int : %d\n", n)

	var s = string(rune('A')) // rune → string
	fmt.Printf("rune('A') → string  : %q\n", s)

	fmt.Println("\n===== 5. 常量 =====")
	fmt.Printf("const Pi        : %v\n", Pi)
	fmt.Printf("const Greeting  : %q\n", Greeting)
	fmt.Printf("HTTP Status OK  : %d\n", StatusOK)

	fmt.Println("\n===== 6. 流程控制 =====")
	// if
	if n := 10; n > 5 {
		fmt.Println("if: n > 5")
	}

	// for（Go 只有 for，没有 while）
	for i := 0; i < 3; i++ {
		fmt.Printf("for: i=%d\n", i)
	}

	// for range
	strs := []string{"a", "b", "c"}
	for i, v := range strs {
		fmt.Printf("range: i=%d v=%q\n", i, v)
	}

	// switch（自动 break，无需手写）
	switch 2 {
	case 1:
		fmt.Println("one")
	case 2:
		fmt.Println("two (no break needed)")
	default:
		fmt.Println("other")
	}
}
