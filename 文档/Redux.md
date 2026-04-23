## 为什么要使用redux
+ 数据独立于组件，无视组件之间的层级关系，简化通信问题 (个人觉得这一点最重要， 和vue的pinia功能非常相似)
+ 单向数据流清晰，易于定位bug
+ 调试工具配套良好，方便调试

## Redux的具体使用步骤
1. 定义一个reducer函数（根据当前想要做的修改返回一个新的状态）
2. 使用createStore方法传入reducer函数，生成一个store实例对象
3. 使用store实例的subscrible方法订阅数据的变化（数据一旦变化，可以得到通知）
4. 使用store实例的dispatch方法提交action对象，触发数据变化（告诉reducer应该怎么更改状态）
5. 使用store实例的getState方法获取罪行的状态数据更新到视图中

### 计算器示例
```html
<button id="decrement">-</button>
<span id="count">0</span>
<button id="increment">+</button>

<script src="https://unpkg.com/redux@latest/dist/redux.min.js"></script>

<script>
  // 定义reducer函数 
  // 内部主要的工作是根据不同的action 返回不同的state
  function counterReducer (state = { count: 0 }, action) {
    switch (action.type) {
      case 'INCREMENT':
        return { count: state.count + 1 }
      case 'DECREMENT':
        return { count: state.count - 1 }
      default:
        return state
    }
  }
  // 使用reducer函数生成store实例
  const store = Redux.createStore(counterReducer)

  // 订阅数据变化
  store.subscribe(() => {
    console.log(store.getState())
    document.getElementById('count').innerText = store.getState().count

  })
  // 增
  const inBtn = document.getElementById('increment')
  inBtn.addEventListener('click', () => {
    store.dispatch({
      type: 'INCREMENT'
    })
  })
  // 减
  const dBtn = document.getElementById('decrement')
  dBtn.addEventListener('click', () => {
    store.dispatch({
      type: 'DECREMENT'
    })
  })
</script>
```

## reducer数据流架构
<!-- 这是一张图片，ocr 内容为：REDUX的难点是理解它对于数据修改的规则,下图动态展示了在整个数据的修改中,数据的流向 STORE STATE STATE REDUCER ACTION STATE STATE VIEW[视图] 为了职责清晰,REDUX代码被分为三个核心的概念,我们单REDUX,其实就是学这三个核心概念之间的配合,三个 概念分别是: 1.STATE:一个对象存放着我们管理的数据 2.ACTION:一个对象用来描述你想怎么改数据 3.REDUCER:一个函数根据ACTION的描述更新STATE -->
![](https://cdn.nlark.com/yuque/0/2025/png/38690142/1749049402998-8aa5d989-6e55-4662-ab6b-fc68d073bb79.png)

## 具体使用方法
### Redux与React - 环境准备
Redux虽然是一个框架无关可以独立运行的插件，但是社区通常还是把它与React绑定在一起使用，以一个计数器案例体验一下Redux + React 的基础使用

### 1. 配套工具
在React中使用redux，官方要求安装俩个其他插件 - Redux Toolkit 和 react-redux

1. Redux Toolkit（RTK）- 官方推荐编写Redux逻辑的方式，是一套工具的集合集，简化书写方式
2. react-redux - 用来 链接 Redux 和 React组件 的中间件

### 2. 配置基础环境
使用 CRA 快速创建 React 项目

```shell
npx create-react-app react-redux 
```

安装配套工具

```shell
npm i @reduxjs/toolkit  react-redux 
```

启动项目

```shell
npm run start 
```

3store目录结构设计

通常集中状态管理的部分都会单独创建一个单独的 `store` 目录

应用通常会有很多个子store模块，所以创建一个 `modules` 目录，在内部编写业务分类的子store

store中的入口文件 index.js 的作用是组合modules中所有的子模块，并导出store

### Redux与React - 实现counter
#### 1. 整体路径熟悉<!-- 这是一张图片，ocr 内容为：注入STORE(REACT-REDUX) 配置COUNTERSTORE模块 STORE 使用STORE中的数据 配置根STORE并组合 COUNTERSTORE模块 修改STORE中的数据 REACT组件 REDUXSTORE配置 -->
![](https://cdn.nlark.com/yuque/0/2025/png/38690142/1749049773307-3fe0fc7c-b9c7-4024-9d89-ad868539e8ae.png)
#### 2. 使用React Toolkit 创建 counterStore
```jsx
import { createSlice } from '@reduxjs/toolkit'

const counterStore = createSlice({
  // 模块名称独一无二
  name: 'counter',
  // 初始数据
  initialState: {
    count: 1
  },
  // 修改数据的同步方法
  reducers: {
    increment (state) {
      state.count++
    },
    decrement(state){
      state.count--
    }
  }
})
// 结构出actionCreater
const { increment,decrement } = counter.actions

// 获取reducer函数
const counterReducer = counterStore.reducer

// 导出
export { increment, decrement }
export default counterReducer
```

```jsx
import { configureStore } from '@reduxjs/toolkit'

import counterReducer from './modules/counterStore'

export default configureStore({
  reducer: {
    // 注册子模块
    counter: counterReducer
  }
})
```

#### 3. 为React注入store
react-redux负责把Redux和React 链接 起来，内置 Provider组件 通过 store 参数把创建好的store实例注入到应用中，链接正式建立

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
// 导入store
import store from './store'
// 导入store提供组件Provider
import { Provider } from 'react-redux'

ReactDOM.createRoot(document.getElementById('root')).render(
  // 提供store数据
  <Provider store={store}>
    <App />
  </Provider>
)
```

#### 4. React组件使用store中的数据
在React组件中使用store中的数据，需要用到一个钩子函数 - useSelector，它的作用是把store中的数据映射到组件中，使用样例如下：

<!-- 这是一张图片，ocr 内容为：1 CONST { COUNT } - USESELECTOR(STATE STATE COUNTER 12345678 IMPORT { CONFIGURESTORE } FROM "@REDUXJS/TOOLKIT" IMPORT COUNTERREDUCER /MODULES/COUNTERSTORE" FROM //创建根STORE组合子模块 CONFIGURESTORE({ CONST STORE REDUCER COUNTER COUNTERREDUCER 子) 10 172  EXPORT DEFAULT STORE -->
![](https://cdn.nlark.com/yuque/0/2025/png/38690142/1749049831362-3375e0cd-a4b3-49d1-a70e-929f3fe8eeb1.png)

#### 5. React组件修改store中的数据
React组件中修改store中的数据需要借助另外一个hook函数 - useDispatch，它的作用是生成提交action对象的dispatch函数，使用样例如下：

<!-- 这是一张图片，ocr 内容为：IMPORT { USEDISPATCH, USELECTOR } FROM 'REACT-REDUX' 1 2 //导入创建ACTION对象的方法 DECREMENT, INCREMENT ? FROM './STORE/MODULES/COUNTERSTORE' IMPORT }( FUNCTION APP 5 USESESELECTOR(STATE -> STATE.COUNTER) COUNT CONST //得到DISPATCH函数 9 4 DISPATCH USEDISPATCH() 二 CONST 8 RETURN <DIV CLASSNAME-"APP"> 9 10 {/* 调用DISPATCH提交ACTION对象 */} <BUTTON ONCLICK-{() -> DISPATCH(DECREMENT()>>-</BUTTON> 卫口 <SPAN>{COUNT}</SPAN> <BUTTON ONCLICK-L (K-{() -> DISPATCH(INCREMENT()}+</BUTTON> 13 14 </DIV> 15 子 16 -->
![](https://cdn.nlark.com/yuque/0/2025/png/38690142/1749049849015-2c9d3b8c-ed22-4162-b047-c109d7017510.png)

#### Redux与React - 提交action传参
> 需求：组件中有俩个按钮 `add to 10` 和 `add to 20` 可以直接把count值修改到对应的数字，目标count值是在组件中传递过去的，需要在提交action的时候传递参数
>

<!-- 这是一张图片，ocr 内容为：￥ 2 C LOCALHOST:3000 ADD TO 10 0 ADD TO 20 -->
![](https://cdn.nlark.com/yuque/0/2025/png/38690142/1749049921829-57201847-f4f2-4c77-90e6-32905bd8cf80.png)

实现方式：在reducers的同步修改方法中添加action对象参数，在调用actionCreater的时候传递参数，参数会被传递到action对象payload属性上

<!-- 这是一张图片，ocr 内容为：APP.IS M X COUNTERSTORE.JS M X COUNTERSTORE.JS >..... APP.JS > SRC SRC STORE > MODULES> FEUCERS:1 IMPORT { USEDISPATCH, USELECTOR } FROM 'REACT-REDUX' 17 (STATE) INCREMENT // 导入创建ACTION对象的方法 STATE.COUNTTH 34 IMPORT { DECREMENT. INCREMENT. ADDTONUM } FROM ',/STORE/MODULES/ 34567890123456380 13 子, FUNCTIONAPP(){  DECREMENT (STATE) { 14 CONST { COUNT } USESELECTOR(STATE -> STATE.COUNTER) 15 STATE.COUNT //得到DISPATCH函数 16  CONST DISPATCH - USEDISPATCH() ADDTONUM (STATE, ACTION) RETURN STATE.COUNT ACTION.PAYLOAD <DIV CLASSNAME-"APP"> {/*调用DISPATCH提交ACTION对象 <BUTTON ONCLICK-() DISPATCH(DECREMENT())>-</BUTTON> <SPAN>:COUNT}</SPAN> DISPATCH(INCREMENT()>>>+</BUTTON> <BUTTON ONCLICK () 解构出创建ACTION对象的函数  (ACTIONCREATER) DISPATCH(ADDTONUM(10))}-ADD TO 10</ (BUTTON ONCLICK CONST [ INCREMENT, DECREMENT, ADDTONUM ] COUNTERSTORE.ACTIONS 6UTTON ONCLICK-{() DISPATCH(ADDTONUM(20))]]] PADD TO 20</1 //获取REDUCER函数 25 </DIV> 26 CONST COUNTERREDUCER - COUNTERSTORE.REDUCER 27 // 导出创建ACTION对象的函数和REDUCER函数 19 28 EXPORT { INCREMENT, DECREMENT, ADDTONUM } 29 EXPORT DEFAULT COUNTERREDUCER  EXPORT DEFAULT APP 20 30 21 -->
![](https://cdn.nlark.com/yuque/0/2025/png/38690142/1749049903383-c13e54b5-e65c-4ce4-acf3-e95df8247c1f.png)

