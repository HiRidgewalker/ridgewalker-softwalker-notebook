# JS Demo 配套示例

本目录为 `Hub/01_JavaScript笔记.md` / `Hub/02_JavaScript进阶笔记.md` / `Hub/03_JavaScript异步与模块笔记.md` 的可运行示例。

## 目录结构

```
js-demo/
├── 01_basics/          基础语法（变量 / 类型 / 数组方法）
├── 02_es6/             ES6+（箭头函数 / 解构 / 展开 / Set / Map）
├── 03_scope_closure/   作用域 / 闭包 / this
├── 04_oop/             原型链 / class / 继承
├── 05_async/           Promise / async-await / 事件循环
└── 06_module/          ES Module 导入导出
```

## 运行方式

**不需要 Python venv，直接用 Node 即可。**

```bash
# 单文件 demo（01~05 子目录下的 .js）
node workspace/js-demo/01_basics/01_variables_and_types.js
node workspace/js-demo/05_async/02_async_await_eventloop.js

# 06_module 必须以 ESM 模式运行（子目录已配 package.json 的 "type": "module"）
cd workspace/js-demo/06_module && node app.js
```

## 与 Hub 笔记的对应关系

| 子目录 | 对应 Hub 笔记章节 |
|---|---|
| 01_basics | `Hub/01` 第三、四、五、六、九章 |
| 02_es6 | `Hub/01` 第八、十一、十二章 |
| 03_scope_closure | `Hub/02` 第一、二、三、四章 |
| 04_oop | `Hub/02` 第五、六章 |
| 05_async | `Hub/03` 第二、三、四、五章 |
| 06_module | `Hub/03` 第六、七章 |
