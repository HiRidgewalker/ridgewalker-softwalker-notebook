import { TransitionDemo } from './TransitionDemo';
import { DeferredDemo } from './DeferredDemo';

export default function App() {
  return (
    <div style={{ maxWidth: 720, margin: '0 auto', padding: 16, fontFamily: 'sans-serif' }}>
      <h1>React 18+ Hooks 并发特性演示</h1>
      <p>对应笔记：<code>Hub/02_React Hooks笔记.md</code></p>
      <DeferredDemo />
      <div style={{ height: 16 }} />
      <TransitionDemo />
    </div>
  );
}
