---
type: hub
topic: React Hooks
status: refactored
source:
  - 旧稿 (hooks 列表)
  - 旧稿 hooks useTransition() and useDeferredValue().md
---

# React Hooks 笔记

> 由旧稿 hooks 列表 + 由旧稿合并精炼版。
> 旧稿目录已清理，当前以本文为准。

## 目录

1. Hooks 通用规则
2. 状态与引用
3. 副作用与生命周期
4. 性能优化
5. 上下文与外部订阅
6. 路由相关 Hook（Router Hooks）
7. 自定义 Hook
8. 并发特性：`useTransition` 与 `useDeferredValue`
9. Hook 执行时机总表

---

## 1. Hooks 通用规则

> 只能在**组件顶层**或**自定义 Hook 内**调用 Hook，不能嵌套在 `if`、`for`、其它函数中。

原因：

- React 通过调用 Hook 的**顺序**关联状态和副作用
- 顺序不固定 → React 无法匹配之前的状态 → 状态错乱
- 自定义 Hook 本质是函数，内部可以调用其它 Hook，只要在组件顶层调用，顺序依然固定

---

## 2. 状态与引用

### 2.1 `useState`

返回 `[state, setState]`。调用 `setState` 且新值≠旧值时触发重渲染。

```jsx
const [count, setCount] = useState(0);
setCount(count + 1);
setCount(prev => prev + 1); // 函数式更新，基于上一次的值
```

### 2.2 `useReducer`

`useState` 的替代方案，适用于复杂状态逻辑（多子值、下一状态依赖上一状态）。

```jsx
function reducer(state, action) {
  switch (action.type) {
    case 'increment': return { count: state.count + 1 };
    case 'decrement': return { count: state.count - 1 };
    default: return state;
  }
}

const [state, dispatch] = useReducer(reducer, { count: 0 });
dispatch({ type: 'increment' });
```

### 2.3 `useRef`

返回一个可变的 ref 对象 `.current`，**修改不会触发重渲染**。

- 访问 DOM：`const ref = useRef(null); <div ref={ref} />`
- 跨渲染保存任意可变值（计时器 id、上一次值等）

---

## 3. 副作用与生命周期

### 3.1 `useEffect`

```jsx
useEffect(() => {
  // 副作用逻辑
  return () => {
    // 清除副作用（可选）
  };
}, [deps]);
```

| 依赖项 | 副作用函数执行时机 | 清除函数执行时机 |
|---|---|---|
| 无依赖 | 初始渲染 + 每次更新 | 组件卸载 + 下次副作用执行前 |
| 空数组 `[]` | 仅初始渲染 1 次 | 组件卸载 |
| 指定依赖 `[a, b]` | 初始渲染 + 任一依赖变化 | 同上 |

### 3.2 `useLayoutEffect`

同步执行，**在 DOM 更新之后、浏览器绘制之前**。用于同步读取/修改 DOM（如测量尺寸、避免闪烁）。

### 3.3 `useInsertionEffect`

比 `useLayoutEffect` 更早执行，专为 CSS-in-JS 库设计，普通业务用不到。

---

## 4. 性能优化

### 4.1 `useMemo`

缓存计算结果，依赖不变就跳过重算。

```jsx
const filtered = useMemo(
  () => list.filter(x => x.name.includes(keyword)),
  [list, keyword]
);
```

### 4.2 `useCallback`

缓存函数引用，依赖不变就返回同一个函数。常用于把函数传给 `React.memo` 包裹的子组件。

```jsx
const handleClick = useCallback(() => {
  doSomething(id);
}, [id]);
```

### 4.3 `React.memo`（不是 Hook）

对函数组件的 props 做浅比较，props 不变就不重渲染。

---

## 5. 上下文与外部订阅

### 5.1 `useContext`

获取上层 `<Context.Provider value={...}>` 注入的值。

```jsx
const theme = useContext(ThemeContext);
```

### 5.2 `useSyncExternalStore`

订阅外部 store（zustand、redux 等都用它实现）。一般业务不直接用，状态管理库内部会用到。

---

## 6. 路由相关 Hook（Router Hooks）

> 完整路由笔记见 [[IV_React Router笔记]]。这里只列 API 速查。

| Hook | 作用 |
|---|---|
| `useParams` | 获取动态路由参数（如 `/user/:id` 中的 `id`） |
| `useSearchParams` | 读写查询字符串（`?key=value`） |
| `useNavigate` | 编程式跳转 |
| `useLocation` | 获取当前 location 对象（pathname、search、state） |
| `useMatch` | 判断当前 URL 是否匹配某个 pattern |

---

## 7. 自定义 Hook

### 7.1 封装通用思路

```jsx
import { useState } from 'react';

function useToggle() {
  const [value, setValue] = useState(false);
  const toggle = () => setValue(v => !v);
  return { value, toggle };
}
```

四步法：

1. 声明一个以 `use` 打头的函数
2. 内部封装可复用逻辑
3. 把状态/回调 return 出去（对象或数组）
4. 在组件中调用并解构

### 7.2 复用价值

自定义 Hook 是**状态逻辑复用**的机制，与组件复用不同——它不返回 JSX，只返回数据和方法。

---

## 8. 并发特性：`useTransition` 与 `useDeferredValue`

> React 18+ 提供的"更新优先级调度工具"，适合**有部分更新可以稍后完成**的场景。

### 8.1 一句话区分

- `useTransition`：**延后"更新动作"**，把一批 state 更新标记为低优先级
- `useDeferredValue`：**延后"值的使用"**，让某些 UI 晚一点用上新值

### 8.2 `useTransition` 是什么

```jsx
const [isPending, startTransition] = useTransition();
```

- `isPending`：当前 transition 是否进行中
- `startTransition`：把某些 state 更新包起来

```jsx
function App() {
  const [tab, setTab] = useState('about');
  const [isPending, startTransition] = useTransition();

  function selectTab(next) {
    startTransition(() => setTab(next));
  }

  return (
    <>
      <button onClick={() => selectTab('about')}>About</button>
      <button onClick={() => selectTab('posts')}>Posts</button>
      {isPending && <p>切换中...</p>}
      {tab === 'about' ? <About /> : <HeavyPosts />}
    </>
  );
}
```

**常见误区**：

- ❌ 不是防抖（不是等 300ms 再执行）
- ❌ 不是 `setTimeout`
- ❌ 不会治好"写得很差的组件"
- ✅ 调整 React 处理更新的**优先级**

**关键限制**：过渡更新**不能用来控制文本输入**本身。输入框更新属于高优先级。

适合场景：tab 切换、路由切换、大区域刷新、过滤条件切换、表单提交后的大块 UI 更新。

### 8.3 `useDeferredValue` 是什么

```jsx
const deferredValue = useDeferredValue(value);
```

不是"延后设置 state"，而是：**有最新值 `value`，但某些地方先继续用旧值，晚点再跟上**。

```jsx
function SearchPage() {
  const [keyword, setKeyword] = useState('');
  const deferredKeyword = useDeferredValue(keyword);
  const isStale = keyword !== deferredKeyword;

  return (
    <>
      <input value={keyword} onChange={e => setKeyword(e.target.value)} />
      {isStale && <p>结果更新中...</p>}
      <SearchResults query={deferredKeyword} />
    </>
  );
}
```

适合场景：搜索框关键字、滚动/拖动产生的高频值、某个 props 驱动昂贵渲染。

### 8.4 与防抖（debounce）的区别

| 工具 | 控制什么 |
|---|---|
| debounce | 时间（连续触发时等一会儿再执行） |
| `useTransition` / `useDeferredValue` | 渲染优先级（重要的先来） |

这些工具**不是互斥的**，经常会一起用。

### 8.5 选哪个

- 主动发起一批 state 更新 → `useTransition`（且能拿到 `isPending`）
- 只有一个值，但希望重区域慢点跟上 → `useDeferredValue`（更简洁）
- 无法直接拿到 `set` 函数，或值来自 props/custom hook → 优先 `useDeferredValue`

### 8.6 完整实战示例

```jsx
import { useMemo, useState, useTransition, useDeferredValue } from 'react';

function BigList({ query }) {
  const items = useMemo(
    () => Array.from({ length: 20000 }, (_, i) => `Topic ${i}`)
      .filter(x => x.toLowerCase().includes(query.toLowerCase())),
    [query]
  );
  return <ul>{items.slice(0, 100).map(x => <li key={x}>{x}</li>)}</ul>;
}

export default function Demo() {
  const [input, setInput] = useState('');
  const [tab, setTab] = useState('search');
  const [isPending, startTransition] = useTransition();

  const deferredInput = useDeferredValue(input);
  const isStale = input !== deferredInput;

  return (
    <div>
      <button onClick={() => startTransition(() => setTab('search'))}>搜索</button>
      <button onClick={() => startTransition(() => setTab('about'))}>关于</button>
      {isPending && <p>页面切换中...</p>}
      {tab === 'search' ? (
        <>
          <input value={input} onChange={e => setInput(e.target.value)} />
          {isStale && <p>结果更新中...</p>}
          <BigList query={deferredInput} />
        </>
      ) : <div>关于页</div>}
    </div>
  );
}
```

完整可运行 demo 见 [example/react/hooks-demo/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/react/hooks-demo)。

---

## 9. Hook 执行时机总表

| Hook | 相对 JSX 渲染 | 说明 |
|---|---|---|
| `useState` | 渲染前 | 同步执行 |
| `useReducer` | 渲染前 | 同上 |
| `useMemo` | 渲染前 | 依赖变才重算 |
| `useCallback` | 渲染前 | 缓存函数引用 |
| `useRef` | 渲染前 | 初始化 ref |
| `useContext` | 渲染前 | 读取 context |
| `useId` | 渲染前 | React 18，生成稳定 ID |
| `useTransition` | 渲染前 | 启动 transition |
| `useDeferredValue` | 渲染前 | 延后值消费 |
| `useSyncExternalStore` | 渲染前 | 订阅外部 store |
| `useInsertionEffect` | 渲染前（比 useLayoutEffect 更早） | CSS-in-JS 插入 |
| `useLayoutEffect` | 渲染后、DOM 更新前（同步） | 布局测量 |
| `useEffect` | 渲染后、DOM 更新后（异步） | 异步副作用 |
| `useImperativeHandle` | 渲染后、DOM 更新前（forwardRef 内） | 暴露 ref |

执行流程：

1. 执行组件函数（含所有渲染前 hook）
2. 生成 JSX → 虚拟 DOM → 真实 DOM
3. `useLayoutEffect` 同步执行
4. 浏览器绘制 UI
5. `useEffect` 异步执行

---

## 关联笔记

- React 核心：[[I_React笔记]]
- 状态管理：[[III_Zustand状态管理笔记]]
- 路由：[[IV_React Router笔记]]
