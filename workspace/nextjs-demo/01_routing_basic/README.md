# 01_routing_basic · 路由基础 demo

演示 **Next.js 14 App Router 的文件式路由**。

## 涵盖知识点

- `app/page.tsx` → 根路由
- `app/layout.tsx` → 根布局（包裹所有页面）
- 静态段：`app/about/page.tsx` → `/about`
- 动态段：`app/blog/[slug]/page.tsx` → `/blog/:slug`
- 嵌套布局：`app/blog/` 下加 `layout.tsx`（可选）
- Catch-all：`app/docs/[...slug]/page.tsx`
- `<Link>` 客户端导航 + prefetch

## 路由速查表

| 文件 | URL |
|------|-----|
| `app/page.tsx` | `/` |
| `app/about/page.tsx` | `/about` |
| `app/blog/page.tsx` | `/blog` |
| `app/blog/[slug]/page.tsx` | `/blog/:slug` |
| `app/docs/[...slug]/page.tsx` | `/docs/a/b/c`（不匹配 `/docs`） |

## 运行

```bash
cd 01_routing_basic
npm install
npm run dev
# 打开 http://localhost:3000
```

## 关键观察点

1. 打开浏览器 DevTools → Network → 切换路由时只会下载**该路由的 RSC payload**，不会重新加载整个页面
2. 把鼠标 hover 到 `<Link>` 上 → Next.js 自动 prefetch 对应路由
3. 访问 `/docs` 会 404（因为用的是 Catch-all `[...slug]`，要让它也命中需要 `[[...slug]]`）
4. 访问 `/blog/some-text` 也会命中 `[slug]` 段

## 对应笔记

- [[II_Next.js 路由笔记]]
