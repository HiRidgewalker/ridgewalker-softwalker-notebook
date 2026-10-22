// 02_composite: Go 复合类型
//
// 涵盖：
//   - 数组（定长，少用）
//   - 切片（动态数组：声明/make/append/copy/range）
//   - map（声明/增删改查/遍历）
//   - 指针（&取址、*解引用、new）
//   - 类型别名（type X = T）vs 新类型（type X T）
//
// 运行：go run main.go
package main

import "fmt"

func main() {
	fmt.Println("===== 1. 数组（定长，少用）=====")
	// 长度是类型的一部分，[3]int 和 [4]int 是不同类型
	var arr1 [3]int = [3]int{1, 2, 3}
	arr2 := [...]int{1, 2, 3, 4} // ... 让编译器算长度
	arr3 := [5]int{2: 99}        // 给索引 2 赋值，其余为 0
	fmt.Printf("arr1=%v arr2=%v arr3=%v\n", arr1, arr2, arr3)

	// 多维数组
	var grid [2][3]int
	grid[0][1] = 5
	fmt.Printf("grid=%v\n", grid)

	fmt.Println("\n===== 2. 切片（slice，动态数组，常用）=====")
	// 2.1 直接声明
	s1 := []int{1, 2, 3}
	fmt.Printf("s1=%v len=%d cap=%d\n", s1, len(s1), cap(s1))

	// 2.2 make 构造：make([]T, len, cap)
	s2 := make([]int, 3, 5)
	fmt.Printf("s2=%v len=%d cap=%d\n", s2, len(s2), cap(s2))

	// 2.3 切片截取（左闭右开）
	s3 := []int{0, 1, 2, 3, 4, 5}
	fmt.Printf("s3[1:4]=%v  s3[:3]=%v  s3[3:]=%v  s3[:]=%v\n", s3[1:4], s3[:3], s3[4:], s3[:])

	// 2.4 append 添加元素（可能扩容，返回新切片）
	s1 = append(s1, 4, 5)
	fmt.Printf("s1 append 后=%v\n", s1)

	// 2.5 copy 复制（按 min(dst, src) 个数复制）
	dst := make([]int, 3)
	src := []int{10, 20, 30, 40}
	n := copy(dst, src)
	fmt.Printf("copy dst=%v, copied %d\n", dst, n)

	fmt.Println("\n===== 3. map（键值对）=====")
	// 3.1 声明（nil map 不能写）
	var m1 map[string]int                       // nil
	m2 := map[string]int{"a": 1, "b": 2}        // 字面量
	m3 := make(map[string]int, 4)               // make
	fmt.Printf("m1=%v m2=%v m3=%v\n", m1, m2, m3)

	// 3.2 增删改查
	m3["x"] = 100
	m3["y"] = 200
	m3["x"] = 999 // 改
	v, ok := m3["x"]
	fmt.Printf("m3[x]=%d ok=%v\n", v, ok)
	delete(m3, "y")
	fmt.Printf("m3 删除 y 后=%v\n", m3)

	// 3.3 遍历（map 顺序不固定）
	for k, v := range m2 {
		fmt.Printf("range: k=%q v=%d\n", k, v)
	}

	fmt.Println("\n===== 4. 指针 =====")
	x := 42
	p := &x // 取址，p 是 *int
	fmt.Printf("x=%d  &x=%p  p=%p  *p=%d\n", x, &x, p, *p)
	*p = 100 // 通过指针改值
	fmt.Printf("改 *p 后 x=%d\n", x)

	// new 返回指向零值的指针
	p2 := new(string)
	*p2 = "hi"
	fmt.Printf("new(string) → *p2=%q\n", *p2)

	fmt.Println("\n===== 5. 类型别名 vs 新类型 =====")
	// 类型别名：完全等价于原类型
	type IntAlias = int
	var ai IntAlias = 10
	var bi int = ai // 不需要转换
	fmt.Printf("IntAlias 与 int 等价: ai=%d bi=%d 类型 %T == %T\n", ai, bi, ai, bi)

	// 新类型：与原类型不兼容，必须显式转换
	type NewInt int
	var ni NewInt = 20
	// var ii int = ni  // ❌ 编译错误：cannot use ni (variable of type NewInt) as int
	var ii int = int(ni) // ✅ 必须 cast
	fmt.Printf("NewInt 不等价于 int: ni=%d ii=%d 类型 %T vs %T\n", ni, ii, ni, ii)
}
