/**
 * Cart 组件
 * 演示：immer 中间件 - 嵌套结构直接改
 */
import { useCartStore } from './store';

const SAMPLE_ITEMS = [
  { id: 1, name: 'React 入门' },
  { id: 2, name: 'TypeScript 实战' },
  { id: 3, name: 'Vite 工程化' },
];

export function Cart() {
  const items = useCartStore((s) => s.items);
  const addItem = useCartStore((s) => s.addItem);
  const increase = useCartStore((s) => s.increase);
  const removeItem = useCartStore((s) => s.removeItem);
  const clear = useCartStore((s) => s.clear);

  return (
    <div style={{ padding: 16, border: '1px solid #ddd', borderRadius: 8 }}>
      <h2>Cart（immer 演示）</h2>

      <div>
        <strong>商品列表：</strong>
        {SAMPLE_ITEMS.map((item) => (
          <button
            key={item.id}
            onClick={() => addItem(item)}
            style={{ marginLeft: 8 }}
          >
            + {item.name}
          </button>
        ))}
      </div>

      <h3>购物车：</h3>
      {items.length === 0 && <p>购物车为空</p>}
      {items.map((item) => (
        <div key={item.id} style={{ marginBottom: 4 }}>
          {item.name} × {item.qty}
          <button onClick={() => increase(item.id)} style={{ marginLeft: 8 }}>
            +
          </button>
          <button onClick={() => removeItem(item.id)} style={{ marginLeft: 4 }}>
            删除
          </button>
        </div>
      ))}

      {items.length > 0 && (
        <button onClick={clear} style={{ marginTop: 8 }}>
          清空
        </button>
      )}
    </div>
  );
}
