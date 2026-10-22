---
type: hub
topic: React 状态管理 (Zustand)
status: created
---

# Zustand 状态管理笔记

> 替代 Redux 的轻量状态管理方案。本笔记为新建基础版（基于通用知识）。
> 完整可运行 demo 见 [workspace/react/zustand-demo/](https://gitee.com/solowalker-limber/personal-knowledge-base/tree/master/workspace/react/zustand-demo)。

## 目录

1. 为什么选 zustand
2. 核心 API
3. Store 的组织
4. 进阶用法
5. 与 Redux 对比
6. 常见坑

---

## 1. 为什么选 zustand

- **极简**：核心 API 只有 `create`，几行代码一个 store
- **无样板代码**：不用写 action、reducer、dispatch
- **无 Provider 包裹**（默认）：store 是普通 JS 对象，直接 import 即可使用
- **支持 selector**：只在订阅的 slice 变化时重渲染
- **TypeScript 友好**：类型推断完善
- **体积小**：~1KB（gzip）

vs Redux：Redux 适合大型项目、有强中间件/时间旅行/调试需求；中小项目用 zustand 更轻。

---

## 2. 核心 API

### 2.1 创建 store

```ts
import { create } from 'zustand';

type CounterState = {
  count: number;
  increment: () => void;
  decrement: () => void;
  incrementBy: (n: number) => void;
};

const useCounterStore = create<CounterState>((set) => ({
  count: 0,
  increment: () => set((s) => ({ count: s.count + 1 })),
  decrement: () => set((s) => ({ count: s.count - 1 })),
  incrementBy: (n) => set((s) => ({ count: s.count + n })),
}));
```

### 2.2 在组件中使用

```tsx
function Counter() {
  const count = useCounterStore((s) => s.count);
  const increment = useCounterStore((s) => s.increment);

  return <button onClick={increment}>count is {count}</button>;
}
```

> **关键**：用 selector 取值时，**只在该 slice 变化时重渲染**。上面 `count` 不变时即使 `increment` 引用变了，组件也不会重渲染。

### 2.3 取多个值（性能）

```tsx
// ❌ 每次 store 任意变化都重渲染
const { count, increment } = useCounterStore();

// ✅ 只在 count 变时重渲染
const count = useCounterStore((s) => s.count);
const increment = useCounterStore((s) => s.increment);
```

### 2.4 改 state 的两种方式

```ts
// 1. 全量替换（传对象）
set({ count: 1 });

// 2. 增量合并（传函数返回部分 state）
set((s) => ({ count: s.count + 1 }));

// 3. 替换但保留不变字段（默认 shallow merge）
set({ count: 1 }); // 其他字段保留
```

### 2.5 异步 action

zustand 没有 thunk 中间件的概念，**直接写成 async 函数**：

```ts
type UserState = {
  user: User | null;
  loading: boolean;
  fetchUser: (id: string) => Promise<void>;
};

const useUserStore = create<UserState>((set) => ({
  user: null,
  loading: false,
  fetchUser: async (id) => {
    set({ loading: true });
    const res = await fetch(`/api/users/${id}`);
    const user = await res.json();
    set({ user, loading: false });
  },
}));
```

---

## 3. Store 的组织

### 3.1 拆分多个 store

按业务域拆，不要全塞一个 store：

```ts
// stores/useUserStore.ts
export const useUserStore = create<UserState>(...);

// stores/useCartStore.ts
export const useCartStore = create<CartState>(...);

// stores/useUIStore.ts
export const useUIStore = create<UIState>(...);
```

### 3.2 跨 store 调用

```ts
const useCartStore = create<CartState>((set, get) => ({
  items: [],
  addItem: (item) => {
    const user = useUserStore.getState().user; // 访问其他 store
    if (!user) return;
    set((s) => ({ items: [...s.items, item] }));
  },
}));
```

### 3.3 store 拆分到 slice

大型项目用 slice 模式（类似 Redux 的 combineReducers）：

```ts
// stores/createBearStore.ts
import { create } from 'zustand';

export const createBearStore = (set) => ({
  bears: 0,
  addBear: () => set((s) => ({ bears: s.bears + 1 })),
  eatFish: () => set((s) => ({ fishes: s.fishes - 1 })),
});

// stores/createFishStore.ts
import { create } from 'zustand';

export const createFishStore = (set) => ({
  fishes: 0,
  addFish: () => set((s) => ({ fishes: s.fishes + 1 })),
});

// stores/useBoundStore.ts
import { create } from 'zustand';
import { createBearStore } from './createBearStore';
import { createFishStore } from './createFishStore';

export const useBoundStore = create((...a) => ({
  ...createBearStore(...a),
  ...createFishStore(...a),
}));
```

---

## 4. 进阶用法

### 4.1 在组件外使用 store

```ts
// 不在 React 组件中也能读写
const count = useCounterStore.getState().count;
useCounterStore.getState().increment();

// 订阅变化
const unsub = useCounterStore.subscribe((s) => console.log(s.count));
```

### 4.2 持久化（中间件）

```ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      setAuth: (token, user) => set({ token, user }),
      logout: () => set({ token: null, user: null }),
    }),
    {
      name: 'auth-storage', // localStorage key
      storage: createJSONStorage(() => localStorage),
      partialize: (s) => ({ token: s.token, user: s.user }), // 只持久化部分
    }
  )
);
```

### 4.3 devtools 调试

```ts
import { devtools } from 'zustand/middleware';

const useStore = create<State>()(
  devtools(
    (set) => ({ ... }),
    { name: 'myStore' } // 在 Redux DevTools 中显示的名字
  )
);
```

### 4.4 immer 简化更新

```ts
import { immer } from 'zustand/middleware/immer';

const useStore = create<State>()(
  immer((set) => ({
    nested: { a: 1, b: { c: 2 } },
    update: () => set((s) => {
      s.nested.b.c = 3; // 直接改，immer 处理不可变
    }),
  }))
);
```

### 4.5 SSR 注意事项

- 服务端每个请求要**创建独立 store**，避免请求间共享
- 用 `zustand/middleware` 的 `combine` 或在请求作用域内创建

---

## 5. 与 Redux 对比

| 维度 | zustand | Redux (RTK) |
|---|---|---|
| 样板代码 | 极少 | 多（slice、reducer、action） |
| Provider | 不需要 | 需要 `<Provider store={store}>` |
| 异步处理 | 直接写 async | 需 thunk/saga |
| 调试 | devtools 中间件 | 原生 Redux DevTools（更强） |
| 时间旅行 | 弱 | 强 |
| 中间件生态 | 较少 | 极丰富 |
| 学习成本 | 低 | 中高 |
| 适合规模 | 中小项目、组件级状态 | 大型项目、跨团队协作 |
| TypeScript | 简单 | 较繁琐 |

> **选型建议**：项目状态 < 10 个 store、没有强时间旅行需求 → zustand；大型项目、需要严格规范 → RTK。

---

## 6. 常见坑

### 6.1 selector 返回新对象导致死循环

```tsx
// ❌ 每次 render 都返回新数组，触发重渲染
const items = useStore((s) => s.items.filter(x => x.active));

// ✅ 用 shallow 比较
import { useShallow } from 'zustand/react/useShallow';
const items = useStore(useShallow((s) => s.items.filter(x => x.active)));
```

### 6.2 store 里放组件实例 / DOM 引用

zustand 是**全局状态**，不要存组件级别的临时数据（如 ref、计时器）。这些用 `useRef` 或组件 state。

### 6.3 在 selector 里读其它 store

```tsx
// ❌ 跨 store selector 不在订阅范围内
const user = useUserStore((s) => s.user);
const items = useCartStore((s) => s.items.filter(x => x.userId === user.id));
```

> 跨 store 派生要么把派生结果存进 store，要么用 `useShallow` 或自定义 hook 组合。

### 6.4 不必要的整体订阅

```tsx
// ❌ 任意字段变都重渲染
const state = useStore();

// ✅ 精确订阅
const count = useStore((s) => s.count);
const increment = useStore((s) => s.increment);
```

---

## 关联笔记

- React 核心：[[I_React笔记]]
- Hooks：[[II_React Hooks笔记]]
- 路由：[[IV_React Router笔记]]
