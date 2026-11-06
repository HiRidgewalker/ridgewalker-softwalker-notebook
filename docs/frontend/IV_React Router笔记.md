---
title: "React Router 笔记"
type: hub
topic: React Router
status: created
sidebar_position: 4
---

# React Router 笔记

> 基础版（基于通用知识）。完整可运行 demo 见 [example/react/router-demo/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/example/react/router-demo)。
>
> 当前主流使用 **React Router v6+**，本笔记以 v6 为主。

## 目录

1. 安装与基础
2. 路由配置：`<Routes>` 与 `<Route>`
3. 嵌套路由与 `<Outlet>`
4. 动态参数
5. 查询字符串
6. 编程式导航
7. 路由守卫（受保护路由）
8. 数据加载（loader）
9. 常见模式

---

## 1. 安装与基础

```bash
# v6
npm i react-router-dom
```

入口注入：

```tsx
import { BrowserRouter } from 'react-router-dom';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
);
```

> 另一种选择是 `HashRouter`（用 URL 的 hash 部分），用于静态托管（如 GitHub Pages）没有服务端 fallback 的场景。本地开发或支持 fallback 的部署用 `BrowserRouter`。

---

## 2. 路由配置：`<Routes>` 与 `<Route>`

v6 用 `<Routes>` 包裹一组 `<Route>`：

```tsx
import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import About from './pages/About';
import NotFound from './pages/NotFound';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/about" element={<About />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
```

> v6 不需要 `exact`，路径匹配算法变了（默认精确匹配）。

---

## 3. 嵌套路由与 `<Outlet>`

```tsx
function App() {
  return (
    <Routes>
      <Route path="/user" element={<UserLayout />}>
        <Route index element={<UserList />} />
        <Route path=":id" element={<UserDetail />} />
      </Route>
    </Routes>
  );
}

function UserLayout() {
  return (
    <div>
      <h1>用户模块</h1>
      {/* 子路由渲染在这里 */}
      <Outlet />
    </div>
  );
}
```

访问：

- `/user` → `<UserLayout><UserList /></UserLayout>`
- `/user/123` → `<UserLayout><UserDetail id="123" /></UserLayout>`

---

## 4. 动态参数：`useParams`

路由中以 `:` 开头的段：

```tsx
<Route path="/user/:id" element={<UserDetail />} />
```

组件中获取：

```tsx
import { useParams } from 'react-router-dom';

function UserDetail() {
  const { id } = useParams<{ id: string }>();
  return <div>用户 ID：{id}</div>;
}
```

> 老版本（v5）的 `useParams` 不传泛型，需要断言。

---

## 5. 查询字符串：`useSearchParams`

```tsx
import { useSearchParams } from 'react-router-dom';

function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const keyword = searchParams.get('kw') ?? '';
  const page = Number(searchParams.get('page') ?? '1');

  return (
    <>
      <input
        value={keyword}
        onChange={(e) => setSearchParams({ kw: e.target.value, page: 1 })}
      />
      <div>第 {page} 页</div>
    </>
  );
}
```

`setSearchParams` 支持传对象或函数式更新：

```tsx
// 对象形式（会覆盖其他参数）
setSearchParams({ kw: 'react' });

// 函数式更新（基于当前 params）
setSearchParams((prev) => {
  prev.set('page', '2');
  return prev;
});
```

---

## 6. 编程式导航：`useNavigate`

```tsx
import { useNavigate } from 'react-router-dom';

function LoginButton() {
  const navigate = useNavigate();

  function handleLogin() {
    // 登录成功后跳转
    navigate('/dashboard');
    // 替换历史（不留下当前页记录）
    navigate('/login', { replace: true });
    // 后退
    navigate(-1);
  }

  return <button onClick={handleLogin}>登录</button>;
}
```

---

## 7. 路由守卫（受保护路由）

v6 没有内置的 `<ProtectedRoute>`，自己包一个：

```tsx
import { Navigate, useLocation } from 'react-router-dom';

function RequireAuth({ children }: { children: React.ReactNode }) {
  const isLoggedIn = useAuthStore((s) => s.isLoggedIn);
  const location = useLocation();

  if (!isLoggedIn) {
    // 记录来源，登录后跳回
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return <>{children}</>;
}

// 使用
<Route
  path="/dashboard"
  element={
    <RequireAuth>
      <Dashboard />
    </RequireAuth>
  }
/>
```

---

## 8. 数据加载（loader）

v6.4+ 提供数据加载 API（受 Remix 启发）：

```tsx
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    children: [
      {
        path: 'users/:id',
        element: <UserDetail />,
        loader: async ({ params }) => {
          const res = await fetch(`/api/users/${params.id}`);
          return res.json();
        },
      },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}
```

组件中通过 `useLoaderData()` 拿数据：

```tsx
import { useLoaderData } from 'react-router-dom';

function UserDetail() {
  const user = useLoaderData() as User;
  return <div>{user.name}</div>;
}
```

> 普通项目可以用 zustand + `useEffect` 拉数据，loader 模式适合"路由即数据入口"的场景。

---

## 9. 常见模式

### 9.1 路由懒加载

```tsx
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./pages/Dashboard'));

<Route
  path="/dashboard"
  element={
    <Suspense fallback={<div>加载中...</div>}>
      <Dashboard />
    </Suspense>
  }
/>
```

### 9.2 404 页面

```tsx
<Route path="*" element={<NotFound />} />
```

### 9.3 当前路由高亮（NavLink）

```tsx
import { NavLink } from 'react-router-dom';

<NavLink
  to="/about"
  className={({ isActive }) => isActive ? 'active' : ''}
>
  关于
</NavLink>
```

### 9.4 路由参数变化时重新拉数据

```tsx
function UserDetail() {
  const { id } = useParams();
  const { data } = useUser(id); // 自定义 hook，依赖 id 变化重新请求
  return <div>{data?.name}</div>;
}
```

### 9.5 路由常量集中管理

```ts
// routes.ts
export const ROUTES = {
  home: '/',
  userList: '/user',
  userDetail: (id: string) => `/user/${id}`,
} as const;
```

---

## 常见问题

### 路由变了组件没更新？

检查是否在组件外用了模块级变量读取路由信息（应该是组件内用 `useLocation`、`useParams` 等 hook）。

### `useNavigate` 在异步回调里报错？

`navigate` 是稳定的，但 `useEffect` 清理函数里调用 `navigate` 可能在组件卸载后执行。一般不构成问题，React Router 会忽略无效跳转。

### 静态部署刷新 404？

用 `HashRouter`（路径用 `#/`），或部署平台配置 fallback 到 `index.html`。

---

## 关联笔记

- React 核心：[I_React笔记](./I_React笔记.md)
- Hooks：[II_React Hooks笔记](./II_React%20Hooks笔记.md)
- 状态管理：[III_Zustand状态管理笔记](./III_Zustand状态管理笔记.md)
