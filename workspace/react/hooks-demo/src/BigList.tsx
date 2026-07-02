/**
 * 模拟"渲染很重的列表"
 * 接收 query 做过滤，故意在每次 render 做 2 万次字符串处理
 */
import { useMemo } from 'react';

type Props = { query: string };

export function BigList({ query }: Props) {
  const items = useMemo(() => {
    // 模拟昂贵计算
    const all = Array.from({ length: 20000 }, (_, i) => `React Topic ${i}`);
    return all.filter((x) => x.toLowerCase().includes(query.toLowerCase()));
  }, [query]);

  return (
    <div
      style={{
        height: 200,
        overflow: 'auto',
        border: '1px solid #ddd',
        padding: 8,
      }}
    >
      <p style={{ color: '#888', fontSize: 12 }}>
        过滤结果：{items.length} 条（渲染前 50 条）
      </p>
      <ul style={{ margin: 0, paddingLeft: 20 }}>
        {items.slice(0, 50).map((x) => (
          <li key={x}>{x}</li>
        ))}
      </ul>
    </div>
  );
}
