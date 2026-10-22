import { Link } from 'react-router-dom';

const USERS = [
  { id: 1, name: 'Alice' },
  { id: 2, name: 'Bob' },
  { id: 3, name: 'Charlie' },
];

export function UserList() {
  return (
    <div>
      <h2>用户列表（嵌套路由 index）</h2>
      <ul>
        {USERS.map((u) => (
          <li key={u.id}>
            <Link to={`/user/${u.id}`}>{u.name}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
