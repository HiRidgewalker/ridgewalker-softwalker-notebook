/**
 * 路由守卫：未登录用户重定向到 /login，并记录来源
 */
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from './authStore';

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const isLoggedIn = useAuthStore((s) => s.isLoggedIn);
  const location = useLocation();

  if (!isLoggedIn) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return <>{children}</>;
}
