# React 全家桶 demo

本目录对应 `Hub/` 下的 React 笔记，提供可运行示例。

## 目录结构

```
workspace/react/
├── zustand-demo/          ← Zustand 状态管理演示
│   ├── package.json
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── Counter.tsx        # 基础 store + selector
│       ├── UserInfo.tsx       # 异步 action
│       └── store.ts           # 持久化 + devtools + immer 集成示例
│
├── router-demo/           ← React Router v6 演示
│   ├── package.json
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── routes.tsx
│       ├── RequireAuth.tsx    # 路由守卫
│       ├── Layout.tsx         # 嵌套路由 + Outlet
│       └── pages/
│           ├── Home.tsx
│           ├── About.tsx
│           ├── UserList.tsx
│           ├── UserDetail.tsx # useParams
│           ├── Search.tsx     # useSearchParams
│           ├── Dashboard.tsx  # 受保护页面
│           ├── Login.tsx      # useNavigate
│           └── NotFound.tsx
│
└── hooks-demo/            ← React 18+ Hooks 并发特性
    ├── package.json
    ├── index.html
    ├── vite.config.ts
    ├── tsconfig.json
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── TransitionDemo.tsx # useTransition
        ├── DeferredDemo.tsx   # useDeferredValue
        └── BigList.tsx        # 重渲染组件
```

## 运行约定

每个 demo 都是独立的 Vite + React + TypeScript 项目。

### 准备

```bash
cd workspace/react/zustand-demo   # 或 router-demo / hooks-demo
npm install
```

### 启动

```bash
npm run dev
```

打开 `http://localhost:5173`。

### 构建

```bash
npm run build
npm run preview
```

## 关联笔记

- [[01_React笔记]]
- [[02_React Hooks笔记]]
- [[03_Zustand状态管理笔记]]
- [[04_React Router笔记]]
