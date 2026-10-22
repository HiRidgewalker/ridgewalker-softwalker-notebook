# sys.path 演示说明

本目录演示 **`sys.path` 的第一个路径与执行入口文件位置的关系**。

## 运行方式

```bash
# 在 sys_path_demo 目录下执行 demo1.py
cd workspace/python/modules/sys_path_demo
python demo1.py

# 在 sys_path_demo 目录下执行 subdir/demo2.py
python subdir/demo2.py

# 在 subdir 目录下执行 demo2.py（路径不同，结果不同）
cd subdir
python demo2.py
```

## 关键观察

- `sys.path` 的**第一个路径永远是入口文件的直接父目录**
- 同一个项目，不同入口文件，第一个路径会不同
- 这就是为什么"包名与模块名同名"会产生导入冲突：第一个路径下找到的同名 package 优先被解析