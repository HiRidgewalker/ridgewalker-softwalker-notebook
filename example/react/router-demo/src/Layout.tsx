/**
 * 嵌套路由 Layout：含导航栏 + Outlet
 */
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuthStore } from './authStore';

export function Layout() {
  const navigate = useNavigate();
  const isLoggedIn = useAuthStore((s) => s.isLoggedIn);
  const username = useAuthStore((s) => s.username);
  const logout = useAuthStore((s) => s.logout);

  function handleLogout() {
    logout();
    navigate('/');
  }

  const linkStyle = ({ isActive }: { isActive: boolean }) => ({
    marginRight: 12,
    fontWeight: isActive ? 'bold' : 'normal',
    color: isActive ? '#1677ff' : '#333',
  });

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: 16, fontFamily: 'sans-serif' }}>
      <nav style={{ padding: 12, background: '#f5f5f5', borderRadius: 8, marginBottom: 16 }}>
        <NavLink to="/" end style={linkStyle}>
          Home
        </NavLink>
        <NavLink to="/about" style={linkStyle}>
          About
        </NavLink>
        <NavLink to="/user" style={linkStyle}>
          Users
        </NavLink>
        <NavLink to="/search" style={linkStyle}>
          Search
        </NavLink>
        <NavLink to="/dashboard" style={linkStyle}>
          Dashboard
        </NavLink>

        <span style={{ float: 'right' }}>
          {isLoggedIn ? (
            <>
              <span style={{ marginRight: 8 }}>👤 {username}</span>
              <button onClick={handleLogout}>退出</button>
            </>
          ) : (
            <NavLink to="/login">登录</NavLink>
          )}
        </span>
      </nav>

      {/* 子路由在这里渲染 */}
      <Outlet />
    </div>
  );
}
