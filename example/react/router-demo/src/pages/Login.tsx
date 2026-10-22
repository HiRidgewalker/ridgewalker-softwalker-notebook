/**
 * 演示：useNavigate 编程式跳转 + state.from 来源记录
 */
import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../authStore';

type LocationState = { from?: { pathname: string } };

export function Login() {
  const [name, setName] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const login = useAuthStore((s) => s.login);

  const from = (location.state as LocationState)?.from?.pathname ?? '/dashboard';

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    login(name.trim());
    navigate(from, { replace: true });
  }

  return (
    <div>
      <h1>Login</h1>
      <p style={{ color: '#888' }}>登录后将跳转回：{from}</p>
      <form onSubmit={handleSubmit}>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="用户名"
          autoFocus
        />
        <button type="submit" style={{ marginLeft: 8 }}>
          登录
        </button>
      </form>
      <p style={{ fontSize: 12, color: '#888', marginTop: 8 }}>
        （任意非空用户名都能登录，这是 demo）
      </p>
    </div>
  );
}
