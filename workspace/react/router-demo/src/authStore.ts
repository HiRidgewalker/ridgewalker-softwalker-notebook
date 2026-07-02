/**
 * 简单的 auth store（用 zustand 演示真实场景）
 */
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

type AuthState = {
  isLoggedIn: boolean;
  username: string | null;
  login: (username: string) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isLoggedIn: false,
      username: null,
      login: (username) => set({ isLoggedIn: true, username }),
      logout: () => set({ isLoggedIn: false, username: null }),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => sessionStorage), // 演示用 sessionStorage
    }
  )
);
