---
title: "React 笔记"
sidebar_position: 1
---

# React 笔记

> 由旧稿重新整理版本。聚焦 React 核心（组件、JSX、通信、更新规律）。
> Hooks 已拆到 [II_React Hooks笔记](./II_React%20Hooks笔记.md)，状态管理见 [III_Zustand状态管理笔记](./III_Zustand状态管理笔记.md)，路由见 [IV_React Router笔记](./IV_React%20Router笔记.md)。
> 旧稿目录已清理，当前以本文为准。

## 目录

1. 组件基础与编码约定
2. JSX 渲染机制
3. 组件通信
4. 组件更新规律
5. 常见问题

---

## 1. 组件基础与编码约定

### 1.1 命名与组织

- 组件首字母**必须大写**，推荐组件名与文件名一致
- 可通过 `import` 方式直接引入 CSS、图片，前端构建工具（Vite/Webpack）会自动处理

```jsx
import { useState } from 'react';
import '@/styles/main.scss';
import reactLogo from '@/assets/react.svg';

function AppTemplate() {
  const [count, setCount] = useState(0);
  return (
    <div className="app">
      <img src={reactLogo} className="logo react" alt="React logo" />
      <h1>React + Vite</h1>
      <button onClick={() => setCount(count + 1)}>count is {count}</button>
    </div>
  );
}

export default AppTemplate;
```

### 1.2 组件的两种写法

- **函数组件**（主流）：普通函数返回 JSX，配合 Hooks 管理状态
- **类组件**（老项目）：继承 `React.Component`，通过 `this.state` 和生命周期方法管理

新项目一律用函数组件。

---

## 2. JSX 渲染机制

### 2.1 渲染顺序

**先执行 JS（函数逻辑），再生成并渲染 return 的 JSX。**

```jsx
function MyComponent() {
  console.log("组件函数执行");      // 1. 先执行
  const now = new Date().toLocaleTimeString();
  return <div>当前时间是：{now}</div>; // 2. 再渲染 JSX
}
```

首次挂载的执行顺序：

| 步骤 | 内容 |
|---|---|
| 1 | 执行组件函数（含 `useState`、`useRef`、`useMemo` 等所有 render 阶段 hook） |
| 2 | return JSX，被转成 `React.createElement(...)` 调用 |
| 3 | 构建虚拟 DOM → 真实 DOM，浏览器渲染 |
| 4 | `useLayoutEffect` 同步执行（DOM 已更新，浏览器尚未绘制） |
| 5 | 浏览器绘制 UI |
| 6 | `useEffect` 异步执行（DOM 更新之后） |

### 2.2 Hook 执行时机速查

| 类型 | 渲染前 | 渲染后 |
|---|---|---|
| 状态/缓存类（useState、useReducer、useMemo、useCallback、useRef、useContext、useId、useTransition、useDeferredValue、useSyncExternalStore） | ✅ | ❌ |
| DOM 副作用-布局（useLayoutEffect） | ❌ | ✅（DOM 更新后，浏览器绘制前） |
| DOM 副作用-插入（useInsertionEffect） | ❌ | ✅（比 useLayoutEffect 更早） |
| 异步副作用（useEffect） | ❌ | ✅（DOM 更新后） |
| ref 暴露（useImperativeHandle） | ❌ | ✅（forwardRef 内） |

完整 Hook 体系见 [II_React Hooks笔记](./II_React%20Hooks笔记.md)。

---

## 3. 组件通信

### 3.1 父 → 子

通过 `props` 传递。`props` 可传任意合法数据（数字、字符串、布尔值、数组、对象、函数、JSX）。

```jsx
function Son({ name, age }) {
  return <div>{name}--{age}</div>;
}

function App() {
  return <Son name="app" age={16} />;
}
```

> **props 是只读对象**。子组件只能读取，不能直接修改；父组件的数据只能由父组件修改。

### 3.2 特殊 prop：`children`

组件标签内嵌套的内容会自动作为 `children` 传入。

```jsx
function MyComponent({ children }) {
  return <div>{children}</div>;
}

<MyComponent>
  <h1>Hello</h1>
  <p>段落</p>
</MyComponent>
```

### 3.3 子 → 父

核心是**状态提升**：父组件定义一个函数，通过 `props` 传给子组件，子组件调用时把数据作为参数传回去。

```jsx
function Son({ onGetMsg }) {
  const sonMsg = 'this is son msg';
  return <button onClick={() => onGetMsg(sonMsg)}>send</button>;
}

function App() {
  const [name, setName] = useState('');
  return (
    <div>
      <Son onGetMsg={setName} />
      <div>收到：{name}</div>
    </div>
  );
}
```

### 3.4 跨级组件通信

**本质仍是状态提升**——把状态放到最近的共同祖先，通过 `props` 一层层传下去（或传函数回去）。

更复杂的场景（深层嵌套）使用：

- `useContext`（React 内置）
- 状态管理库（项目用 zustand，见 [III_Zustand状态管理笔记](./III_Zustand状态管理笔记.md)）

---

## 4. 组件更新规律

### 4.1 重新渲染规则

| 触发条件 | 是否重新渲染 |
|---|---|
| 自己组件调用 `setState`（新值与旧值不同） | ✅ 会 |
| `setState` 新值与旧值相同 | ❌ 不会 |
| 多次 `setState` 设置相同值 | ❌ 不会 |
| 修改 ref、普通变量、外部对象 | ❌ 不会（不触发渲染） |
| 父组件 `setState` | ✅ 默认会，子组件也跟着重渲染 |
| 子组件 `setState` | ❌ 不会影响父组件 |
| 父组件 `setState`，子组件用 `React.memo` 包裹 | ❌（props 不变时） |

> React 是**单向数据流**：数据只能从父组件往下流。

### 4.2 重新渲染意味着什么

- 函数组件整体重新执行
- 重新计算 JSX，更新虚拟 DOM
- 用 Diff 算法**只更新变化的部分 DOM**

### 4.3 阻止无效渲染

- `React.memo`：对函数组件 props 做浅比较
- `useMemo` / `useCallback`：保持引用稳定，避免传给子组件的 props 每次都是新对象
- 状态尽量放子组件本地（能不提升就不提升）

```jsx
// 父组件每次 render 都会创建新对象 → 子组件 memo 失效
function Parent() {
  const style = { color: 'red' };
  return <MemoChild style={style} />;
}

// 用 useMemo 保持引用稳定
function Parent() {
  const style = useMemo(() => ({ color: 'red' }), []);
  return <MemoChild style={style} />;
}
```

---

## 5. 常见问题

### 5.1 组件挂载时，是先执行 JS 还是先渲染 HTML？

**先执行 JS（函数逻辑），再生成并渲染 return 的 JSX。**

详见 [2. JSX 渲染机制](#2-jsx-渲染机制)。

### 5.2 子组件会跟着父组件更新吗？

默认会。父组件重渲染时，所有子组件（未用 `React.memo` 优化）都会跟着重渲染。

用 `React.memo` + `useMemo` / `useCallback` 阻止不必要的渲染。

### 5.3 `setState` 不会触发重新渲染的场景

- 新值与旧值相同
- 多次 set 相同值
- 修改的是 ref、普通变量、外部对象

### 5.4 受控 vs 非受控组件

- **受控**：表单值由 React state 持有，通过 `onChange` 同步（如 `<input value={x} onChange={...} />`）
- **非受控**：用 `ref` 直接读取 DOM 值（如 `useRef` + `defaultValue`）

新代码推荐受控，行为可预测。

---

## 关联笔记

- Hooks 完整指南：[II_React Hooks笔记](./II_React%20Hooks笔记.md)
- 状态管理：[III_Zustand状态管理笔记](./III_Zustand状态管理笔记.md)
- 路由：[IV_React Router笔记](./IV_React%20Router笔记.md)
- TypeScript 类型：[TypeScript类型标注与React类型笔记](../typescript/TypeScript类型标注与React类型笔记.md)
