/**
 * 演示：useSearchParams 读写查询字符串
 */
import { useSearchParams } from 'react-router-dom';

export function Search() {
  const [searchParams, setSearchParams] = useSearchParams();
  const keyword = searchParams.get('kw') ?? '';
  const page = Number(searchParams.get('page') ?? '1');

  return (
    <div>
      <h2>Search（useSearchParams 演示）</h2>
      <input
        value={keyword}
        onChange={(e) => setSearchParams({ kw: e.target.value, page: '1' })}
        placeholder="搜索关键词"
      />
      <button
        onClick={() => setSearchParams((prev) => {
          prev.set('page', String(page + 1));
          return prev;
        })}
        style={{ marginLeft: 8 }}
      >
        下一页
      </button>
      <p>
        当前关键词：<code>{keyword || '(空)'}</code>
      </p>
      <p>当前页码：{page}</p>
      <p style={{ color: '#888', fontSize: 12 }}>
        （注意浏览器地址栏的 ?kw=...&page=... 变化）
      </p>
    </div>
  );
}
