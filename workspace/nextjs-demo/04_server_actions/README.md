# 04_server_actions · Server Actions demo

演示 **Next.js 14 中 Server Action 的几种使用方式**。

## 涵盖知识点

- `'use server'` 标记整个文件为 Server Actions
- 原生 `<form action={serverAction}>` —— 无需 JS 也能提交（渐进增强）
- `action.bind(null, arg)` 注入参数
- Client 组件 + `useActionState` 拿到 `isPending` 和 action 返回值
- Client 组件手动调用 Server Action（搭配 `useTransition`）

## 路由对照

| 路径 | 演示内容 |
|------|----------|
| `/` | 入口 |
| `/simple-form` | 纯 Server 页面 + 原生 form（增加 / 删除） |
| `/client-form` | Server 页面 + Client 表单 + `useActionState` |
| `/toggle` | Server 页面 + Client 按钮组件手动调用 action |

## 运行

```bash
cd 04_server_actions
npm install
npm run dev
# 打开 http://localhost:3000
```

## 关键观察点

1. **`/simple-form`**：打开 DevTools，禁用 JavaScript，刷新页面 —— 表单仍能提交（渐进增强）。`deleteTodo.bind(null, t.id)` 把 id 绑定到 action。
2. **`/client-form`**：提交时按钮显示"提交中..."，下方显示 action 返回的消息。
3. **`/toggle`**：弹窗输入标题后调用 action，列表自动更新（因为 Server Action 内 `revalidatePath` 了）。

## 数据是"进程内"的

这个 demo 的 `db` 是模块级变量，**只在 dev 进程存活**。
- `next dev` 时数据保持
- `next build && next start` 时数据也保持
- 重启进程 → 数据回到初始

真实场景换成数据库 / 持久层即可。

## 对应笔记

- [[04_Next.js 数据获取与Server Actions笔记]]
