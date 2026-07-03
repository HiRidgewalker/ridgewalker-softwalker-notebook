// 03_functions: Go 函数与方法（不含 method，method 见 04_oop）
//
// 涵盖：
//   - 函数定义（参数类型合并、多返回值、命名返回值）
//   - 形参：值传递 / 指针传递 / 不定参数
//   - 函数作为值 / 匿名函数 / 闭包
//   - defer（栈、参数预求值、典型用法）
//   - panic + recover 错误处理
//
// 运行：go run main.go
package main

import "fmt"

// ========== 1. 函数定义 ==========

// 同类型相邻参数可合并
func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}

// 多返回值（必须用括号）
func div(a, b int) (int, int) {
	return a / b, a % b
}

// 命名返回值：默认零值，return 隐式返回
func f1() (names []string, m map[string]int, num int) {
	m = make(map[string]int)
	m["k1"] = 2
	// 直接 return，不带值 → 返回命名返回值的当前值
	return
}

// ========== 2. 不定参数 ==========

// args ...int 表示 0 或多个 int
func sum(prefix string, args ...int) int {
	total := 0
	for _, v := range args {
		total += v
	}
	fmt.Printf("  %s=%d (len=%d)\n", prefix, total, len(args))
	return total
}

// ========== 3. 指针参数（用于修改原值 / 避免大结构拷贝）==========

func swap(x, y *int) {
	*x, *y = *y, *x
}

// ========== 4. 函数作为值（函数式编程基础）==========

type Handler func(int) int

func apply(n int, h Handler) int {
	return h(n)
}

func main() {
	fmt.Println("===== 1. 基本函数 =====")
	fmt.Printf("max(3,5)=%d\n", max(3, 5))

	q, r := div(10, 3)
	fmt.Printf("div(10,3) → 商=%d 余=%d\n", q, r)

	fmt.Println("\n===== 2. 命名返回值 =====")
	names, m, n := f1()
	fmt.Printf("f1: names=%v m=%v n=%d\n", names, m, n)

	fmt.Println("\n===== 3. 不定参数 =====")
	sum("0 args")
	sum("1 arg", 10)
	sum("3 args", 1, 2, 3)

	// 把切片展开传给不定参数
	s := []int{1, 2, 3, 4}
	sum("slice spread", s...)

	fmt.Println("\n===== 4. 指针参数：swap =====")
	a, b := 1, 2
	swap(&a, &b)
	fmt.Printf("swap 后 a=%d b=%d\n", a, b)

	fmt.Println("\n===== 5. 函数作为值 / 匿名函数 =====")
	// 具名函数作为值
	double := func(x int) int { return x * 2 }
	fmt.Printf("double(5)=%d\n", apply(5, double))

	// 直接传匿名函数
	fmt.Printf("apply(7, *3)=%d\n", apply(7, func(x int) int { return x * 3 }))

	fmt.Println("\n===== 6. 闭包（捕获外层变量）=====")
	counter := func() func() int {
		i := 0
		return func() int {
			i++
			return i
		}
	}()
	fmt.Printf("闭包计数器: %d %d %d\n", counter(), counter(), counter())

	fmt.Println("\n===== 7. defer（栈 + 参数预求值）=====")
	// defer 先进后出（LIFO）
	deferOrder()

	// defer 的参数在 defer 那一行就求值了
	x := 1
	defer fmt.Printf("defer 拿到的 x=%d（声明时就求值）\n", x)
	x = 99
	fmt.Printf("实际 x=%d\n", x)

	fmt.Println("\n===== 8. panic + recover（异常捕获）=====")
	safeCall(func() {
		fmt.Println("正常调用")
	})
	safeCall(func() {
		panic("oops!")
	})
	fmt.Println("主流程没被 panic 打断 ✓")

	fmt.Println("\n===== 9. defer 典型用法：资源清理 =====")
	readFileSim()
}

// deferOrder 演示 defer 的 LIFO 顺序
func deferOrder() {
	fmt.Println("  defer order:")
	for i := 1; i <= 3; i++ {
		defer fmt.Printf("    defer #%d\n", i)
	}
}

// safeCall 把 panic 转成普通错误处理
func safeCall(fn func()) {
	defer func() {
		if r := recover(); r != nil {
			fmt.Printf("  [recovered] %v\n", r)
		}
	}()
	fn()
}

// readFileSim 模拟 defer 关文件 / 释放锁的典型用法
func readFileSim() {
	fmt.Println("  模拟 readFile：")
	// 实际代码：f, err := os.Open(...)
	// 习惯写法：成功打开后立刻 defer f.Close()
	fmt.Println("    open file")
	defer fmt.Println("    [defer] close file")
	fmt.Println("    read file ...")
	// panic("中间出错")   // 即便这里 panic，defer 也会执行
}
