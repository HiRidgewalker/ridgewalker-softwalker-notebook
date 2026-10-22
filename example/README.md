# workspace

本目录存放知识库笔记中涉及的可运行演示代码。所有 demo 都可以独立运行，
对应说明见 `Hub/` 下的总览笔记，笔记中通过 git 远程链接引用。

## 目录结构

```
workspace/
├── python/
│   ├── basics/                 ← Python 基础演示
│   │   ├── data_types.py
│   │   ├── comprehensions.py
│   │   ├── iterators_generators.py
│   │   ├── match_case.py
│   │   ├── file_io.py
│   │   ├── namespaces_scope.py
│   │   └── oop_inherit.py
│   ├── class_methods/
│   │   └── instance_class_static.py
│   └── modules/
│       ├── sys_path_demo/      ← sys.path 与入口文件位置的关系
│       ├── import_vs_from.py
│       ├── dir_demo.py
│       ├── package_init/       ← 包导入与 __init__.py
│       └── name_collision/     ← 同名包冲突演示
└── (后续其他语言/技术模块的 demo 放这里)
```

## 运行约定

- 所有 demo 使用标准库或显式标注的第三方库
- 不依赖任何专有配置，开箱即用
- 每个 demo 顶部 docstring 说明其涵盖的知识点和运行方式