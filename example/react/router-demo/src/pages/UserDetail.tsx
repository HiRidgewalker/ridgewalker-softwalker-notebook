/**
 * 演示：useParams 拿动态路由参数
 */
import { useParams, Link } from 'react-router-dom';

export function UserDetail() {
  const { id } = useParams<{ id: string }>();
  return (
    <div>
      <h2>用户详情</h2>
      <p>当前 ID：{id}</p>
      <p>（修改 URL 中的数字，观察页面更新）</p>
      <Link to="/user">← 返回列表</Link>
    </div>
  );
}
