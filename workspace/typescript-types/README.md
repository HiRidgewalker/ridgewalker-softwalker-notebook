# workspace/typescript-types

TypeScript + React 类型笔记的配套 demo。所有文件都是**纯 TS 类型演示**，不依赖运行时。

## 目录

| 文件 | 知识点 |
|---|---|
| `01_inference_vs_annotation.ts` | 推断 vs 标注的对比、空值场景 |
| `02_react_hooks_types.ts` | useState / useReducer / useContext / useRef / useImperativeHandle |
| `03_event_types.ts` | React 事件类型全集（Change/Mouse/Keyboard/Focus/Pointer/Drag/Wheel/Clipboard） |
| `04_common_pitfalls.ts` | 空数组推断、联合 widen、as 滥用、satisfies / as const 修复 |

## 如何使用

### 方式 A：纯阅读

直接看 `.ts` 文件，每个文件顶部注释说明涵盖的知识点。

### 方式 B：用 tsc 验证（推荐）

```bash
cd workspace/typescript-types
npx -y typescript@5 --init --strict
# 把 demo 文件加到 tsconfig 的 include，或者直接命令行编译
npx tsc --noEmit 01_inference_vs_annotation.ts 02_react_hooks_types.ts 03_event_types.ts 04_common_pitfalls.ts
```

打开任意文件，把鼠标悬停在变量上即可看到推断类型；故意写错的行会有红色波浪线。

> demo 不依赖 React 运行时，纯 TS 即可验证类型。如果你想跑真实的 React Hooks 代码，
> 需要单独搭一个 Vite + React + TS 工程（不在本 demo 范围内）。

### 方式 C：TS Playground

复制文件内容到 https://www.typescriptlang.org/play 即可看到类型推断。