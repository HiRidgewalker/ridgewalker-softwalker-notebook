## go基本命令
| 命令 | 用途 |
| --- | --- |
| go version |  查看当前 Go 的版本   |
| go env |  查看 Go 环境变量（包括 `GOPATH`、`GOROOT` 等）   |
| go help |  查看帮助，配合子命令使用，比如 `go help build` |


## go模块相关命令
| 命令 | 用途 |
| --- | --- |
| go mod init 模块名称 | 初始化模块创建一个mod文件 |
| go mod tidy | 清理无用的依赖并补全缺失依赖 |
| go mod download | 下载所有的依赖包 |
| go mod verify | 校验模块中缓存的包 |
| go mod graph | 打印模块依赖图 |
| go list -m all | 列出所有依赖的模块 |


## 项目管理与构建
| 命令 | 用途 |
| --- | --- |
| `go build` | 编译当前包或指定包 |
| `go run <文件.go>` | 编译并运行 Go 程序（通常用于调试） |
| `go install` | 编译并安装可执行文件到 `$GOPATH/bin` |
| `go clean` | 清理构建缓存和临时文件 |
| `go generate` | 根据代码中指令生成代码（如 `//go:generate`<br/>） |


## 🧪 测试与调试
| 命令 | 用途 |
| --- | --- |
| `go test` | 运行当前包下的测试代码（`*_test.go`<br/>） |
| `go test -v` | 输出详细测试日志 |
| `go test -cover` | 显示测试覆盖率 |
| `go benchmark` | 跑基准测试（在 `_test.go`<br/> 中使用 `Benchmark`<br/> 函数） |


## 🔍 代码分析和工具
| 命令 | 用途 |
| --- | --- |
| `go fmt` | 格式化代码（建议养成习惯） |
| `go vet` | 静态代码检查 |
| `go doc <包名>` | 查看包的文档（例如：`go doc fmt.Println`<br/>） |
| `go list` | 列出包信息 |
| `go get <模块路径>` | 添加或更新依赖包 |


# go module详解
go module 是Go语言从 1.11 版本之后官方推出的版本管理工具，并且从 Go1.13 版本开始，go module 成为了Go语言默认的依赖管理工具。

## 使用go module前需要设置环境变量
1. GO111MODULE=on
2. GOPROXY=https://goproxy.io,direct
3. GOPROXY=https://goproxy.cn,direct(国内的七牛云提供)

GO111MODULE 有三个值：off, on和auto（默认值）。

+ GO111MODULE=off，go命令行将不会支持module功能，寻找依赖包的方式将会沿用旧版本那种通过vendor目录或者GOPATH模式来查找。
+ GO111MODULE=on，go命令行会使用modules，而一点也不会去GOPATH目录下查找。
+ GO111MODULE=auto，默认值，go命令行将会根据当前目录来决定是否启用module功能。这种情况下可以分为两种情形：
    - 当前目录在GOPATH之外且该目录包含go.mod文件 开启
    - 当处于 GOPATH 内且没有 go.mod 文件存在时其行为会等同于 GO111MODULE=off
+ 如果不使用 Go Modules, go get 将会从模块代码的 master 分支拉取
+ 而若使用 Go Modules 则你可以利用 Git Tag 手动选择一个特定版本的模块代码

## go mod 有以下命令
| 命令 | 说明 |
| --- | --- |
| download | download modules to local cache(下载依赖包) |
| edit | edit go.mod from tools or scripts（编辑go.mod) |
| graph | print module requirement graph (打印模块依赖图) |
| init | initialize new module in current directory（在当前目录初始化mod） |
| tidy | add missing and remove unused modules(拉取缺少的模块，移除不用的模块) |
| vendor | make vendored copy of dependencies(将依赖复制到vendor下) |
| verify | verify dependencies have expected content (验证依赖是否正确） |
| why | explain why packages or modules are needed(解释为什么需要依赖) |


+ 常用的有 `init tdiy edit`

使用go get命令下载指定版本的依赖包：

执行`go get `命令，在下载依赖包的同时还可以指定依赖包的版本。

+ 运行`go get -u`命令会将项目中的包升级到最新的次要版本或者修订版本；
+ 运行`go get -u=patch`命令会将项目中的包升级到最新的修订版本；
+ 运行`go get [包名]@[版本号]`命令会下载对应包的指定版本或者将对应包升级到指定的版本。

> 提示：`go get [包名]@[版本号]`命令中版本号可以是 x.y.z 的形式，例如 go get foo@v1.2.3，也可以是 git 上的分支或 tag，例如 go get foo@master，还可以是 git 提交时的哈希值，例如 go get foo@e3702bed2。
>

## 项目中使用
1. 在 GOPATH 目录下新建一个目录，并使用`go mod init`初始化生成 go.mod 文件。go.mod 文件一旦创建后，它的内容将会被 go toolchain 全面掌控，go toolchain 会在各类命令执行时，比如`go get`、`go build`、`go mod`等修改和维护 go.mod 文件。go.mod 提供了 module、require、replace 和 exclude 四个命令：

初始化生成的 go.mod 文件如下所示：

```go
module hello

go 1.13
```

    - module 语句指定包的名字（路径）；
    - require 语句指定的依赖项模块；
    - replace 语句可以替换依赖项模块；
    - exclude 语句可以忽略依赖项模块。
2. 添加依赖。新建一个 main.go 文件，写入以下代码：

```go
package main
import (
    "net/http"
    "github.com/labstack/echo"
)
func main() {
    e := echo.New()
    e.GET("/", func(c echo.Context) error {
        return c.String(http.StatusOK, "Hello, World!")
    })
    e.Logger.Fatal(e.Start(":1323"))
}
```

执行`go mod tidy`运行代码会发现 go mod 会自动查找依赖自动下载

```go
go: finding module for package github.com/labstack/echo
go: found github.com/labstack/echo in github.com/labstack/echo v3.3.10+incompatible
go: finding module for package github.com/stretchr/testify/assert
go: finding module for package github.com/labstack/gommon/log
go: finding module for package github.com/labstack/gommon/color
go: finding module for package golang.org/x/crypto/acme/autocert
go: found github.com/labstack/gommon/color in github.com/labstack/gommon v0.3.1
go: found github.com/labstack/gommon/log in github.com/labstack/gommon v0.3.1
go: found golang.org/x/crypto/acme/autocert in golang.org/x/crypto v0.0.0-20220112180741-5e0467b6c7ce
go: found github.com/stretchr/testify/assert in github.com/stretchr/testify v1.7.0

```

go.mod中的内容：

```go
module learning09

go 1.17

require github.com/labstack/echo v3.3.10+incompatible

require (
    github.com/labstack/gommon v0.3.1 // indirect
    github.com/mattn/go-colorable v0.1.11 // indirect
    github.com/mattn/go-isatty v0.0.14 // indirect
    github.com/valyala/bytebufferpool v1.0.0 // indirect
    github.com/valyala/fasttemplate v1.2.1 // indirect
    golang.org/x/crypto v0.0.0-20220112180741-5e0467b6c7ce // indirect
    golang.org/x/net v0.0.0-20211112202133-69e39bad7dc2 // indirect
    golang.org/x/sys v0.0.0-20211103235746-7861aae1554b // indirect
    golang.org/x/text v0.3.6 // indirect
)

```

go module 安装 package 的原则是先拉取最新的 release tag，若无 tag 则拉取最新的 commitgo 会自动生成一个 go.sum 文件来记录 dependency tree。执行脚本`go run main.go`，就可以运行项目。可以使用命令`go list -m -u all`来检查可以升级的 package，使用`go get -u need-upgrade-package`升级后会将新的依赖版本更新到 go.mod ，比如：`go get -u github.com/labstack/gommon`也可以使用`go get -u`升级所有依赖。

3. 一般使用包之前，是首先执行`go get`命令，先下载依赖。比如 `github.com/labstack/echo`

使用 replace 替换无法直接获取的 package：

由于某些已知的原因，并不是所有的 package 都能成功下载，比如：golang.org 下的包。

modules 可以通过在 go.mod 文件中使用 replace 指令替换成 github 上对应的库，比如：

```go
replace (
    golang.org/x/crypto v0.0.0-20190313024323-a1f597ede03a => github.com/golang/crypto v0.0.0-20190313024323-a1f597ede03a
)
```

或者

```go
replace golang.org/x/crypto v0.0.0-20190313024323-a1f597ede03a => github.com/golang/crypto v0.0.0-20190313024323-a1f597ede03a
```

> `go install`命令将项目打包安装为可执行文件，在安装在GOPATH的bin目录下，go install执行的项目 必须有main方法
>



## 常规问题：go mod init <项目名称> 的项目名应该如何定义
这是个非常好的问题！`go mod init` 后面跟的“模块名”不是包名、也不一定是项目文件夹名，而是 **整个项目的模块路径**，**通常是你将来代码仓库的地址（比如 GitHub、GitLab 等）**。

---

### ✅ 官方推荐的模块名写法（正规写法）
```plain
go mod init github.com/你的用户名/项目名
```

✅ 为什么这么写？

因为：

1. 将来你项目的依赖者会通过这个地址来 `go get` 你的模块；
2. 这样 Go 能识别并从该 URL 下载模块源码（比如从 GitHub 下载）；
3. 避免多个项目模块名重复的问题。

---

### 📦 举例说明
假设你有一个项目，代码将来放在 GitHub：

```go
mkdir my-awesome-api
cd my-awesome-api
go mod init github.com/yudonghe/my-awesome-api
```

这时 `go.mod` 里是这样的：

```go
module github.com/yudonghe/my-awesome-api

go 1.21
```

你的代码结构可能是这样：

```go
my-awesome-api/
├── go.mod
├── go.sum
├── main.go
└── internal/
└── handlers/
```

---

### ❓如果不是托管在 GitHub 怎么办？
+ 放在 GitLab：`gitlab.com/username/project`
+ 放在 Gitee：中国开发者也可以写：`gitee.com/用户名/项目名`
+ 如果不打算开源/托管，写一个符合规范的模块名也可以（Go 不会强制验证你模块名必须可访问）

```go
go mod init example.com/internal/myproject
```

但注意：如果你将来要分享、部署或让别人通过 `go get` 使用你模块，模块名必须是可访问的 URL。

---

### ❗️常见错误用法（不推荐）
```plain
go mod init myproject      # ❌ 模块名太短，容易与别人冲突
go mod init main           # ❌ 无意义，也不利于依赖管理
go mod init .              # ❌ 当前目录名不是标准路径
```

---

### ✅ 总结：如何取模块名
| 情况 | 推荐写法 |
| --- | --- |
| 项目会开源或放在远程仓库 | `go mod init github.com/你的用户名/项目名` |
| 私有项目但有内部规范 | `go mod init git.mycompany.com/team/project` |
| 临时学习项目或不打算分享 | 可以简写，但建议规范，比如 `example.com/test/project` |


# go多版本管理工具 `g`
