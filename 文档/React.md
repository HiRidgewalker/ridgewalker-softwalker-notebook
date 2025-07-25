react编写注意事项
- react定义组件的时候，首字母一定要大写,推荐组件名称与文件名称相同
- react允许直接通过import 的方式引入css文件、图片等，前端构建工具会自动处理
```jsx
mport { useState } from 'react';
import '@/styles/main.scss';
import reactLogo from '@/assets/react.svg';

function AppTemplate() {
  const [count, setCount] = useState(0);
  return (
    <div className="app">
      <div>
        <a href="https://react.dev" target="_blank" rel="noreferrer">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>React + Vite</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/AppTemplate.jsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the React logo to learn more
      </p>
    </div>
  );
}

export default AppTemplate;
```
## react组件通信
### 父子传递
常规传递
```jsx
function Son(obj) {
    // 子组件props名称随意
    // props可以传递任意的合法数据，比如数字、字符串、布尔值、数组、对象、函数、JSX
    return (
        <div>
            {console.log(obj)}
            <div>{obj.name}--{obj.age}</div>
        </div>
    );
}

function App() {
    // 组件通信
    // 1. 父组件向子组件通信
    const name = 'this is app name'
    const age = 16
    return (
        <div>
            <Son name={name} age={age}/>
        </div>
    )
}

export default App;

```
特殊传递
在React中，组件可以通过`props`接收数据，其中一个特殊的`prop`是`children`。当你在组件标签内部嵌套内容时，这些内容会自动作为`children`传递给组件。`children`可以是任何类型的React元素，包括字符串、数字、React组件或其他元素。
例如，假设你有一个简单的组件：
```jsx
function MyComponent(props) {
  return (
    <div>
      {props.children}
    </div>
  );
}
```

在使用这个组件时，你可以这样嵌套内容：
```jsx
<MyComponent>
  <h1>Hello, World!</h1>
  <p>This is a paragraph.</p>
</MyComponent>
```
在这种情况下，`<h1>`和`<p>`标签会作为`children`传递给`MyComponent`，并在组件内部进行渲染。这种方式使得组件可以灵活地接收和渲染嵌套的内容。
>[!warning]
>**props是只读对象** 子组件只能读取props中的数据，不能直接进行修改, 父组件的数据只能由父组件修改

父子通信相关代码：
```jsx
// function Son(obj) {
//     // 子组件props名称随意
//     // props可以传递任意的合法数据，比如数字、字符串、布尔值、数组、对象、函数、JSX
//     return (
//         <div>
//             {console.log(obj)}
//             <div>{obj.name}--{obj.age}</div>
//         </div>
//     );
// }
import { useState } from 'react';
// // 特殊的props
// function SonOne (props) {
//     return <div>
//         {props.children}
//     </div>
// }
 
// 注意: 这里解构之后才能够直接使用
// function SonTwo ({onGetMsg}) {
//     const sonMsg = 'this is son msg
//     return (
//         <div>
//             {/* 子组件中执行父组件传递过来的函数 */}
//             <button onClick={() => onGetMsg(sonMsg)}>send</button>
//         </div>
//     )
// }

// 3. 跨级组件通信
// 跨级组件通信的本质： 子组件向父组件通信
// 跨级组件通信的实现： 子组件向父组件传递函数
// 跨级组件通信的实现： 父组件向子组件传递函数
// 简单说就是一个状态提升
function SonThree({ onGetMsg }) {
    const sonMsg = 'this is son msg';
    return <button onClick={() => onGetMsg(sonMsg)}>send</button>;
}

function SonFour(props) {
    return <div>{props.name}</div>;
}
  
function App() {
    // 组件通信
    // 1. 父组件向子组件通信
    // const name = 'this is app name'
    // const age = 16
    // return (
    //     <div>
    //         <Son name={name} age={age}/>
    //         <SonOne>
    //             <div>hello world</div>
    //         </SonOne>
    //     </div>
    // )
    // 2. 子组件向父组件通信
    // const getMsg = (msg) => console.log(msg)
    // return (
    //     <div>
    //         {/* 传递父组件中的函数到子组件 */}
    //         <SonTwo onGetMsg={getMsg}/>
    //     </div>
    // )
    // 3. 跨级组件通信
    const [name, setName] = useState('');
    const getName = (name) => {
        setName(name);
    };
    return (
        <div>
            <SonThree onGetMsg={getName} />
            <SonFour name={name} />
        </div>
    );
}
 
export default App;
```

## react的hook函数
- useState
	- 返回state和setState
- useRef
	- 返回链接的dom对象
- useContext
	在底层组件，通过useContext使用组件
	- 返回provider上的value值
- useEffect
语法：
```jsx
useEffect(() => {
	// 实现副作用逻辑
	return () => {
		// 清除副作用逻辑
	}
}, [])
```
#useEffect执行详解

| 依赖项     | 副作用功能函数的执行时机        | 清除副作用功能函数执行时机        |
| ------- | ------------------- | -------------------- |
| 没有依赖项   | 组件初始渲染 + 组件更新时执行    | 组件卸载时 + 副作用函数下一次执行之前 |
| 空数组依赖   | 只在初始渲染时候执行1次        | 组件卸载时                |
| 添加特定依赖项 | 组件初始渲染  + 依赖项变化时候执行 | 组件卸载时 + 副作用函数下一次执行之前 |
- useDispatch
	- React组件中修改store中的数据需要借助另外一个hook函数 - useDispatch，它的作用是生成提交action对象的dispatch函数
- useSelector
	- 在React组件中使用store中的数据，需要用到一个钩子函数 - useSelector，它的作用是把store中的数据映射到组件中
- useParams
	- 获取动态路由传参
- useSearchParams
	- 获取查询字符串传参
- useState
	- 获取隐式传参

## react 自定义hook和使用hook的注意事项
```js
// 封装自定义hook
// 问题: 布尔切换的逻辑, 当前组件耦合在一起, 不方便使用
// 解决思路： 自定义hook

import { useState } from 'react';

function useToggle() {
    // 可复用的逻辑代码
    const [value, setValue] = useState(false);
    const toggle = () => setValue(!value);

    // 哪些状态和回调函数需要在其他组件中使用就return
    return {
        value,
        toggle,
    };
}

// 封装自定义hook通用思路
// 1. 声明一个以use打头的函数
// 2. 在函数体内封装可复用的逻辑（只要是可复用的逻辑）
// 3. 把组件中用到的状态或者回调return出去（以对象或者数组）
// 4. 在哪个组件中要用到这个逻辑，就执行这个函数，解构出来状态和回调进行使用

// React Hooks使用规则
// 只能在组件中或者其他自定义Hook函数中调用
// 只能在组件的顶层调用，不能嵌套在if、for、其它的函数中

export { useToggle }
```
>[!warning]

React的Hook只能在组件的顶层或自定义Hook中使用，主要是为了保证Hook调用的顺序在每次渲染时保持一致。这是React设计Hook的一个重要规则，原因如下：
1. **保证Hook调用顺序一致**  
    React通过调用Hook的顺序来关联状态和副作用。如果在条件语句（如`if`）、循环（如`for`）或函数内部调用Hook，可能导致每次渲染时调用的Hook数量或顺序不同，React就无法正确匹配之前的状态，导致状态错乱或报错。
    
2. **避免状态管理混乱**  
    Hook内部依赖调用顺序来维护状态和副作用的对应关系。如果调用顺序不固定，React无法追踪哪个状态对应哪个Hook，导致状态更新错误。
    
3. **自定义Hook作为复用机制**  
    自定义Hook本质上是一个函数，内部可以调用其他Hook。只要自定义Hook在组件顶层调用，调用顺序依然固定，React就能正确管理状态。
    
总结：  
为了保证React能够正确地追踪和管理组件的状态，Hook必须在组件函数的顶层或自定义Hook中调用，不能放在条件判断、循环或嵌套函数中。这样才能保证每次渲染时Hook调用顺序一致，避免状态错乱。


## redux
类似vue的pinia
作用：
- 独立于组件，无视组件之间的层级关系，简化组件之间的通信问题
- 单项数据流清晰，已于定位bug
- 调试工具配套良好，方便调试

| 角色      | 作用                    | 例子                                      |
| ------- | --------------------- | --------------------------------------- |
| state   | 存储数据                  |  `{ value: 0 }`                         |
| reducer | 根据action更新state       |  `increment: (state) => {}`             |
| action  | 描述事件，触发reducer更新state |  `increment()`, `incrementByAmount(5)`  |

这样，`state`是数据，`action`是触发更新的信号，`reducer`是根据`action`修改`state`的逻辑。`@reduxjs/toolkit`通过`createSlice`把这些角色整合得很方便。
![[image.png]]


## 常见问题
### react组件挂载时，是先执行js代码还是先渲染html代码
 ✅ 简短回答：
**先执行 JS（函数逻辑）代码，再生成并渲染 return 的 JSX（HTML-like 结构）**。

---

🧠 详细解释：
以一个函数组件为例：
```jsx
function MyComponent() {   
	console.log("组件函数执行");    
	const now = new Date().toLocaleTimeString();    
	return <div>当前时间是：{now}</div>; 
}

```
当这个组件首次挂载到页面上时：
✅ React 的执行顺序：
1. **执行组件函数**（这是一个普通的 JS 函数）：
    
    - `console.log("组件函数执行")` 会立即打印。
        
    - 所有定义的变量、函数、hooks（如 `useState`, `useEffect`）都会运行。
        
2. **组件函数 return JSX**：
    
    - JSX 是一种语法糖，React 会将其转换成 `React.createElement(...)` 调用。
        
3. **React 根据 return 的 JSX 构建虚拟 DOM → 真实 DOM**
    
4. **浏览器渲染 DOM，最终显示在页面上**
    
5. **最后才执行 `useEffect(...)` 中的副作用逻辑（如果有）**
    

---

💡 所以你可以理解为：
- `return` 的 JSX 类似于“函数的输出”；
    
- 只有**组件函数被执行后**，才能得到这些 HTML 结构；
    
- 因此，JS 逻辑（即组件函数体的内容）是先执行的。
    

---

⏱ 举个带副作用的例子：
```jsx
function Example() {
  console.log("1. 组件函数执行");

  useEffect(() => {
    console.log("3. useEffect 执行（DOM挂载后）");
  }, []);

  return <div>2. 返回 JSX</div>;
}
```
**输出顺序：**
`1. 组件函数执行 2. （JSX 渲染在页面上） 3. useEffect 执行（DOM挂载后）`



### react常见原生钩子函数执行时机
总结 **React 原生 Hook 的执行时机**：到底是在 **render（即 JSX 渲染）前** 还是 **后** 执行的。

---

✅ React 原生 Hook 执行时机总览表（函数组件）

|Hook 名称|何时执行（相对于 JSX 渲染）|说明|
|---|---|---|
|`useState`|✅ 渲染前（同步执行）|初始化状态，JS 函数体中同步执行|
|`useReducer`|✅ 渲染前（同步执行）|同上，用于更复杂状态管理|
|`useMemo`|✅ 渲染前（同步执行）|仅当依赖变化时重新计算|
|`useCallback`|✅ 渲染前（同步执行）|返回缓存的函数引用|
|`useRef`|✅ 渲染前（同步执行）|初始化 ref 对象|
|`useContext`|✅ 渲染前（同步执行）|获取 context 值|
|`useLayoutEffect`|✅ 渲染后、DOM 更新前（同步执行）|用于同步副作用操作（如测量 DOM）|
|`useEffect`|❌ 渲染后、DOM 更新后（异步执行）|用于异步副作用（如请求、订阅）|
|`useImperativeHandle`|✅ 渲染后、DOM 更新前（在 forwardRef 内）|控制暴露给父组件的 ref|
|`useId`|✅ 渲染前|React 18 新增，用于生成稳定 ID|
|`useTransition`|✅ 渲染前|启动 transition（延迟更新）|
|`useDeferredValue`|✅ 渲染前|推迟不重要的值更新|
|`useSyncExternalStore`|✅ 渲染前|用于订阅外部 store（如 Redux）|
|`useInsertionEffect`|✅ 渲染前（比 `useLayoutEffect` 更早）|用于插入 CSS（CSS-in-JS 场景）|

---

🔄 执行流程图解（顺序大致如下）：

1. ✅ 执行组件函数（包括所有 useState、useRef、useMemo 等）
    
2. ✅ 生成并渲染 JSX（构建虚拟 DOM）
    
3. ✅ React 更新真实 DOM（DOM 已出现在页面上）
    
4. ✅ `useLayoutEffect` 执行（同步）
    
5. ✅ 浏览器绘制 UI
    
6. ✅ `useEffect` 执行（异步）
    

---

🧠 举个例子：

```jsx
function Demo() {
  const [count, setCount] = useState(0);       // 渲染前
  const ref = useRef(null);                    // 渲染前

  useMemo(() => console.log("memo"), [count]); // 渲染前

  useLayoutEffect(() => {
    console.log("useLayoutEffect", ref.current);
  }, []);

  useEffect(() => {
    console.log("useEffect");
  }, []);

  return <div ref={ref}>Count: {count}</div>;
}
```
输出顺序（首次挂载）：

```csharp
memo useLayoutEffect [object HTMLDivElement] useEffect
```

---
📌 小结：

| 类型           | 渲染前执行 | 渲染后执行             |
| ------------ | ----- | ----------------- |
| 状态、缓存类       | ✅     | ❌                 |
| DOM 副作用类（布局） | ❌     | ✅（layout 在 DOM 前） |
| 异步副作用类       | ❌     | ✅                 |
|              |       |                   |
### useState管理的数据被更新后，组件的操作
简短回答
> 只要你调用 `setState` 并且新值和旧值不同，React 就会重新渲染组件。

```jsx
function Counter() {
  const [count, setCount] = useState(0);

  console.log("组件渲染");

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>+1</button>
    </div>
  );
}
```
- 每次点击按钮，`setCount(count + 1)` 被调用；
    
- `count` 发生变化，组件函数会重新执行（重新渲染）；
    
- 控制台会打印多次 `"组件渲染"`，表示组件重新执行。
注意但是有两种情况不会发生改变
1. 新旧值相同
```jsx
setCount(count); // 如果 count 没变，React 不会重新渲染
```
2.多次setState且值未发生改变
```jsx
setCount(1);
setCount(1); // 第二次不会导致额外渲染
```
🧠 总结逻辑

|情况|会重新渲染吗|
|---|---|
|`useState` 的值变了（新旧不一样）|✅ 会|
|`useState` 的值没变（新旧一样）|❌ 不会|
|多次 set 相同值|❌ 不会|
|直接调用 `setState`（如 `setCount(1)`）|✅/❌ 看值是否变|
|修改的是 ref、变量、外部对象|❌ 不会（不会触发渲染）|

---

🔄 补充：重新渲染意味着什么？

- 函数组件会**整体重新执行**；
    
- 会重新计算 JSX 并更新虚拟 DOM；
    
- React 会使用 Diff 算法，**只更新变化的部分 DOM**。
    

---

如果你想**阻止无效渲染**，可以结合：

- `React.memo()`：函数组件的“纯组件”优化；
    
- `useMemo()`、`useCallback()`：优化值或函数引用；
    
- 或者 `useReducer()` 自定义更新逻辑。

### react组件更新的情况下，子组件会更新吗，父组件嘞
这是个非常关键的问题，关系到 **性能优化** 和 **渲染机制**。我来给你系统梳理一下：

---

✅ 简短回答

|问题|是否会重新渲染？|
|---|---|
|组件本身 `setState` 导致更新|✅ 组件会重新渲染|
|父组件更新时，子组件会重新渲染吗|✅ 默认会，除非使用了优化手段（如 `React.memo`）|
|子组件更新时，父组件会重新渲染吗|❌ 不会，React 是单向数据流|

---
 🧠 详细解释

✅ 1. 父组件更新 → 子组件会重新渲染（**默认行为**）

`function Parent() {   const [count, setCount] = useState(0);   return (     <div>       <Child />       <button onClick={() => setCount(count + 1)}>+1</button>     </div>   ); }  function Child() {   console.log("👶 Child 渲染");   return <div>子组件</div>; }`

**点击按钮 ➝ Parent 重新渲染 ➝ Child 也重新渲染（默认）**

> ✅ 因为 `Child()` 是在 `Parent()` 内调用的，父组件一重新执行，子组件也会执行。

---

### 🔒 如何“阻止”子组件不必要的渲染？

使用：

`const Child = React.memo(() => {   console.log("👶 Child 渲染");   return <div>子组件</div>; });`

✅ `React.memo()` 会对 props 做浅比较，只有 props 变化时才会重新渲染。

---

❌ 2. 子组件更新（如自己调用了 `setState`）→ **不会影响父组件**

`function Parent() {   console.log("👨 Parent 渲染");   return <Child />; }  function Child() {   const [count, setCount] = useState(0);   return <button onClick={() => setCount(count + 1)}>+1</button>; }`

> 点击子组件按钮后，**只有 `Child` 会重新渲染**，`Parent` 保持不变。

---

✅ 3. 子组件 props 变了 → 仍然会渲染

即使你用 `React.memo` 包裹子组件，如果父组件给子组件传了 **新的 props（即使值一样）**，子组件也可能渲染。

`function Parent() {   const [count, setCount] = useState(0);   const style = { color: "red" }; // 每次 render 都是新对象！    return <MemoChild style={style} />; }  const MemoChild = React.memo(({ style }) => {   console.log("子组件渲染");   return <div style={style}>子组件</div>; });`

✅ 如果 `style` 是个新对象（内存地址变了），即使内容没变，也会重新渲染。

**解决方式：使用 `useMemo` 保持引用不变。**

---

 📌 总结表

|情况|子组件会渲染？|父组件会渲染？|
|---|---|---|
|自己组件调用 `setState`|✅|❌|
|父组件 `setState`|✅ 默认会|✅|
|父组件 `setState`，但子组件是 `React.memo`|❌（如果 props 不变）|✅|
|子组件 `setState`|✅|❌|

---

🧰 优化建议

- 用 `React.memo` 包裹不变的子组件
    
- 用 `useCallback`、`useMemo` 保证传给子组件的 props 不变
    
- 避免不必要的状态提升（能放子组件就放子组件）
