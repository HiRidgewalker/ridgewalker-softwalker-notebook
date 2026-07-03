# 三种挂载方式对比 Demo

对应：[[03_Docker数据卷与挂载笔记]] 的"三种挂载方式对比"和"易踩坑点"。

## 演示什么

- **bind mount**：本目录的 `./bind-data/` 目录挂到容器 → 写入文件后**主机立即可见**
- **named volume**：compose 创建的命名卷 → 用 `inspector` 容器（不重启 tester）即可读到
- **tmpfs**：内存级 → tester 容器退出 = 数据丢失

## 运行

```bash
cd 03_volume_demo

# 查看初始 bind 目录内容
ls -l bind-data/            # 应该有 before.txt

# 启动
docker compose up tester -d

# 等几秒让它写完三个挂载
sleep 5

# ① bind mount - 主机直接看
ls -l bind-data/
cat bind-data/hello.txt     # 容器内写的内容

# ② named volume - 用 inspector 服务查看（不依赖 tester）
docker compose up inspector -d
docker compose exec inspector sh
> ls -l /inspect-volume
> cat /inspect-volume/hello.txt
> exit
docker compose stop inspector

# ③ tmpfs - tester 容器已经存了数据在内存里，但容器退出就没了
docker compose stop tester
docker compose up tester  # 重新启动，新容器看不到 hello.txt
# （可以检查新容器 /in-tmpfs 是空的）

# 清理
docker compose down -v      # 包括 named volume 也删
```

## 期望结果

- **bind**：主机 `bind-data/hello.txt` 立即存在，是容器刚写入的内容
- **named volume**：删除 tester 容器后 `inspector` 仍能读到 hello.txt（验证持久化）
- **tmpfs**：tester 重启后空目录（验证"容器退出数据消失"）
