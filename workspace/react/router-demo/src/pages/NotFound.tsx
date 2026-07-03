import { Link } from 'react-router-dom';

export function NotFound() {
  return (
    <div>
      <h1>404 - 页面不存在</h1>
      <Link to="/">回到首页</Link>
    </div>
  );
}
