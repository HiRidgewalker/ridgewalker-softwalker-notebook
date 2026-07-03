/**
 * 演示：useDeferredValue
 *
 * 场景：搜索框输入流畅，搜索结果区晚一点跟上
 */
import { useDeferredValue, useState } from 'react';
import { BigList } from './BigList';

export function DeferredDemo() {
  const [keyword, setKeyword] = useState('');
  // deferredKeyword 在 React "空下来"时再更新
  const deferredKeyword = useDeferredValue(keyword);
  const isStale = keyword !== deferredKeyword;

  return (
    <section style={{ padding: 16, border: '1px solid #ddd', borderRadius: 8 }}>
      <h2>useDeferredValue 演示</h2>
      <p>快速输入文本，观察 BigList 滞后更新：</p>
      <input
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        placeholder="输入关键词"
        style={{ width: 240 }}
      />
      {isStale && (
        <p style={{ color: '#fa8c16' }}>结果更新中...</p>
      )}
      <BigList query={deferredKeyword} />
    </section>
  );
}
