/**
 * 演示：useTransition
 *
 * 场景：tab 切换属于低优先级，先保证输入响应
 */
import { useState, useTransition } from 'react';
import { BigList } from './BigList';

export function TransitionDemo() {
  const [tab, setTab] = useState<'home' | 'list'>('home');
  const [keyword, setKeyword] = useState('');
  const [isPending, startTransition] = useTransition();

  function selectTab(next: 'home' | 'list') {
    // 包在 startTransition 里：tab 切换是低优先级
    startTransition(() => {
      setTab(next);
    });
  }

  return (
    <section style={{ padding: 16, border: '1px solid #ddd', borderRadius: 8 }}>
      <h2>useTransition 演示</h2>

      <div>
        <button onClick={() => selectTab('home')}>Home</button>
        <button onClick={() => selectTab('list')} style={{ marginLeft: 8 }}>
          Big List
        </button>
        {isPending && <span style={{ marginLeft: 12, color: '#1677ff' }}>切换中...</span>}
      </div>

      <div style={{ marginTop: 12 }}>
        {tab === 'home' ? (
          <p>输入框在 Home/List 切换时仍保持响应（输入不属于 transition）：</p>
        ) : (
          <BigList query={keyword} />
        )}
      </div>

      <input
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        placeholder="搜索关键词"
        style={{ marginTop: 12, width: 240 }}
      />
    </section>
  );
}
