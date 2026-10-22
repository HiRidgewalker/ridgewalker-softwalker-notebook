// 04_oop: Go 的"面向对象"——struct / method / interface / embedding
//
// Go 没有 class，用 struct + method 实现数据 + 行为；
// 用 interface 实现多态；用 embedding（嵌入）实现代码复用，
// 体验上类似继承但不是继承。
//
// 涵盖：
//   - struct 定义、6 种实例化方式
//   - 匿名字段（嵌入）实现"继承"
//   - 方法：值接收器 vs 指针接收器
//   - interface 定义与实现（鸭子类型）
//   - 多接口 / 多类型 / 空接口 / 类型断言
//
// 运行：go run main.go
package main

import "fmt"

// ========== 1. struct 定义 ==========

type Person struct {
	Name string
	Age  int
	City string
}

// 嵌入（匿名字段）—— 类似"继承"
type Employee struct {
	Person     // 匿名字段：Employee 自动拥有 Name/Age/City 字段
	Salary int
	Dept   string
}

// ========== 2. 方法（值/指针接收器）==========

// 值接收器：不会修改原对象
func (p Person) Greet() string {
	return fmt.Sprintf("Hi, I'm %s from %s", p.Name, p.City)
}

// 指针接收器：可以修改原对象（更常见，因为经常要改）
func (p *Person) HaveBirthday() {
	p.Age++
}

// 为自定义类型（非 struct）加方法
type MyFloat float64

func (f MyFloat) Abs() float64 {
	if f < 0 {
		return float64(-f)
	}
	return float64(f)
}

// ========== 3. interface 定义与实现 ==========

// 任何实现了 Speak() string 的类型，都"自动"实现了 Speaker 接口
type Speaker interface {
	Speak() string
}

// 多个方法组成接口
type Mover interface {
	Move() string
	Speed() float64
}

// ========== 4. 实现接口的具体类型 ==========

type Dog struct {
	Name string
}

func (d Dog) Speak() string { return fmt.Sprintf("%s: 汪汪汪", d.Name) }
func (d Dog) Move() string  { return "四只脚跑" }
func (d Dog) Speed() float64 { return 30.0 }

type Cat struct {
	Name string
}

func (c Cat) Speak() string { return fmt.Sprintf("%s: 喵喵喵", c.Name) }
func (c Cat) Move() string  { return "悄无声息" }
func (c Cat) Speed() float64 { return 15.0 }

// 实现了 Speaker 但没实现 Mover
type Radio struct{}

func (Radio) Speak() string { return "📻 正在播报新闻" }

func main() {
	fmt.Println("===== 1. struct 实例化（6 种方式）=====")
	// 方式 1：零值
	var p1 Person
	// 方式 2：字面量（按字段顺序）
	p2 := Person{"张三", 25, "北京"}
	// 方式 3：字面量（指定字段名，推荐）
	p3 := Person{Name: "李四", Age: 30}
	// 方式 4：取指针
	p4 := &Person{Name: "王五", City: "上海"}
	// 方式 5：new
	p5 := new(Person)
	p5.Name = "赵六"
	// 方式 6：构造函数（自己写）
	p6 := NewPerson("周八", 40, "广州")

	fmt.Printf("p1=%+v\n", p1)
	fmt.Printf("p2=%+v\n", p2)
	fmt.Printf("p3=%+v\n", p3)
	fmt.Printf("p4=%+v\n", p4)
	fmt.Printf("p5=%+v\n", p5)
	fmt.Printf("p6=%+v\n", p6)

	fmt.Println("\n===== 2. 方法（值/指针接收器）=====")
	fmt.Println(p2.Greet())
	p2.HaveBirthday() // 即使 p2 是值类型，方法也是改得到的
	fmt.Printf("p2 生日后 Age=%d\n", p2.Age)

	f := MyFloat(-3.14)
	fmt.Printf("MyFloat(-3.14).Abs()=%v\n", f.Abs())

	fmt.Println("\n===== 3. 嵌入（匿名字段）=====")
	e := Employee{
		Person: Person{Name: "钱七", Age: 28, City: "深圳"},
		Salary: 30000,
		Dept:   "后端",
	}
	// 字段提升：e.Name 等价于 e.Person.Name
	fmt.Printf("e.Name=%s e.City=%s e.Salary=%d\n", e.Name, e.City, e.Salary)
	// 嵌入字段的方法也被提升
	fmt.Println("e.Greet() =", e.Greet())

	fmt.Println("\n===== 4. interface 多态 =====")
	dog := Dog{Name: "旺财"}
	cat := Cat{Name: "小花"}
	radio := Radio{}

	// 不同类型都实现 Speaker，可以放进同一个 slice
	speakers := []Speaker{dog, cat, radio}
	for _, s := range speakers {
		fmt.Println("  ", s.Speak())
	}

	// 没实现 Mover 的 Radio 不能放进 Mover slice
	movers := []Mover{dog, cat}
	for _, m := range movers {
		fmt.Printf("    %s, 速度 %.1f\n", m.Move(), m.Speed())
	}

	fmt.Println("\n===== 5. 空接口 + 类型断言 =====")
	// 空接口 interface{} 可以存任意类型
	var anything interface{} = "hello"
	fmt.Printf("anything=%v 类型 %T\n", anything, anything)

	// 类型断言（不安全版本）
	s, ok := anything.(string)
	if ok {
		fmt.Printf("  断言为 string: %q\n", s)
	}

	// type switch：处理多种可能类型
	describe := func(v interface{}) string {
		switch x := v.(type) {
		case int:
			return fmt.Sprintf("int %d", x)
		case string:
			return fmt.Sprintf("string %q", x)
		case Speaker:
			return fmt.Sprintf("Speaker 说话: %s", x.Speak())
		default:
			return fmt.Sprintf("未知类型 %T", x)
		}
	}
	fmt.Println("  ", describe(42))
	fmt.Println("  ", describe("hi"))
	fmt.Println("  ", describe(dog))
	fmt.Println("  ", describe(3.14))
}

// 构造函数（约定俗成：返回指针）
func NewPerson(name string, age int, city string) *Person {
	return &Person{Name: name, Age: age, City: city}
}
