# 同名包冲突演示

## 项目结构

```
name_collision/
└── project/
    ├── other_module.py        # 同名的 func 函数
    └── module1/
        ├── __init__.py
        └── module1/            ← 子包与父包同名
            ├── __init__.py
            ├── module1.py      # func 函数定义在这里
            └── module2.py      # 在这里写 from module1.module1 import func
```

## 复现方法

```bash
cd workspace/python/modules/name_collision/project/module1/module1
python module2.py
```

## 现象

执行 `module2.py` 时，`sys.path` 第一个路径是 `module1/module1/` 目录本身，
而该目录下又存在一个名为 `module1` 的子目录，Python 解释器在按 `module1.module1`
路径解析时，可能错误地把同名子目录当作包，从而无法正确导入 `func`，抛错。

## 解决原则（个人经验）

- **避免同名冲突**：包名、模块名、子包名不要互相重复
- **使用绝对导入**：不要用相对路径
- **不要让包名和模块名重名**

详见 `Hub/Python基础.md` 中"包（package）"小节的总结。