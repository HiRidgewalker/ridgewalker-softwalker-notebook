// 05_packages: Go 包管理与常用标准库
//
// 涵盖：
//   - import 的 4 种写法（普通、别名、点导入、匿名）
//   - init() 函数
//   - 常用标准库：fmt / strings / strconv / time / errors
//   - 错误处理：error 接口、errors.New / fmt.Errorf
//   - 常见坑：包级变量循环依赖、init 顺序
//
// 运行：go run main.go
package main

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
	"time"
)

// ========== 1. import 别名示例 ==========
// 真实工程里常用：import f "fmt" 这种，f.Println(...)
// 本 demo 不实际演示，重点看 main 里的 import 块

// ========== 2. 错误处理 ==========

// 自定义 error
var ErrDivideByZero = errors.New("division by zero")

func safeDiv(a, b int) (int, error) {
	if b == 0 {
		return 0, ErrDivideByZero
	}
	return a / b, nil
}

// 包装错误（Go 1.13+）
func parsePort(s string) (int, error) {
	p, err := strconv.Atoi(s)
	if err != nil {
		return 0, fmt.Errorf("解析端口失败: %w", err)
	}
	if p < 1 || p > 65535 {
		return 0, fmt.Errorf("端口超出范围 [1, 65535]: %d", p)
	}
	return p, nil
}

// ========== 3. init() 函数 ==========
//
// init 在 main 之前自动执行，每个文件可以有多个，
// 同一个包内按文件名字母序执行。
// 常用于：注册驱动、初始化全局配置、读配置文件等。

var startTime time.Time

func init() {
	startTime = time.Now()
	fmt.Println("[init] 包初始化完成")
}

func main() {
	fmt.Println("===== 1. strings 常用函数 =====")
	s := "Hello, Go World"
	fmt.Printf("Contains('Go')=%v\n", strings.Contains(s, "Go"))
	fmt.Printf("HasPrefix('Hello')=%v\n", strings.HasPrefix(s, "Hello"))
	fmt.Printf("ToUpper=%q  ToLower=%q\n", strings.ToUpper(s), strings.ToLower(s))
	fmt.Printf("Split by space=%v\n", strings.Split(s, " "))
	fmt.Printf("Replace 'o'->'0' n=2=%q\n", strings.Replace(s, "o", "0", 2))
	fmt.Printf("TrimSpace 前后去空格=%q\n", strings.TrimSpace("  hi  "))
	fmt.Printf("Join=%q\n", strings.Join([]string{"a", "b", "c"}, "-"))

	fmt.Println("\n===== 2. strconv 类型转换 =====")
	// 数字 → 字符串
	n := 42
	sn := strconv.Itoa(n)
	fmt.Printf("Itoa(42)=%q\n", sn)

	// 字符串 → 数字（失败返回 error）
	if v, err := strconv.Atoi("123"); err == nil {
		fmt.Printf("Atoi(\"123\")=%d\n", v)
	}

	// int ↔ string 进制转换
	fmt.Printf("FormatInt(255, 16)=%q  FormatInt(255, 2)=%q\n",
		strconv.FormatInt(255, 16), strconv.FormatInt(255, 2))

	// 浮点格式化（保留 2 位）
	fmt.Printf("FormatFloat(3.14159, 'f', 2, 64)=%q\n",
		strconv.FormatFloat(3.14159, 'f', 2, 64))

	// bool
	fmt.Printf("FormatBool=%q  ParseBool=%v\n",
		strconv.FormatBool(true), mustParseBool("true"))

	fmt.Println("\n===== 3. time 时间处理 =====")
	now := time.Now()
	fmt.Printf("now=%v\n", now)
	fmt.Printf("now.Format(2006-01-02 15:04:05)=%s\n",
		now.Format("2006-01-02 15:04:05")) // Go 的"参考时间"是固定的 Mon Jan 2 15:04:05 MST 2006

	// 时长计算
	d := 2*time.Hour + 30*time.Minute
	fmt.Printf("2h30m 转换成分钟=%v\n", d.Minutes())

	// 解析时间
	t, _ := time.Parse("2006-01-02", "2026-06-14")
	fmt.Printf("parse 2026-06-14=%v\n", t)

	// 距启动时长
	fmt.Printf("距包初始化 %.3f ms\n", time.Since(startTime).Seconds()*1000)

	fmt.Println("\n===== 4. error 处理 =====")
	// 普通 error
	if v, err := safeDiv(10, 0); err != nil {
		fmt.Printf("  safeDiv 失败: %v\n", err)
	} else {
		fmt.Printf("  safeDiv 成功: %d\n", v)
	}

	// 错误包装 + 解包
	if _, err := parsePort("abc"); err != nil {
		fmt.Printf("  parsePort 失败: %v\n", err)
		// errors.Is 检查是否是某个特定 error
		// errors.Unwrap 拿到包装的底层 error
	}

	fmt.Println("\n===== 5. 常见坑：包级变量初始化顺序 =====")
	fmt.Printf("  configValue=%q（init 顺序：常量 → var → init → main）\n", configValue)
}

var configValue = loadConfig()

func loadConfig() string {
	return "from var"
}

func mustParseBool(s string) bool {
	v, _ := strconv.ParseBool(s)
	return v
}
