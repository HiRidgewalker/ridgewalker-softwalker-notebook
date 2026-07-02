# 03_data_fetching · 数据获取 demo

演示 **Server Component 中数据获取的几种方式**。

## 涵盖知识点

- Server Component 顶层 `await fetch`（默认 force-cache）
- `Promise.all` 并行请求，消除瀑布流
- `export const revalidate = N` 实现 ISR
- `export const dynamic = 'force-dynamic'` + `cache: 'no-store'` 强制每次重取

## 路由对照

| 路径 | 行为 | 观察点 |
|------|------|--------|
| `/basic` | force-cache，多次刷新时间戳不变 | DevTools Network 看不到 fetch（直接复用缓存） |
| `/parallel` | 两个 fetch 并行 | 总耗时 = max(200ms) 而不是 sum |
| `/revalidate` | 30s 内缓存，30s 后重新生成 | 等 30s 后刷新看 timestamp 变化 |
| `/no-store` | 每次都重取 | timestamp 每次刷新都变 |

## 运行

```bash
cd 03_data_fetching
npm install
npm run dev
# 打开 http://localhost:3000
```

## 关键观察点

1. **/basic**：连续刷新 5 次，timestamp 都不变 —— 因为 Next.js 把 fetch 结果缓存了
2. **/parallel**：观察总耗时，应该接近 200ms（不是 400ms）
3. **/revalidate**：立刻刷新不会变，等 30 秒后再刷新，timestamp 才会更新
4. **/no-store**：每次刷新 timestamp 都变

## 对应笔记

- [[Hub/04_Next.js 数据获取与Server Actions笔记]]
- [[Hub/05_Next.js 渲染模式笔记]]
