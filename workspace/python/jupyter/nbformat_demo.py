"""以编程方式读写 .ipynb 文件（nbformat）

涵盖：
- 创建新 notebook（添加代码 cell、markdown cell）
- 保存为 .ipynb 文件
- 读取已存在的 notebook，遍历 cell 检查结构
- 校验 cell 类型 / 数量

依赖：pip install nbformat
运行：workspace/.venv/bin/python workspace/python/jupyter/nbformat_demo.py
"""

import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell


def build_notebook():
    """从零构建一个 notebook 并保存到磁盘"""
    print("=== 构建 notebook ===")
    nb = new_notebook()
    nb.cells.append(new_markdown_cell("# 演示 notebook\n\n自动生成"))
    nb.cells.append(new_code_cell("import sys\nprint(sys.version)"))
    nb.cells.append(new_code_cell("print('hello, jupyter')"))

    path = "workspace/python/jupyter/demo.ipynb"
    with open(path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    print(f"  已写入 {path}")
    return path


def inspect_notebook(path):
    """读取 notebook 并打印结构"""
    print("\n=== 读取并检查 notebook ===")
    with open(path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    print(f"  notebook 版本: nbformat v{nb.nbformat}")
    print(f"  cell 总数: {len(nb.cells)}")

    for i, cell in enumerate(nb.cells):
        head = cell.source.split("\n", 1)[0]
        if len(head) > 40:
            head = head[:40] + "..."
        print(f"  cell[{i}] {cell.cell_type}: {head}")

    # 统计 cell 类型
    counts = {}
    for cell in nb.cells:
        counts[cell.cell_type] = counts.get(cell.cell_type, 0) + 1
    print(f"  类型分布: {counts}")


def validate_notebook(path):
    """用 nbformat 校验 notebook 合法性"""
    print("\n=== 校验 notebook ===")
    with open(path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    nbformat.validate(nb)
    print(f"  {path} 校验通过")


def main():
    path = build_notebook()
    inspect_notebook(path)
    validate_notebook(path)


if __name__ == "__main__":
    main()