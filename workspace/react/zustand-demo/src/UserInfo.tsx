/**
 * UserInfo 组件
 * 演示：异步 action + 持久化
 */
import { useState } from 'react';
import { useUserStore } from './store';

export function UserInfo() {
  const [idInput, setIdInput] = useState('1');
  const user = useUserStore((s) => s.user);
  const loading = useUserStore((s) => s.loading);
  const error = useUserStore((s) => s.error);
  const fetchUser = useUserStore((s) => s.fetchUser);
  const logout = useUserStore((s) => s.logout);

  return (
    <div style={{ padding: 16, border: '1px solid #ddd', borderRadius: 8 }}>
      <h2>User Info（持久化演示）</h2>
      <input
        value={idInput}
        onChange={(e) => setIdInput(e.target.value)}
        placeholder="用户 ID"
      />
      <button onClick={() => fetchUser(Number(idInput))} style={{ marginLeft: 8 }}>
        获取用户
      </button>
      <button onClick={logout} style={{ marginLeft: 8 }}>
        退出登录
      </button>

      {loading && <p>加载中...</p>}
      {error && <p style={{ color: 'red' }}>错误：{error}</p>}
      {user && (
        <div style={{ marginTop: 8 }}>
          <p>ID：{user.id}</p>
          <p>姓名：{user.name}</p>
          <p>邮箱：{user.email}</p>
          <p style={{ color: '#888', fontSize: 12 }}>
            （刷新页面后仍保留，演示 localStorage 持久化）
          </p>
        </div>
      )}
    </div>
  );
}
