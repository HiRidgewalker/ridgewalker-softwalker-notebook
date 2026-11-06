---
sidebar_position: 7
---

---
title: "Go 常见问题笔记"
---

# Go 常见问题笔记

> 本篇按 **「问题 / 现象 / 解决 / 原理」** 四段模板收集 Go 实战中踩过的坑。后续遇到同类问题直接 append 到这里。
> 原稿 旧稿 整理后作为 Q1。

---

## Q1. `go build` / `go run` 突然变慢

### 问题

某次 `go build` / `go run` 编译时间突然从几秒变成几十秒，CPU 不忙但磁盘狂转。

### 现象

- 编译时间和项目规模不匹配
- 单文件 demo 也要几秒
- Windows 上更明显
- 任务管理器里 `go.exe` 占用不高，但磁盘 I/O 100%

### 解决

**首选：调低编译并发度**（经验值 `-p 1`）：

```bash
go build -p 1 ./...      # 一次只编译一个包
go run -p 1 main.go
```

**其他配套优化**：

| 做法 | 作用 |
| --- | --- |
| 把 Go 缓存目录加入杀毒白名单 | 避免每次写 `.a` 文件被扫 |
| `go build` + `./a.exe` 代替 `go run` | 避免 go run 每次重新编译 |
| 改用 SSD | 临时目录 `$TMP` 走 SSD |
| `go clean -cache` | 清掉失效缓存 |
| `go env GOCACHE` 改到大磁盘 | 避免缓存盘满 |

**效果实测**（GPT 整理，供参考）：

| 命令 | 编译时间 | CPU | 磁盘压力 |
| --- | --- | --- | --- |
| `go run -p 8 main.go` | 5.2s | 高 | 高 |
| `go run -p 1 main.go` | 2.1s | 低 | 低 |

### 原理

`go build` 默认按 `runtime.NumCPU()` 并发编译多个包（`GOMAXPROCS` 控制运行时，**`-p` 控制编译时**，两者独立）。多包并发会瞬间产生大量 `.a` 中间文件：

1. **Windows 杀毒软件**（Defender / 360 / 火绒）实时扫描每个新文件 → IO 爆炸
2. **机械硬盘** + 临时目录 `%TEMP%` 拥堵
3. **小项目**反而被并发调度开销拖累

`-p 1` 串行编译绕开这些问题，反而更快。

### 参考

- 知乎《Windows 下 Go 编译突然变慢？罪魁祸首竟是它！》<https://zhuanlan.zhihu.com/p/1937292903824224903>

---

## Q2.（占位）新问题追加示例

```markdown
## Q{N}. {问题标题}

### 问题
{一句话描述}

### 现象
- {关键表现 1}
- {关键表现 2}

### 解决
{命令 / 配置 / 代码改动}

### 原理
{为什么会这样}
```

> **使用说明**：
> - 遇到新问题 → 复制 Q2 模板 → 填四段 → 增到本文件末尾
> - 编号 Q3 / Q4 ... 顺延
> - 不需要的小节可以省略（如纯环境问题可省「原理」）
> - 关键命令 / 报错截图可用 `go build -p 1 ./...` 这种行内代码块

---

## 附录：定位编译慢原因的常用命令

```bash
# 看编译时间
time go build ./...

# 看缓存目录在哪 / 有多大
go env GOCACHE GOMODCACHE
du -sh $(go env GOCACHE)

# 看 CPU 核数
go env GOARCH
nproc                              # Linux
sysctl -n hw.ncpu                  # macOS

# 清缓存
go clean -cache                    # 清构建缓存
go clean -modcache                 # 清下载的模块缓存

# 看具体哪个包慢
go build -v -x ./... 2>&1 | tee build.log   # -x 打印所有执行的子命令
```
