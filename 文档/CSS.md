## font字体属性
[font字体属性](https://github.com/qianguyihao/Web/blob/master/02-CSS%E5%9F%BA%E7%A1%80/01-CSS%E5%B1%9E%E6%80%A7%EF%BC%9A%E5%AD%97%E4%BD%93%E5%B1%9E%E6%80%A7%E5%92%8C%E6%96%87%E6%9C%AC%E5%B1%9E%E6%80%A7.md)
## css 属性的继承性
[css属性的继承性](https://github.com/qianguyihao/Web/blob/master/02-CSS%E5%9F%BA%E7%A1%80/05-CSS%E6%A0%B7%E5%BC%8F%E8%A1%A8%E7%9A%84%E7%BB%A7%E6%89%BF%E6%80%A7%E5%92%8C%E5%B1%82%E5%8F%A0%E6%80%A7.md)
## 行内元素和块级元素
**行内元素和块级元素的区别：**（非常重要）
行内元素：
- 与其他行内元素并排；
- 不能设置宽、高。默认的宽度，就是文字的宽度。
块级元素：
- 霸占一行，不能与其他任何元素并列；
- 能接受宽、高。如果不设置宽度，那么宽度将默认变为父亲的100%。
**行内元素和块级元素的分类：**
在以前的HTML知识中，我们已经将标签分过类，当时分为了：文本级、容器级。
从HTML的角度来讲，标签分为：
- 文本级标签：p、span、a、b、i、u、em。
- 容器级标签：div、h系列、li、dt、dd。
[文档](https://github.com/qianguyihao/Web/blob/master/02-CSS%E5%9F%BA%E7%A1%80/07-%E6%B5%AE%E5%8A%A8.md)
## 浮动
[文档](https://github.com/qianguyihao/Web/blob/master/02-CSS%E5%9F%BA%E7%A1%80/07-%E6%B5%AE%E5%8A%A8.md)
### 浮动性质1
- 脱离原来的文档流
- 一旦一个元素浮动了，那么，将能够并排了，并且能够设置宽高了。无论它原来是个div还是个span。所有标签，浮动之后，已经不区分行内、块级了。
### 浮动性质2
- 浮动的元素互相贴靠
### 浮动性质3
- 浮动的元素有"字围"效果
- 标准流中的文字不会被浮动的盒子遮挡住。

> 关于浮动我们要强调一点，浮动这个东西，为避免混乱，我们在初期一定要遵循一个原则：**永远不是一个东西单独浮动，浮动都是一起浮动，要浮动，大家都浮动。**

### 浮动性质4
- 收缩：一个浮动的元素，如果没有设置width，那么将自动收缩为内容的宽度（这点非常像行内元素）。


> [!info]
> css 浮动作业 [点击](https://github.com/qianguyihao/Web/blob/master/02-CSS%E5%9F%BA%E7%A1%80/07-%E6%B5%AE%E5%8A%A8.md#%E5%B8%83%E7%BD%AE%E4%B8%80%E4%B8%AA%E4%BD%9C%E4%B8%9A)
> 

### css定位属性
[文档](https://github.com/qianguyihao/Web/blob/master/02-CSS%E5%9F%BA%E7%A1%80/08-CSS%E5%B1%9E%E6%80%A7%EF%BC%9A%E5%AE%9A%E4%BD%8D%E5%B1%9E%E6%80%A7.md)

### flex布局图详解
[文档](https://github.com/qianguyihao/Web/blob/master/02-CSS%E5%9F%BA%E7%A1%80/13-CSS3%E5%B1%9E%E6%80%A7%EF%BC%9AFlex%E5%B8%83%E5%B1%80%E5%9B%BE%E6%96%87%E8%AF%A6%E8%A7%A3.md)
