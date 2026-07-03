import { Counter } from './Counter';
import { UserInfo } from './UserInfo';
import { Cart } from './Cart';

export default function App() {
  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: 16, fontFamily: 'sans-serif' }}>
      <h1>Zustand Demo</h1>
      <p>
        对应笔记：<code>Hub/03_Zustand状态管理笔记.md</code>
      </p>
      <Counter />
      <div style={{ height: 16 }} />
      <UserInfo />
      <div style={{ height: 16 }} />
      <Cart />
    </div>
  );
}
