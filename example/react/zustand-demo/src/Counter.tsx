/**
 * Counter 组件
 * 演示：selector 精确订阅 + 性能优化
 */
import { useCounterStore } from './store';

export function Counter() {
  // ✅ 只在 count 变时重渲染
  const count = useCounterStore((s) => s.count);
  const increment = useCounterStore((s) => s.increment);
  const decrement = useCounterStore((s) => s.decrement);
  const reset = useCounterStore((s) => s.reset);

  return (
    <div style={{ padding: 16, border: '1px solid #ddd', borderRadius: 8 }}>
      <h2>Counter</h2>
      <p>当前计数：{count}</p>
      <button onClick={increment}>+1</button>
      <button onClick={decrement} style={{ marginLeft: 8 }}>
        -1
      </button>
      <button onClick={reset} style={{ marginLeft: 8 }}>
        重置
      </button>
    </div>
  );
}
