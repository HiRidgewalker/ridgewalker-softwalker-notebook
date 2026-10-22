# 代码演示外置 workspace 模式

## 规则

知识库中涉及的代码示例，如果具备"可运行 + 有演示价值"的特征，应提炼到 `workspace/` 目录下作为可执行 demo，原文通过**远程 git 链接**引用，而非保留大段代码块。

## 原因

用户希望知识更可验证、可交互——读者能真正运行测试代码，而不只是阅读；纯文本代码块无法体现运行环境差异（如 sys.path、包冲突等）。

## 如何应用

### 1. 原文处理

只保留以下内容：

- 概念定义
- 关键结论
- 表格对比
- 外部教程链接（菜鸟教程、官方文档）
- 个人经验总结

### 2. demo 文件存放

- 放 `workspace/<技术域>/<主题>/`
- 目录结构尽量贴近真实工程结构
- 每个 demo 文件顶部 docstring 说明涵盖的知识点和运行方式
- 文件命名使用小写 + 下划线（Python 风格）

### 3. 远程链接形式

```
[workspace/.../demo.py](https://gitee.com/solowalker-limber/personal-knowledge-base/blob/master/workspace/.../demo.py)
```

- 前缀固定为当前 git 仓库 URL
- 使用 `blob/master/` 在 gitee 在线查看代码
- 使用 `raw/master/` 直接获取原始内容
- 整个目录的演示使用 `tree/master/` 形式

### 4. OCR 截图

内容已记录的前提下，删除截图本身（信息冗余，obsidian 渲染时也容易失效）。

### 5. 合并总览文件

- 多个相关笔记合并后的精炼总览放 `hub/` 下
- 作为该主题的"核心入口"被引用
- 历史原稿归档到 `hub/_archive/`，保留以防回退

## 当前 git 仓库信息

- 仓库名：`personal-knowledge-base`
- 远程平台：gitee
- 默认分支：master
- 用户：solowalker-limber

## 引用本规则的入口

详见根目录 `AGENTS.md` / `CLAUDE.md` 中的"代码演示外置 workspace 模式"小节。
