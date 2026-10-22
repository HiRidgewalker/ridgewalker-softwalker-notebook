import { useAuthStore } from '../authStore';

export function Dashboard() {
  const username = useAuthStore((s) => s.username);
  return (
    <div>
      <h1>Dashboard（受保护页面）</h1>
      <p>欢迎，{username}！</p>
      <p>未登录用户访问此页会被重定向到 /login。</p>
    </div>
  );
}
