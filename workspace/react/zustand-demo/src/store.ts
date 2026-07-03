/**
 * Zustand store 集合
 *
 * 涵盖：
 * - 基础 create + 增量更新
 * - 异步 action
 * - persist 持久化中间件
 * - devtools 调试
 * - immer 简化不可变更新
 * - selector 精确订阅
 */
import { create } from 'zustand';
import { devtools, persist, createJSONStorage } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

// ============ 1. 基础 store：计数器 ============
type CounterState = {
  count: number;
  increment: () => void;
  decrement: () => void;
  incrementBy: (n: number) => void;
  reset: () => void;
};

export const useCounterStore = create<CounterState>()(
  devtools(
    (set) => ({
      count: 0,
      increment: () => set((s) => ({ count: s.count + 1 })),
      decrement: () => set((s) => ({ count: s.count - 1 })),
      incrementBy: (n) => set((s) => ({ count: s.count + n })),
      reset: () => set({ count: 0 }),
    }),
    { name: 'counter-store' }
  )
);

// ============ 2. 异步 action + 持久化：用户信息 ============
type User = { id: number; name: string; email: string };

type UserState = {
  user: User | null;
  loading: boolean;
  error: string | null;
  fetchUser: (id: number) => Promise<void>;
  logout: () => void;
};

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      user: null,
      loading: false,
      error: null,
      fetchUser: async (id) => {
        set({ loading: true, error: null });
        try {
          // 模拟接口
          await new Promise((r) => setTimeout(r, 500));
          const user: User = {
            id,
            name: `User ${id}`,
            email: `user${id}@example.com`,
          };
          set({ user, loading: false });
        } catch (e) {
          set({ error: String(e), loading: false });
        }
      },
      logout: () => set({ user: null }),
    }),
    {
      name: 'user-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (s) => ({ user: s.user }), // 只持久化 user
    }
  )
);

// ============ 3. Immer 简化嵌套更新：购物车 ============
type CartItem = { id: number; name: string; qty: number };

type CartState = {
  items: CartItem[];
  addItem: (item: Omit<CartItem, 'qty'>) => void;
  increase: (id: number) => void;
  removeItem: (id: number) => void;
  clear: () => void;
};

export const useCartStore = create<CartState>()(
  immer((set) => ({
    items: [],
    addItem: (item) =>
      set((s) => {
        const existing = s.items.find((x) => x.id === item.id);
        if (existing) {
          existing.qty += 1;
        } else {
          s.items.push({ ...item, qty: 1 });
        }
      }),
    increase: (id) =>
      set((s) => {
        const item = s.items.find((x) => x.id === id);
        if (item) item.qty += 1;
      }),
    removeItem: (id) =>
      set((s) => {
        s.items = s.items.filter((x) => x.id !== id);
      }),
    clear: () => set((s) => ({ items: [] })),
  }))
);
