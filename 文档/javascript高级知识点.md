## var， let的区别
var关键字声明的变量没有块级作用域，而let声明的有

```javascript
{
  var i1 = 10;
  let i2 = 20;
  console.log(i1);
  console.log(i2);
}
console.log(i1);
console.log(i2); // 报错
```

```javascript
for (var i = 1; i <= 3; i++) {
  // 块作用域
  console.log(i);
}
console.log("全局作用域中的i", i);

for (let i = 1; i <= 3; i++) {
  // 块作用域
  console.log(i);
}
console.log(i);
console.log(i2); // 报错
```

var定义的变量可以发生变量提升,而let声明的变量不会发生变量提升

```javascript
console.log(a1); // undefined
console.log(a2); // 报错
var a1;
let a2;
```

## 闭包
简单闭包写法

```javascript
// 简单的写法
function outer() {
  let a = 10;
  function fn() {
    console.log(a);
  }
  fn();
}
outer();  
// console.log(a);	// 闭包中也无法访问到局部作用域中定义的变量
```

闭包应用2

```javascript
// 闭包的应用
// 普通形式 统计函数调用的次数
let i = 0;
function fn() {
  i++;
  console.log(`函数被调用了${i}次`);
}
//  因为 i 是全局变量，容易被修改
// 闭包形式 统计函数调用的次数
function count() {
  let i = 0;
  function fn() {
    i++;
    console.log(`函数被调用了${i}次`);
  }
  return fn;
}
const fun = count();
fn();
fn();
fn();
```

### 如何理解闭包
1.怎么理解闭包？

+ 闭包 = 内层函数 + 外层函数的变量

2.闭包的作用？

+ 封闭数据，实现数据私有，外部也可以访问函数内部的变量 (需要通过闭包中的函数返回内部的变量，闭包中的变量是不会发生变量提升的)
+ 闭包很有用，因为它允许将函数与其所操作的某些数据（环境）关联起来

3.闭包可能引起的问题？

+ 内存泄漏



## 函数动态参数 (<font style="color:#abb2bf;background-color:#282c34;">arguments关键字</font>)
```javascript
function getSum() {
  // arguments 动态参数 只存在于 函数里面
  // 是伪数组 里面存储的是传递过来的实参
  // console.log(arguments)  [2,3,4]
  let sum = 0;
  console.log(arguments);
  for (let i = 0; i < arguments.length; i++) {
    sum += arguments[i];
  }
  console.log(sum);
}

getSum(2, 3, 4);
getSum(1, 2, 3, 4, 2, 2, 3, 4);
</script>
```

## 函数剩余关键字
```javascript
function getSum(a, b, ...arr) {
  console.log(arr); // 使用的时候不需要写 ...
}
getSum(2, 3); // []
getSum(1, 2, 3, 4, 5); // [3,4,5]
```

## 展开运算符
```javascript
const arr1 = [1, 2, 3];

// console.log(Math.max(1, 2, 3))
// ...arr1  === 1,2,3
// 1 求数组最大值
console.log(Math.max(...arr1)); // 3
console.log(Math.min(...arr1)); // 1
// 2. 合并数组
const arr2 = [3, 4, 5];
const arr = [...arr1, ...arr2];
console.log(arr); //  [1,2,3,3,4,5]
// 展开运算符 可以展开数组
console.log(...arr); //   1 2 3 3 4 5
```

## javascript的对象相关知识点
### 构造函数
对比以下通过面向对象的构造函数实现的封装：

```html
<script>
  function Person() {
    this.name = '佚名'
    // 设置名字
    this.setName = function (name) {
      this.name = name
    }
    // 读取名字
    this.getName = () => {
      console.log(this.name)
    }
  }

  // 实例对像，获得了构造函数中封装的所有逻辑
  let p1 = new Person()
  p1.setName('小明')
  console.log(p1.name)

  // 实例对象
  let p2 = new Person()
  console.log(p2.name)
</script>

```

封装是面向对象思想中比较重要的一部分，js面向对象可以通过构造函数实现的封装。

同样的将变量和函数组合到了一起并能通过 this 实现数据的共享，所不同的是借助构造函数创建出来的实例对象之

间是彼此不影响的

> 总结：
>
> 1. 构造函数体现了面向对象的封装特性
> 2. 构造函数实例创建的对象彼此独立、互不影响
>

封装是面向对象思想中比较重要的一部分，js面向对象可以通过构造函数实现的封装。

前面我们学过的构造函数方法很好用，但是 存在`浪费内存`的问题

### prototype和__proto__
| 名称 | 作用 |
| --- | --- |
|  构造函数   | 用于创建对象的函数，例如 `function Person() {}` |
|  原型（Prototype）  （大写P，和下面不一样） |  共享方法和属性的对象，实例可以通过prototype继承它   |
|  prototype   | 构造函数的 `prototype`<br/> 属性，指向原型对象 |
|  __proto__   | 每个对象的隐藏属性，指向它的原型对象（即 `constructor.prototype`<br/>） |


相关的一些代码测试和结论:

```javascript
<script>
  // 原型对象
  function Person(name, age) {
    this.name = name;
    this.age = age;
  }

function Animal() {}

const p1 = new Person("xiaoming", 19);
const p2 = new Person("daming", 20);

// 原型对象
console.log(p1.__proto__ === p2.__proto__);  // true
console.log(p1.__proto__ === Person.prototype);  // true
console.log(p2.__proto__ === Person.prototype);  // true
console.log((p1.constructor === p2.constructor) === Person); // true

// 在原型对象上添加属性
Person.prototype.sex = "男";
console.log(p1.sex);
console.log(p2.sex);

// 不同构造函数的原型对象是否一致
console.log(Person.prototype === Animal.prototype); // false

/*
通过上述可以得出结论:
1. 每个构造函数都有一个原型对象
2. 原型对象都有一个constructor属性指向构造函数
3. 实例对象都有一个__proto__属性指向原型对象
4. 实例对象可以访问原型对象上的属性和方法
5. 不同构造函数的原型对象不相等
6. 原型和原型对象的意思是对等的
*/

console.log(Person.prototype.__proto__ === Object.prototype); // true
console.log(Object.prototype.__proto__ === null); // true
console.log(Person.prototype.constructor === Person); // true
</script>
```

### 原型链图
<!-- 这是一张图片，ocr 内容为：NULL OBJECT原型对象PROTOTYPE._PROTO_ OBJECT.PROTYPE OBJECT 原型对象 OBJECT构造函数 PROTOTYPE OBJECT原型对 象.CONSTRUCTOR STAR原型对象PROTOTYPE._PROTO_ STAR.PROTYPE STAR原型对象 STAR构造函数 PROTOTYPE 原型对 象.CONSTRUCTOR IDH._PROTO. IDH对象实例 -->
![](https://cdn.nlark.com/yuque/0/2025/png/38690142/1742121185316-6671ca65-7bd8-48a2-be3e-dcc655b17612.png)

### constructor属性
在哪里？ 每个原型对象里面都有个constructor 属性（constructor 构造函数）

作用：该属性指向该原型对象的构造函数， 简单理解，就是指向我的爸爸，我是有爸爸的孩子

**使用场景：**

如果有多个对象的方法，我们可以给原型对象采取对象形式赋值.

但是这样就会覆盖构造函数原型对象原来的内容，这样修改后的原型对象 constructor 就不再指向当前构造函数了

此时，我们可以在修改后的原型对象中，添加一个 constructor 指向原来的构造函数。

使用案例：

```javascript
Person.prototype.sayHello = function () {
  console.log("Hello");
};
console.log(Person.prototype.constructor === Person); // true

Person.prototype = {
  sayHello: function () {
    console.log("Hello");
  },
};

console.log(Person.prototype.constructor === Person); // false
console.log(Person.prototype.constructor === Object); // true

// 修改回来
Person.prototype = {
  constructor: Person,
  sayHello: function () {
    console.log("Hello");
  },
};

console.log(Person.prototype.constructor === Person); // true

/*
  总结:
    1. 给原型对象从新定义后constructor属性会被修改
    2. 如果想让constructor属性指向构造函数,需要手动修改
 */
```

