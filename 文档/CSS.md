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


## css flex布局
启动flex布局
父弹性盒子
```css
parent {
	display: flex
}
```
作用于父弹性盒子上的几个属性
```css
parent {
	display: flex;
	/* 
	flex-direction:
		- 控制主轴方向
		- 可选值
			- row: 从左向右
			- column: 从上向下
			- row-reverse: 从右向左
			- column: 从下向上

	flex-wrap:
		- 控制子元素溢出时的换行处理
		- 可选值：
			- nowrap： **不换行**（默认值），所有子元素排在一行，可能会溢出
			- wrap： **自动换行**，多余的子元素会移到下一行
			- wrap-reverse： **反向换行**，下一行出现在上方（从下往上排）

	justify-content
		- 置子元素在**主轴上的对齐方式**
		- 可选值
			- `flex-start` 从主轴的起点对齐（默认值）
			- `flex-end` 从主轴的终点对齐
			- `center` 居中对齐
			- `space-around` 在父盒子里平分
			- `space-between` 两端对齐 平分
	*/
}
```

可以作用在子元素上的几个属性
```css
son {
	/*
	align-items: 
		- 设置子元素在**侧轴上的对齐方式**
		- 可选值：
			- `flex-start` 从侧轴开始的方向对齐 
			- `flex-end` 从侧轴结束的方向对齐 
			- `baseline` 基线 默认同flex-start 
			- `center` 中间对齐 
			- `stretch` 拉伸 (注意： 子元素设置了height后使用了也没有效果)

	flex: 
		- 设置子盒子的权重（主轴方向）
		- 可选值
			- 数字

	justify-content：
		同上
		
	*/
}
```
```css
#div {

    height: 100%;

    display: flex;

    /* 用于设置盒子中子元素的排列方向 主轴方向*/

    /* 从左向右水平排列 */

    flex-direction: row;

    /* 从上向下垂直排列 */

    /* flex-direction: column; */

    /* 从右向左水平排列 */

    /* flex-direction: row-reverse; */

    /* 从下向上垂直排列 */

    /* flex-direction: column-reverse; */

    /* 备注：如果我们不给父容器写flex-direction这个属性，那么，子元素默认就是从左到右排列的。 */

  

    /* 控制子元素溢出时的换行处理 */

    /* flex-wrap: nowrap; */

    /*

    控制子元素在主轴上的排列方式

        justify-content:

            flex-start; 设置子元素在主轴上的对齐方式。属性值可以是：

            flex-start 从主轴的起点对齐（默认值）

            flex-end 从主轴的终点对齐

            center 居中对齐

            space-around 在父盒子里平分

            space-between 两端对齐 平分

    */

    /* justify-content: flex-start; */

    /* justify-content: flex-end; */

    justify-content: space-between;

  

    /* 侧轴方向操作 */

    /* 从侧轴开始的方向对齐 */

    /* align-items: flex-start */

    /* 从侧轴结束的方向对齐 */

    /* align-items: stretch; */

}

  

/* #div1 {

    width: 500px;

    height: 200px;

    background-color: antiquewhite;

}

  

#div2 {

    width: 20px;

    height: 300px;

    background-color: aquamarine;

}

  

#div3 {

    width: 300px;

    height: 100px;

    background-color: bisque;

}

#div4 {

    width: 800px;

    height: 100px;

    background-color: chocolate;

} */

  

#div div  {

    width: 200px;

    /* height: 200px; */

    /* background-color: aquamarine; */

    margin-right: 5px;

}

  

#div1 {

    background-color: aqua;

    flex: 2

}

  

#div2 {

    background-color: bisque;

    flex: 3

}

  

#div3 {

    background-color: black;

    flex: 1

}

#div4 {

    background-color: blue;

    flex: 2

}
```