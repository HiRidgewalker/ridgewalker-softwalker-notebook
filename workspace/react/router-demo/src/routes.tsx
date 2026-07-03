/**
 * 路由配置
 *
 * 演示：
 * - 嵌套路由（Layout + Outlet）
 * - 动态参数 :id
 * - index 路由
 * - 路由守卫 RequireAuth
 * - 404 fallback (*)
 */
import { createBrowserRouter } from 'react-router-dom';
import { Layout } from './Layout';
import { RequireAuth } from './RequireAuth';
import { Home } from './pages/Home';
import { About } from './pages/About';
import { UserList } from './pages/UserList';
import { UserDetail } from './pages/UserDetail';
import { Search } from './pages/Search';
import { Dashboard } from './pages/Dashboard';
import { Login } from './pages/Login';
import { NotFound } from './pages/NotFound';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'about', element: <About /> },
      {
        path: 'user',
        children: [
          { index: true, element: <UserList /> },
          { path: ':id', element: <UserDetail /> },
        ],
      },
      { path: 'search', element: <Search /> },
      {
        path: 'dashboard',
        element: (
          <RequireAuth>
            <Dashboard />
          </RequireAuth>
        ),
      },
      { path: 'login', element: <Login /> },
      { path: '*', element: <NotFound /> },
    ],
  },
]);
