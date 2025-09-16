> [!note]
> go语言语法学习笔记

## go语言的变量类型
- bool
- string
- 有符号整数类型
	- int  随系统，一般占4个字节
	- int8  占用1个字节
	- int16  占用2个字节
	- int32  占用4个字节
	- int64  占用8个字节
- 无符号整数
	- uint8
	- uint16
	- uint32
	- uint64
	- uintptr  无符号整型， 用于存放一个指针
- byte  uint8的别名
- rune  int32的别名 代表一个unicode码
- 浮点数
	- float32
	- float64
- 复数
	- complex64
	- complex128

> [!info]- unicode和ascii的异同 
> 1. ASCII 只支持 128 个字符，而 Unicode 覆盖了全球所有语言的字符。  
> 
> 2. Unicode 的前 128 个字符与 ASCII 完全相同，确保了向后兼容。  
> 
> 3. UTF-8 编码方式使得 ASCII 字符在 Unicode 环境下仍然能用 1 字节表示，保持兼容性。

### go语言的变量类型详解
#### 整形
- Go语言同时提供了有符号和无符号的整数类型。
- 有符号整型: int、int8、int64、int32、int64
- 无符号整型: uint、uint8、uint64、uint32、uint64、uintptr
- 有符号整型范围：$-2^{(n-1)}$ 到 $2^{(n-1)-1}$
- 无符号整型范围: 0 到 $2^{n-1}$
- 在二进制传输、读写文件的结构描述时，为了保持文件的结构不会受到不同编译目标平台字节长度的影响，不要使用 int 和 uint

#### 浮点数
**Go语言支持两种浮点型数**
- `float32` :范围 约1.4e-45 到 约3.4e38
- `float64` :范围约4.9e-324 到 约1.8e308
[示例代码](https://github.com/hyd1128/study-go-project/blob/master/go-basic-02/02_%E6%B5%AE%E7%82%B9%E5%9E%8B(float).go)

#### 布尔
- var 变量名 bool
- `==`,`>`,`<`，`<=`, `>=`,`&&(AND)`,`||(OR)`等都会产生bool值
- Go语言对于值之间的比较有非常严格的限制，只有两个相同类型的值才可以进行比较, 如果值的类型是接口（interface），那么它们也必须都实现了相同的接口。
- 如果其中一个值是`常量`，那么另外一个值可以不是常量，但是类型必须和该常量类型相同。
- 如果以上条件都不满足，则必须将其中一个值的类型转换为和另外一个值的类型相同之后才可以进行比较。
- `&&(AND)`,`||(OR)`是具有短路行为的，如果运算符左边的值已经可以确定整个布尔表达式的值，那么运算符右边的值将不再被求值。(&&优先级高于||)
[示例代码](https://github.com/hyd1128/study-go-project/blob/master/go-basic-02/03_%E5%B8%83%E5%B0%94%E7%B1%BB%E5%9E%8B(bool).go)

#### 字符串
- `字符串是一种值类型，且值不可变，即创建某个文本后将无法再次修改这个文本的内容。`
- `当字符为 ASCII 码表上的字符时则占用 1 个字节`
```go
// 使用单引号 表示一个字符  
// var ch byte = 'A'  
// 在 ASCII 码表中，A 的值是 65,也可以这么定义  
// var ch byte = 65  
// 65使用十六进制表示是41，所以也可以这么定义 \x 总是紧跟着长度为 2 的 16 进制数  
// var ch byte = '\x41'  
// 65的八进制表示是101，所以使用八进制定义 \后面紧跟着长度为 3 的八进制数  
// var ch byte = '\101'  
// fmt.Printf("%c", ch)
var ch rune = '\u0041'  
var ch1 int64 = '\U00000041'  
// 格式化说明符%c用于表示字符，%v或%d会输出用于表示该字符的整数，%U输出格式为 U+hhhh 的字符串。  
fmt.Printf("%c,%c,%U", ch, ch1, ch)
```
**示例代码链接**
[字符类型](https://github.com/hyd1128/study-go-project/blob/master/go-basic-02/04_%E5%AD%97%E7%AC%A6%E7%B1%BB%E5%9E%8B(string).go)
[字符串类型](https://github.com/hyd1128/study-go-project/blob/master/go-basic-02/05_%E5%AD%97%E7%AC%A6%E4%B8%B2%E7%B1%BB%E5%9E%8B(string).go)
[字符串的应用](https://github.com/hyd1128/study-go-project/blob/master/go-basic-02/06_%E5%AD%97%E7%AC%A6%E4%B8%B2%E7%9A%84%E5%BA%94%E7%94%A8.go)
[字符串格式化](https://github.com/hyd1128/study-go-project/tree/master/go-basic-02)
[字符串查找](https://github.com/hyd1128/study-go-project/blob/master/go-basic-02/08_%E5%AD%97%E7%AC%A6%E4%B8%B2%E6%9F%A5%E6%89%BE.go)

#### 类型转换
- 类型转换只能在定义正确的情况下转换成功，例如从一个取值范围较小的类型转换到一个取值范围较大的类型（将 int16 转换为 int32）。
- 当从一个取值范围较大的类型转换到取值范围较小的类型时（将 int32 转换为int16 或将 float32 转换为 int），会发生`精度丢失`的情况。
- 只有相同底层类型的变量之间可以进行相互转换（如将 int16 类型转换成 int32 类型）, 不同底层类型的变量相互转换时会引发编译错误（如将 bool 类型转换为 int 类型）
[示例代码](https://github.com/hyd1128/study-go-project/blob/master/go-basic-02/09_%E7%B1%BB%E5%9E%8B%E8%BD%AC%E6%8D%A2.go)
[类型转换练习](https://github.com/hyd1128/study-go-project/blob/master/go-basic-02/10_%E4%BF%AE%E6%94%B9%E5%AD%97%E7%AC%A6%E4%B8%B2.go)

## go语言变量类型、变量作用域
### go语言有以下几种变量
**匿名变量**
	1. 匿名变量以`_`下划线表示  
	2. 匿名变量不占用命名空间，也不会分配内存。匿名变量可以重复声明使用
	3. `_`本身就是一个特殊的标识符，被称为空白标识符。它可以像其他标识符那样用于变量的声明或赋值（任何类型都可以赋值给它），但任何赋给这个标识符的值都将被抛弃，因此这些值不能在后续的代码中使用, 也不可以使用这个标识符作为变量对其它变量进行赋值或运算。

**全局变量**
	1. 函数外定义的变量称为全局变量
	2. 在函数体外声明的变量称之为`全局变量`，全局变量只需要在`一个源文件中定义`, 就可以在所有源文件中使用，当然，不包含这个全局变量的源文件需要使用import关键字引入全局变量所在的源文件之后才能使用这个全局变量。 
	3. 全局变量声明`必须以 var 关键字开头`，如果想要在外部包中使用全局变量的`首字母必须大写`。

**局部变量**
	1. 函数内定义的变量称为局部变量
	2. 在函数体内声明的变量称之为`局部变量`，它们的作用域`只在函数体内`，函数的参数和返回值变量都属于局部变量。
	3.  局部变量不是一直存在的，它只在定义它的函数被调用后存在，函数调用结束后这个局部变量就会被销毁。
	4. Go语言程序中全局变量与局部变量名称可以相同，但是函数体内的局部变量会被优先考虑。

**形式变量**
	1. 函数中定义的变量称为形式变量
	2. 在定义函数时函数名后面括号中的变量叫做`形式参数`（简称形参）。形式参数只在函数调用时才会生效，函数调用结束后就会被销毁，在函数未被调用时，函数的形参`并不占用实际的存储单元`，也没有实际值。
	3. 形式参数会作为`函数的局部变量来使用`。

## go语言的变量声明
[示例代码](https://github.com/hyd1128/study-go-project/blob/master/go-basic-01/02_%E5%8F%98%E9%87%8F%E5%A3%B0%E6%98%8E.go)

## fmt库类型表达占位符
```go
/*  
       %c  单一字符  
       %T  动态类型  
       %v  本来值的输出  
       %+v 字段名+值打印  
       %d  十进制打印数字  
       %p  指针，十六进制  
       %f  浮点数  
       %b  二进制  
       %s  string
*/
```

## 指针
1. 一个指针变量可以指向任何一个值的内存地址，它所指向的值的内存地址在 32 和 64 位 机器上分别占用 4 或 8 个字节，占用字节的大小与所指向的值的大小无关。
2. 当一个指针被定义后`没有分配到任何变量`时，它的默认值为 `nil`。
3. Go语言中使用在变量名前面添加`&`操作符（前缀）来获取变量的内存地址（取地址操作）
4. 其中 v 代表被取地址的变量，变量 v 的地址使用变量 ptr 进行接收，ptr 的类型为`*T`，称做 T 的指针类型，`*`代表指针。`ptr := &v`,  v 的类型为 T
5. 取地址操作符`&`和取值操作符`*`是一对互补操作符，`&`取出地址，`*`根据地址取出地址指向的值
6. 变量、指针地址、指针变量、取地址、取值的相互关系和特性如下：
	1. 对变量进行取地址操作使用`&`操作符，可以获得这个变量的指针变量。
	2.  指针变量的值是指针地址。
	3. 对指针变量进行取值操作使用`*`操作符，可以获得指针变量指向的原变量的值。
```go
var room int = 10  
var ptr = &room  
fmt.Printf("%p \n", &room)  
fmt.Printf("%T, %p \n", ptr, ptr)  
fmt.Println("指针地址:", ptr)  
fmt.Println("指针地址代表的值:", *ptr)

/*
0xc00000a0c8 
*int, 0xc00000a0c8
指针地址: 0xc00000a0c8
指针地址代表的值: 10
*/
```

### 通过new方法创建指针
```go
func main() {  
    str := new(string)  
    *str = "学习go语言"  
    fmt.Println(*str)  
    fmt.Printf("指针类型: %T, 指针值: %s, 指针指向变量的地址值: %p", str, *str, str)  
  
}

/*
学习go语言
指针类型: *string, 指针值: 学习go语言, 指针指向变量的地址值: 0xc000026070
*/
```

## 类型别名和定义新类型
### 类型别名
```go
var IntAlise = int // 类型别名
```
### 新类型
```go
type NewInt int // 新类型
```
相关代码
```go
/*  
类型别名是 Go 1.9 版本添加的新功能，主要用于解决代码升级、迁移中存在的类型兼容性问题。  
*/  
  
// 将NewInt定义为int类型  
type NewInt int  
  
// 将int取一个别名叫IntAlias  
type IntAlias = int  
  
// 将a声明为NewInt类型  
var a NewInt  
  
func main() {  
    /*  
       类型别名:  
          type TypeAlias = Type       类型定义:  
          定义Name为Type类型 ,定义之后 Name为一种新的类型  
          type Name Type    */  
    // 查看a的类型名 main.NewInt    fmt.Printf("a type: %T\n", a)  
    // 将a2声明为IntAlias类型  
    var a2 IntAlias  
    // 查看a2的类型名 int    // IntAlias 类型只会在代码中存在，编译完成时，不会有 IntAlias 类型。  
    fmt.Printf("a2 type: %T\n", a2)  
  
}

/*
a type: main.NewInt
a2 type: int 

*/
```

## 数组
1. 数组是一个由固定长度的特定类型元素组成的序列，一个数组可以由零个或多个元素组成。
2. 因为数组的长度是固定的，所以在Go语言中很少直接使用数组。
3. 定义数组: `var 数组变量名 [元素数量]Type`

### 给数组赋值的示例参考
```go
import (  
    "fmt"  
)  
  
func main() {  
    // 初始化的时候赋值  
    var arr [3]int = [3]int{1, 2, 3}  
    fmt.Println(arr)  
  
    // 如果第三个赋值,则为默认值  
    var arr1 [3]int = [3]int{1, 2}  
    fmt.Println(arr1)  
  
    // 简单声明  
    arr2 := [3]int{1, 2, 3}  
    fmt.Println(arr2)  
  
    // 不写数据数量, 而使用..., 表示数组的长度是更具初始化值的个数来计算的  
    arr3 := [...]int{1, 3, 4}  
    fmt.Println(arr3)  
    // 一定要注意，数组是定长的，不可更改，在编译阶段就决定了  
  
    // 只想给第三个值赋值,其余的值为默认值  
    arr4 := [3]int{2: 3}  
    for index, value := range arr4 {  
       fmt.Printf("索引值: %d, 值: %d", index, value)  
    }  
}
```
### 数组比较的一些规则
```go
import "fmt"  
  
func main() {  
    /*  
       如果两个数组类型相同（包括数组的长度，数组中元素的类型）的情况下，  
       我们可以直接通过较运算符（`==`和`!=`）来判断两个数组是否相等，  
       只有当两个数组的所有元素都是相等的时候数组才是相等的，不能比较两个类型不同的数组，       否则程序将无法完成编译。  
    */  
    a := [2]int{1, 2}  
    b := [...]int{1, 2}  
    c := [2]int{1, 3}  
  
    fmt.Println(a == b, b == c, c == a)  
    // d := [3]int{1, 2}  
    // fmt.Println(a == d) // 编译错误：无法比较 [2]int == [3]int  
}
```
### 多维数组定义
```go
import (  
    "fmt"  
)  
  
func main() {  
    /*  
       array_name 为数组的名字，array_type 为数组的类型，size1、size2 等等为数组每一维度的长度。  
       var array_name [size1][size2]...[sizen] array_type    */    // 声明一个二维数组  
    var arr1 [4][2]int  
    fmt.Println(arr1)  
  
    // 使用数组字面量声明并初始化一个二维整形数组  
    arr2 := [4][2]int{{1, 2}, {3, 4}, {5, 6}, {7, 8}}  
    fmt.Println(arr2)  
  
    // 声明并初始化数组中索引为1和3的元素  
    arr3 := [4][2]int{1: {1, 2}, 3: {3, 4}}  
    fmt.Println(arr3)  
  
    // 取值  
    fmt.Println(arr3[1][0])  
  
    // 循环取值  
    for index, value := range arr3 {  
       fmt.Printf("index: %d, value: %d\n", index, value)  
    }  
}
```
## 切片
### 切片语法
```go
slice [开始位置 : 结束位置]  
    语法说明如下：  
    - slice：表示目标切片对象；  
    - 开始位置：对应目标切片对象的索引；  
    - 结束位置：对应目标切片的结束索引。
```

从数组或切片生成新的切片拥有如下的特性:
- 取出的元素数量为：结束位置 - 开始位置；
- 取出元素不包含结束位置对应的索引，切片最后一个元素使用 `slice[len(slice)-1]` 获取；
- 当缺省开始位置时，表示从连续区域开头到结束位置`(a[:2])`；
- 缺省结束位置时，表示从开始位置到整个连续区域末尾`(a[0:])`；
- 两者同时缺省时，与切片本身等效`(a[:])`；
- 两者同时为 0 时，等效于空切片，一般用于切片复位`(a[0:0])`。

### 声明切片
[示例链接](https://github.com/hyd1128/study-go-project/blob/master/go-basic-04/06_%E7%9B%B4%E6%8E%A5%E5%A3%B0%E6%98%8E%E6%96%B0%E7%9A%84%E5%88%87%E7%89%87.go)

#### 通`append`向切片中添加元素
```go
var strListOne []string  
// 追加一个元素  
strListOne = append(strListOne, "go教程")  
fmt.Println(strListOne)
```

#### 使用make函数构造切片
```go
func main() {  
    // 如果需要动态地创建一个切片，可以使用 make() 内建函数，格式如下：  
    // make( []Type, size, cap )  
    // Type` 是指切片的元素类型，`size` 指的是为这个类型分配多少个元素，`cap `为预分配的元素数量，  
    // 这个值设定后不影响 size，只是能提前分配空间，`降低多次分配空间造成的性能问题`。  
  
    a := make([]int, 2)  
    b := make([]int, 2, 10)  
    fmt.Println(len(a), cap(a))  
    fmt.Println(len(b), cap(b))  
    fmt.Println(a, b)  
    fmt.Println(len(a), len(b))  
  
}
```

### 切片复制 go语言内置的`copy`函数
```go
func main() {  
    /*  
       copy( destSlice, srcSlice []T) int    */  
    slice1 := []int{1, 2, 3, 4, 5}  
    slice2 := []int{5, 4, 3}  
    // copy(slice2, slice1) // 只会复制slice1的前3个元素到slice2中  
    copy(slice1, slice2) // 只会复制slice2的3个元素到slice1的前3个位置  
    // fmt.Println(result1)  
    // fmt.Println(result2)    fmt.Println(slice1)  
    fmt.Println(slice2)  
    /*  
       Go语言的内置函数 copy() 可以将一个数组切片复制到另一个数组切片中，如果加入的两个数组切片不一样大，  
       就会按照其中较小的那个数组切片的元素个数进行复制。  
       其中 `srcSlice `为数据来源切片，`destSlice `为复制的目标（也就是将 srcSlice 复制到 destSlice），  
       `目标切片必须分配过空间且足够承载复制的元素个数`，并且来源和目标的`类型必须一致`，copy() 函数的返回值表示实际发生复制的元素个数。  
    */  
}
```
#### 切片复制续
[示例链接](https://github.com/hyd1128/study-go-project/blob/master/go-basic-04/10_%E5%88%87%E7%89%87%E5%A4%8D%E5%88%B6%E7%BB%AD.go)

## 切片和数组总结
[示例链接](https://github.com/hyd1128/study-go-project/blob/master/go-basic-04/11_%E6%95%B0%E7%BB%84%E5%92%8C%E5%88%87%E7%89%87%E6%80%BB%E7%BB%93.go)




## 函数
### 函数定义
```go
func main() {  
    fmt.Println(max(1, 10))  
    fmt.Println(max(-1, -2))  
  
    fmt.Println(test(1, 2, "123"))  
  
    x, y := testTwo(1, 2, "abc")  
    fmt.Println(x, y)  
}  
  
// 类型相同的相邻参数，参数类型可合并。  
func max(n1, n2 int) int {  
    if n1 > n2 {  
       return n1  
    }  
    return n2  
}  
  
/*  
**Go语言是编译型语言，所以函数编写的顺序是无关紧要的，鉴于可读性的需求，  
最好把 main() 函数写在文件的前面，其他函数按照一定逻辑顺序进行编写（例如函数被调用的顺序）。**  
*/  
  
func test(x, y int, s string) (int, string) {  
    // 类型相同的相邻参数，参数类型可合并。 多返回值必须用括号。  
    n := x + y  
    return n, fmt.Sprintf(s, n)  
}  
  
func testTwo(x, y int, z string) (int, string) {  
    resultX := x + y  
    resultY := z  
    return resultX, resultY  
}
```
### 使用函数作为形参
```go
func testOne(fn func() int) int {  
// 注意: 将函数作为形参还需要填写函数的入参类型和出参类型
    return fn()  
}  
func fn() int {  
    return 200  
}  
func main() {  
    // 这是直接使用匿名函数  
    // s1 := testOne(func() int { return 100 })  
    // 这是传入一个函数  
    s1 := testOne(fn)  
    fmt.Println(s1)  
}
```
### 命名返回值
```go
import "fmt"  
  
// 支持返回值 命名 ，默认值为类型零值,命名返回参数可看做与形参类似的局部变量,由return隐式返回  
// 在return 数据类型的时候已经显示的命名变量了  
func f1() (names []string, m map[string]int, num int) {  
    m = make(map[string]int)  
    m["k1"] = 2  
    return  
}  
  
func main() {  
    a, b, c := f1()  
    fmt.Println(a, b, c)  
}
```
- 支持返回值 命名 ，默认值为类型零值,命名返回参数可看做与形参类似的局部变量,由return隐式返回
- 在return 数据类型的时候已经显示的命名变量了

### 函数参数的互换、不定参数数目传递
```go
package main  
  
import "fmt"  
  
func swap(x, y *int) {  
    *x, *y = *y, *x  
}  
  
func main() {  
    var a, b int = 1, 2  
    /*  
       调用 swap() 函数  
       &a 指向 a 指针, a变量的地址  
       &b 指向 b 指针, b变量的地址  
    */  
    swap(&a, &b)  
    fmt.Println(a, b)  
}  
  
/*  
多参数传递写法格式:  
  func myfunc(args ...int) {    //0个或多个参数  
  }  
  func add(a int, args…int) int {    //1个或多个参数  
  }  
  func add(a int, b int, args…int) int {    //2个或多个参数  
  }*/
```

### 匿名函数
```go
import (  
    "fmt"  
)  
  
// 匿名函数定义格式  
  
/*  
func (参数列表) (返回参数列表) {  
       函数体  
    }*/  
  
// 匿名函数用作回调函数  
// 遍历切片的每一个元素, 通过给定函数进行元素访问  
func visit(list []int, f func(int)) {  
    for _, v := range list {  
       f(v)  
    }  
}  
  
func main() {  
    // // 这里将一个函数当作一个变量一样操作  
    // getSqrt := func(a float64) float64 {  
    //     // 接收一个float64的数字, 并返回这个数字的平方根  
    //     return math.Sqrt(a)  
    // }    //    // fmt.Println(getSqrt(4))  
    // // 直接调用匿名函数  
    // func(data int) {  
    //     fmt.Println("hello", data)    // }(100)  
    // 使用匿名函数打印切片内容  
    visit([]int{1, 2, 3, 4}, func(v int) {  
       fmt.Println(v)  
    })  
  
}
```
在 Go 语言中，**匿名函数（Anonymous Function）**就是**没有名字的函数**，通常用来**临时创建、直接使用或作为值传递**。

**创建多个匿名函数**
[示例代码](https://github.com/hyd1128/study-go-project/blob/master/go-basic-06/08_%E5%88%9B%E5%BB%BA%E5%A4%9A%E4%B8%AA%E5%8C%BF%E5%90%8D%E5%87%BD%E6%95%B0.go)

## defer关键字
```go
import "fmt"  
  
func main() {  
    var whatever = [5]int{1, 2, 3, 4, 5}  
  
    for i := range whatever {  
       fmt.Printf("hello -> %v \n", whatever[i])  
       defer fmt.Println(whatever[i])  
    }  
}

/*
hello -> 1 
hello -> 2 
hello -> 3
hello -> 4
hello -> 5
5
4
3
2
1
*/
```
通过上述可以看到`defer`关键字就是延迟调用,并且当有多个defer的时候就是栈结构，先进后出

典型defer示例
```go

func main() {  
    start := time.Now()  
    log.Printf("开始时间为：%v", start)  
    defer log.Printf("时间差：%v", time.Since(start)) // Now()此时已经copy进去了  
    // 不受这3秒睡眠的影响  
    time.Sleep(3 * time.Second)  
  
    log.Printf("函数结束")  
} 

/*
2025/08/10 14:55:43 开始时间为：2025-08-10 14:55:43.5657826 +0800 CST m=+0.004311601
2025/08/10 14:55:46 函数结束
2025/08/10 14:55:46 时间差：18.9083ms
*/
  
func main() {  
    var whatever = [5]int{1, 2, 3, 4, 5}  
    // go 1.22版本之后for循环的每一个i都是独立的  
    for i, _ := range whatever {  
       // 函数正常执行,由于闭包用到的变量 i 在执行的时候已经变成4,所以输出全都是4.  
       defer func() { fmt.Println(i) }()  
    }  
}

/*
4 3 2 1 0
*/
```

## 异常捕获
```go
package main  
  
func main() {  
    testThree()  
}  
  
func testThree() {  
    defer func() {  
       // 捕获panic异常  
       if err := recover(); err != nil {  
          // 类型断言, 返回的是interface{} 通过变量.(类型)的方式进行断言  
          println(err.(string)) // 将 interface{} 转型为具体类型。  
       }  
    }()  
  
    panic("panic error!")  
}  
  
// import "fmt"  
//  
// func testThree(x, y int) {  
//  var z int  
//  
//  func() {  
//     defer func() {  
//        if recover() != nil {  
//           z = 0  
//        }  
//     }()  
//     panic("test panic")  
//     z = x / y  
//     return  
//  }()  
//  
//  fmt.Printf("x / y = %d\n", z)  
// }  
//  
// func main() {  
//  testThree(2, 1)  
// }  
  
// var ErrDivByZero = errors.New("division by zero")  
//  
// func div(x, y int) (int, error) {  
//  if y == 0 {  
//     return 0, ErrDivByZero  
//  }  
//  return x / y, nil  
// }  
//  
// func main() {  
//  defer func() {  
//     fmt.Println(recover())  
//  }()  
//  switch z, err := div(10, 0); err {  
//  case nil:  
//     println(z)  
//  case ErrDivByZero:  
//     panic(err)  
//  }  
// }  
  
// import "fmt"  
//  
// func Try(fun func(), handler func(interface{})) {  
//  defer func() {  
//     if err := recover(); err != nil {  
//        handler(err)  
//     }  
//  }()  
//  fun()  
// }  
//  
// func main() {  
//  Try(func() {  
//     panic("test panic")  
//  }, func(err interface{}) {  
//     fmt.Println(err)  
//  })  
// }
```

## 结构体
### 结构体定义
```go
import "fmt"  
  
type Point struct {  
    X int  
    Y int  
}  
  
func main() {  
    // 使用.来访问结构体的成员变量,结构体成员变量的赋值方法与普通变量一致。  
    var p Point  
    p.X = 1  
    p.Y = 2  
    fmt.Printf("%v,x=%d,y=%d", p, p.X, p.Y)  
}
```

### 结构体示例
[示例代码](https://github.com/hyd1128/study-go-project/blob/master/go-basic-07/02_%E7%BB%93%E6%9E%84%E4%BD%93%E6%A1%88%E4%BE%8B2.go)

### 匿名结构体
[示例代码](https://github.com/hyd1128/study-go-project/blob/master/go-basic-07/03_%E5%8C%BF%E5%90%8D%E7%BB%93%E6%9E%84%E4%BD%93.go)

### 实例化结构体方法总结
```go
package main

import "fmt"

type Person struct {
    Name string
    Age  int
    City string
}

func main() {
    // 方式1: 零值
    var p1 Person
    fmt.Printf("p1: %+v\n", p1) // p1: {Name: Age:0 City:}
    
    // 方式2: 字面量 按照字段顺序
    p2 := Person{"张三", 25, "北京"}
    fmt.Printf("p2: %+v\n", p2) // p2: {Name:张三 Age:25 City:北京}
    
    // 方式3: 指定字段名
    p3 := Person{Name: "李四", Age: 30}
    fmt.Printf("p3: %+v\n", p3) // p3: {Name:李四 Age:30 City:}
    
    // 方式4: 指针
    p4 := &Person{Name: "王五", City: "上海"}
    fmt.Printf("p4: %+v\n", p4) // p4: &{Name:王五 Age:0 City:上海}

	// 方法5： 使用new关键子
	p := new(Person) // 返回 *Person 类型（指针） 
	p.Name = "赵六" 
	p.Age = 28

	//方法6: 构造函数
	func NewPerson(name string, age int, city string) *Person {   
		return &Person{ Name: name, Age: age, City: city, } } 
		// 使用 
		p := NewPerson("周八", 40, "广州")

}
```

### 接收器
#### 指针类型接收器
[示例代码](https://github.com/hyd1128/study-go-project/blob/master/go-basic-07/04_%E6%8C%87%E9%92%88%E7%B1%BB%E5%9E%8B%E6%8E%A5%E6%94%B6%E5%99%A8.go)

#### 非指针类型接收器
[示例代码](https://github.com/hyd1128/study-go-project/blob/master/go-basic-07/05_%E9%9D%9E%E6%8C%87%E9%92%88%E7%B1%BB%E5%9E%8B%E6%8E%A5%E6%94%B6%E5%99%A8.go)

#### 给任意类型添加方法
[示例代码](https://github.com/hyd1128/study-go-project/blob/master/go-basic-07/06_%E7%BB%99%E4%BB%BB%E6%84%8F%E7%B1%BB%E5%9E%8B%E6%B7%BB%E5%8A%A0%E6%96%B9%E6%B3%95.go)


### 匿名字段
[示例代码](https://github.com/hyd1128/study-go-project/blob/master/go-basic-07/07_%E5%8C%BF%E5%90%8D%E5%AD%97%E6%AE%B5.go)


## 接口
### 接口定义
[示例代码](https://github.com/hyd1128/study-go-project/blob/master/go-basic-08/01_%E6%8E%A5%E5%8F%A3%E5%AE%9A%E4%B9%89.go)
### 接口的实现条件
[示例代码](https://github.com/hyd1128/study-go-project/blob/master/go-basic-08/02_%E6%8E%A5%E5%8F%A3%E7%9A%84%E5%AE%9E%E7%8E%B0%E6%9D%A1%E4%BB%B6.go)
### 接口与类型之间的关系
#### 多个接口被一个类型实现
[示例代码](https://github.com/hyd1128/study-go-project/blob/master/go-basic-08/03_%E6%8E%A5%E5%8F%A3%E4%B8%8E%E7%B1%BB%E5%9E%8B%E4%B9%8B%E9%97%B4%E7%9A%84%E5%85%B3%E7%B3%BB_%E5%A4%9A%E6%8E%A5%E5%8F%A3%E8%A2%AB%E4%B8%80%E4%B8%AA%E7%B1%BB%E5%9E%8B%E5%AE%9E%E7%8E%B0.go)

#### 多个类型实现同一个接口
[示例代码](https://github.com/hyd1128/study-go-project/blob/master/go-basic-08/04_%E6%8E%A5%E5%8F%A3%E4%B8%8E%E7%B1%BB%E5%9E%8B%E4%B9%8B%E9%97%B4%E7%9A%84%E5%85%B3%E7%B3%BB_%E5%A4%9A%E7%B1%BB%E5%9E%8B%E5%AE%9E%E7%8E%B0%E4%B8%80%E4%B8%AA%E6%8E%A5%E5%8F%A3.go)

### 空接口及其应用
[示例代码1](https://github.com/hyd1128/study-go-project/blob/master/go-basic-08/05_%E7%A9%BA%E6%8E%A5%E5%8F%A3.go)
[示例代码2](https://github.com/hyd1128/study-go-project/blob/master/go-basic-08/06_%E7%A9%BA%E6%8E%A5%E5%8F%A3%E7%9A%84%E5%BA%94%E7%94%A8.go)
### 类型断言
[示例代码](https://github.com/hyd1128/study-go-project/blob/master/go-basic-08/07_%E7%B1%BB%E5%9E%8B%E6%96%AD%E8%A8%80.go)

## go语言包导入机制
[理解Go语言包(package) - 知乎](https://zhuanlan.zhihu.com/p/91627930)




