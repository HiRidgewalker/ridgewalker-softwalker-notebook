## javascirpt的引入方式
JavaScript 程序不能独立运行，它需要被嵌入 HTML 中，然后浏览器才能执行 JavaScript 代码。通过 `script` 标签将 JavaScript 代码引入到 HTML 中，有两种方式：

### 内部方式
通过 `script` 标签包裹 JavaScript 代码

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>JavaScript 基础 - 引入方式</title>

</head>

<body>
  <!-- 内联形式：通过 script 标签包裹 JavaScript 代码 -->
  <script>
    alert('嗨，欢迎来传智播学习前端技术！')
  </script>

</body>

</html>

```

### 外部形式
一般将 JavaScript 代码写在独立的以 .js 结尾的文件中，然后通过 `script` 标签的 `src` 属性引入

```javascript
// demo.js
document.write('嗨，欢迎来传智播学习前端技术！')
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>JavaScript 基础 - 引入方式</title>

</head>

<body>
  <!-- 外部形式：通过 script 的 src 属性引入独立的 .js 文件 -->
  <script src="demo.js"></script>

</body>

</html>

```

如果 script 标签使用 src 属性引入了某 .js 文件，那么 标签的代码会被忽略！！！如下代码所示：

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>JavaScript 基础 - 引入方式</title>

</head>

<body>
  <!-- 外部形式：通过 script 的 src 属性引入独立的 .js 文件 -->
  <script src="demo.js">
    // 此处的代码会被忽略掉！！！！
      alert(666);  
  </script>

</body>

</html>

```

## 注释
+ 单行注释

```shell
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>JavaScript 基础 - 注释</title>
</head>
<body>
  
  <script>
    // 这种是单行注释的语法
    // 一次只能注释一行
    // 可以重复注释
    document.write('嗨，欢迎来传智播学习前端技术！');
  </script>
</body>
</html>
```

+ 多行注释

```javascript
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>JavaScript 基础 - 注释</title>
</head>
<body>
  
  <script>
    /* 这种的是多行注释的语法 */
    /*
    	更常见的多行注释是这种写法
    	在些可以任意换行
    	多少行都可以
      */
    document.write('嗨，欢迎来传智播学习前端技术！')
  </script>
</body>
</html>
```

## 输入输出
常见输出相关方法：

1. `alert（）`
2. `document.write()`
3. `console.log()`

输入相关方法：

1. `prompt()`

## 变量
三个声明变量的关键字:

1. var
2. let
3. const

### let关键字使用注意事项
1. 允许声明和赋值同时进行
2. 不允许重复声明
3. 允许同时声明多个变量并赋值
4. JavaScript 中内置的一些关键字不能被当做变量名

### var关键字使用注意事项
2. 允许声明和赋值同时进行
3. 允许重复声明
4. 允许同时声明多个变量并赋值

大部分情况使用 `let` 和 `var` 区别不大，但是 `let` 相较 `var` 更严谨，因此推荐使用 `let`

### const关键字使用注意事项
1. 当某个变量永远不会改变的时候，就可以使用 const 来声明
2. 当使用const声明关键字的时候必须赋初值，同时基本类型定义后就不能够被修改，引用类型可以修改属性

### 变量命名规则
关于变量的名称（标识符）有一系列的规则需要遵守：

1. 只能是字母、数字、下划线、$，且不能能数字开头

2. 字母区分大小写，如 Age 和 age 是不同的变量

3. JavaScript 内部已占用于单词（关键字或保留字）不允许使用

4. 尽量保证变量具有一定的语义，见字知义

## 数据类型
### 基本数据类型
+ number
+ string
+ boolean
+ undefined：声明变量的时候未赋初值
+ null：将来存放对象的时候可以给null
+ symbol

### 引用数据类型
+ object
+ function
+ array

### 数据类型转换
### 显示转换
#### 字符转数字
```html
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
  <style>
    .box {
      width: 50px;
      height: 50px;
    }
  </style>
</head>

<body>
  <script>
    let str = '123'
    console.log(Number(str))
    console.log(Number('pink'))
    // let num = Number(prompt('输入年薪'))
    // let num = +prompt('输入年薪')
    // console.log(Number(num))
    // console.log(num)
    console.log(parseInt('12px'))
    console.log(parseInt('12.34px'))
    console.log(parseInt('12.94px'))
    console.log(parseInt('abc12.94px'))

    // -------------------
    console.log(parseFloat('12px')) // 12
    console.log(parseFloat('12.34px')) // 12.34
    console.log(parseFloat('12.94px')) // 12.94
    console.log(parseFloat('abc12.94px')) // 12.94
  </script>
</body>

</html>
```

### 隐式转换
number和string互相隐式转换

```html
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>

<body>
  <script>
    console.log(1 + 1)
    console.log('pink' + 1)
    console.log(2 + 2)
    console.log(2 + '2') // 22
    console.log(2 - 2)
    console.log(2 - '2')  // 0  
    console.log(+12)
    console.log(+'123')  // 转换为数字型
  </script>
</body>

</html>
```

